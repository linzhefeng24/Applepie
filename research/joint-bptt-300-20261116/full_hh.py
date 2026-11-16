"""Full3988-cell HH BPTT: sparse actual graph, no replayed outer-cell spikes.
Same hard-spike forward and channel equations as the original detailed model;
shared207 variables on their annotated types, with surrogate spike derivatives.
200ms truncated reverse state gradients retain continuous forward state.
"""
from pathlib import Path
import json,sys
import numpy as np
from scipy import sparse
import jax
jax.config.update('jax_enable_x64',True)
import jax.numpy as j
from jax import lax
from jax.experimental.sparse import CSR
R=Path(__file__).resolve().parent;ROOT=R.parents[1]
sys.path.insert(0,str(ROOT/'research/single-model-delivery-20261115/runtime/02_code'))
sys.path.insert(0,str(ROOT/'research/conductance-rebuild-20261114'))
from flymodel import Model
from grouped_parameters import group_key

def csr(value):
 value=value.tocsr();value.sort_indices()
 return CSR((j.asarray(value.data),j.asarray(value.indices),j.asarray(value.indptr)),shape=value.shape)

def linear_sparse_operator(matrix):
 """Exact linear VJP even when the sparse zero-input forward is skipped."""
 transpose=matrix.T
 @jax.custom_vjp
 def apply(x):return lax.cond(j.any(x!=0),lambda value:matrix@value,lambda value:j.zeros(matrix.shape[0],dtype=value.dtype),x)
 def fwd(x):return apply(x),None
 def bwd(res,g):return (lax.cond(j.any(g!=0),lambda value:transpose@value,lambda value:j.zeros(matrix.shape[1],dtype=value.dtype),g),)
 apply.defvjp(fwd,bwd)
 return apply

class FullDifferentiableHH:
 def __init__(self):
  self.cfg=json.loads((R/'neural-config.json').read_text());c=self.cfg;self.model=Model(ROOT/c['baseline_model']);m=self.model;n=m.config['neural'];self.dt=n['solver']['dt_ms'];self.delay=max(1,round(n['solver']['delay_ms']/self.dt));self.substeps=round(n['solver']['spike_bin_ms']/self.dt)
  identity=json.loads((ROOT/'research/surrogate-bptt-20261115/input-identity.json').read_text());self.groups=identity['groups'];group_ids={key:i for i,key in enumerate(self.groups)}
  self.assignment=j.asarray(np.array([group_ids.get(group_key(row),-1) if row['type'] not in c['frozen_types'] else -1 for row in m.neurons],dtype=np.int32));self.n_groups=len(self.groups)
  self.base=j.asarray(m.cells);self.fields=j.asarray(c['train_fields']);self.kinetics=j.asarray(m.kinetics);self.aux=j.asarray(m.aux);self.p=j.asarray(m.global_values)
  N=len(m.ids);positive=m.weight>0;self.We=csr(sparse.coo_matrix((m.weight[positive],(m.post[positive],m.pre[positive])),shape=(N,N)));self.Wi=csr(sparse.coo_matrix((-m.weight[~positive],(m.post[~positive],m.pre[~positive])),shape=(N,N)))
  self.exc_operator=linear_sparse_operator(self.We);self.inh_operator=linear_sparse_operator(self.Wi)
  self.eidx=j.arange(N);self.iidx=j.arange(N);self.data={'local':np.arange(N)}
  row=[];col=[];value=[]
  for k,pool in enumerate(m.mapping):
   for i in pool['MN_indices']:row.append(k);col.append(i);value.append(1/len(pool['MN_indices']))
  self.readout=csr(sparse.coo_matrix((value,(row,col)),shape=(len(m.mapping),N)))
  self.dn=j.asarray(np.array([x['type']=='DNg100' for x in m.neurons]));self.on=c['target_start_ms'];self.off=m.config['experiments'][c['experiment']]['events'][0]['off_ms'];self.drive=m.config['experiments'][c['experiment']]['events'][0]['current_pA'];self.duration=1400
  nm=m.config['neuromuscular'];self.filter_decay=np.exp(-n['solver']['spike_bin_ms']/nm['filter_tau_ms']);self.rate_scale=nm['rate_scale_Hz'];self.bin_rate=1000/n['solver']['spike_bin_ms']
  width=c['surrogate_width_mV'];threshold=float(m.aux[7])
  @jax.custom_vjp
  def spike(old,new):return ((old<threshold)&(new>=threshold)).astype(j.float64)
  def sf(old,new):return spike(old,new),(old,new)
  def sb(res,g):
   old,new=res;slope=width/(width+j.abs(new-threshold))**2;gate=((old<threshold)&(new>old)).astype(j.float64)
   return j.zeros_like(old),g*slope*gate
  spike.defvjp(sf,sb);self.spike=spike
  @jax.custom_vjp
  def state_clip(x):return x
  def cf(x):return x,None
  def cb(res,g):return (j.clip(g,-c.get('backward_state_clip',10.),c.get('backward_state_clip',10.)),)
  state_clip.defvjp(cf,cb);self.state_clip=state_clip

 def parameters(self,raw):
  delta=self.cfg['relative_bound']*j.tanh(raw)
  factors=delta[j.maximum(self.assignment,0)]*(self.assignment>=0)[:,None]
  return self.base.at[:,self.fields].set(self.base[:,self.fields]*(1+factors)),delta

 def gates(self,v):
  k=self.kinetics
  def trap(x):
   small=j.abs(x)<k[16];safe=j.where(small,k[16],x)
   return j.where(small,k[2]+x/2,safe/(-j.expm1(-safe/k[2])))
  return k[0]*trap(v+k[1]),k[3]*j.exp(-(v+k[4])/k[5]),k[6]*j.exp(-(v+k[7])/k[8]),1/(1+j.exp(-(v+k[9])/k[10])),k[11]*trap(v+k[12]),k[13]*j.exp(-(v+k[14])/k[15])

 def forward(self,raw,end_ms=None):
  cell,_=self.parameters(raw);dt=self.dt;aux=self.aux
  ter,ted,tir,tid,ge,gi,gsk,alpha,kd,ena,ek,eca,ee,ei=self.p
  tpe=j.log(ted/ter)/(1/ter-1/ted);norme=1/(j.exp(-tpe/ted)-j.exp(-tpe/ter))
  tpi=j.log(tid/tir)/(1/tir-1/tid);normi=1/(j.exp(-tpi/tid)-j.exp(-tpi/tir))
  de1=j.exp(-dt/ter);de2=j.exp(-dt/ted);di1=j.exp(-dt/tir);di2=j.exp(-dt/tid)
  N=len(self.data['local']);v=cell[:,4];am,bm,ah,bh,an,bn=self.gates(v);zero=j.zeros(N)
  # State: Vs,Va,m,h,n,Ca,xe,ye,xi,yi, delayed spikes, filtered MN rate.
  init=(v,v,am/(am+bm),ah/(ah+bh),an/(an+bn),zero,zero,zero,zero,zero,j.zeros((self.delay+1,N)),j.zeros(len(self.model.mapping)))
  def ms_step(state,inputs):
   ms=inputs
   inj=self.dn*j.where((ms>=self.on)&(ms<self.off),self.drive,0.)
   def micro(carry,inp):
    st,bin_counts=carry;k0=inp;ex=j.zeros(N);inh=j.zeros(N)
    vs,va,m,h,n,ca,xe,ye,xi,yi,hist,filt=st;k=ms*self.substeps+k0
    arriving=hist[k%(self.delay+1)]
    inc_e=ge*norme*cell[:,5]*(ex+self.exc_operator(arriving[self.eidx]*cell[self.eidx,12]))
    inc_i=gi*normi*(inh+self.inh_operator(arriving[self.iidx]*cell[self.iidx,6]*cell[self.iidx,12]))
    xe=xe*de1+inc_e;ye=ye*de2+inc_e;xi=xi*di1+inc_i;yi=yi*di2+inc_i
    am,bm,ah,bh,an,bn=self.gates(va)
    m=am/(am+bm)+(m-am/(am+bm))*j.exp(-dt*(am+bm)*cell[:,11])
    h=ah/(ah+bh)+(h-ah/(ah+bh))*j.exp(-dt*(ah+bh)*cell[:,11])
    n=an/(an+bn)+(n-an/(an+bn))*j.exp(-dt*(an+bn)*cell[:,11])
    gNa=cell[:,13]*m**3*h;gK=cell[:,14]*n**4;cainf=jax.nn.sigmoid((va+25.)/6.);gCa=cell[:,15]*cainf**2;gSK=gsk*cell[:,8]*ca/(ca+kd);gNaP=cell[:,9]*jax.nn.sigmoid((vs-aux[5])/aux[6])
    Cs=cell[:,0];Ca=cell[:,1];gLs=cell[:,2];gLa=cell[:,3];gc=cell[:,7];excit=ye-xe;inhib=yi-xi
    A=Cs/dt+gLs+gc+excit+inhib+gNaP;B=Ca/dt+gLa+gc+gNa+gK+gCa+gSK
    r1=Cs/dt*vs+gLs*cell[:,4]+excit*ee+inhib*ei+gNaP*ena+inj
    r2=Ca/dt*va+gLa*aux[0]+gNa*ena+(gK+gSK)*ek+gCa*eca+cell[:,10]
    den=A*B-gc*gc;newvs=(r1*B+gc*r2)/den;newva=(r2*A+gc*r1)/den
    ca=j.maximum(0.,ca+dt*(-alpha*gCa*(newva-eca)-ca/cell[:,16]))
    spikes=self.spike(va,newva)
    valid=j.all(j.isfinite(newvs)&j.isfinite(newva)&(newvs>=aux[1])&(newvs<=aux[2])&(newva>=aux[1])&(newva<=aux[2]))
    spikes=j.where(valid,spikes,j.nan)
    hist=hist.at[k%(self.delay+1)].set(0.).at[(k+self.delay)%(self.delay+1)].set(spikes)
    return ((newvs,newva,m,h,n,ca,xe,ye,xi,yi,hist,filt),bin_counts+spikes),None
   (st,counts),_=lax.scan(micro,(state,j.zeros(N)),j.arange(self.substeps))
   filt=self.filter_decay*st[-1]+(1-self.filter_decay)*(self.readout@counts)*self.bin_rate
   st=(*st[:-1],filt)
   if self.cfg.get('bptt_truncate_ms'):
    boundary=((ms+1)%round(self.cfg['bptt_truncate_ms']))==0
    st=jax.tree_util.tree_map(lambda x:j.where(boundary,lax.stop_gradient(x),x),st)
   if self.cfg.get('backward_state_clip'):st=jax.tree_util.tree_map(self.state_clip,st)
   value=filt/self.rate_scale;clipped=j.clip(value,0.,1.)
   if self.cfg.get('surrogate_readout_clip'):clipped=value+lax.stop_gradient(clipped-value)
   return st,(clipped,counts)
  # Rematerialize each 1ms block during reverse mode, retaining full temporal gradients.
  T=self.duration if end_ms is None else int(end_ms)
  _,out=lax.scan(jax.checkpoint(ms_step),init,j.arange(T))
  return out
