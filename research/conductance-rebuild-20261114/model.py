"""Two compartments, continuous Na/K HH spikes (no threshold/reset), Ca/SK,
NaP, soma/axon coupling; delayed biexponential conductance synapses.
Units ms,mV,pF,nS,pA,uM. Reduced geometry is a declared prior, NOT traced EM.
All cells share a numerical channel family; adult type-specific ionic densities
remain unmeasured. Adult MN Rin targets constrain leak, not all physiology.
"""
from pathlib import Path
import json
import numpy as np
from numba import njit
ROOT=Path(__file__).parent
DEFAULT=dict(dt_ms=.025,duration_ms=1800.,onset_ms=200.,drive_pA=160.,ge_nS_per_synapse=.012,gi_nS_per_synapse=.025,
 tau_e_rise_ms=.5,tau_e_decay_ms=5.,tau_i_rise_ms=1.,tau_i_decay_ms=25.,delay_ms=1.5,
 c_soma_pF=20.,c_axon_pF=2.5,rin_cpg_MOhm=500.,rin_mn_MOhm=300.,coupling_nS=12.,
 gNa_nS=600.,gK_nS=180.,gCa_nS=.3,gSK_nS=1.,gNaP_nS=0.,ca_tau_ms=100.,ca_alpha=.0002,ca_Kd_uM=.2,
 E_leak_mV=-65.,E_Na_mV=55.,E_K_mV=-80.,E_Ca_mV=120.,E_exc_mV=0.,E_inh_mV=-80.,
 gate_speed=1.,leak_scale=1.,axon_bias_pA=0.,inhibitory_gain=1.,I1_gain=1.,I2_gain=1.,I2_leak_shift_mV=0.,mn_gain=1.,background_exc_gain=1.,mn_SK_scale=1.,mn_leak_mV=-65.,
 synaptic_delay_scope='one global delay prior, not measured per edge',adult_scope='Rin=300MOhm is unknown-type adult MN prior; fast/intermediate/slow exemplars tested separately')

@njit(cache=True)
def vtrap(x):
 if abs(x)<1e-7:return 10.+x*.5
 return x/(1.-np.exp(-x/10.))

@njit(cache=True)
def gates(v):
 am=.1*vtrap(v+40.);bm=4.*np.exp(-(v+65.)/18.);ah=.07*np.exp(-(v+65.)/20.);bh=1./(1.+np.exp(-(v+35.)/10.));an=.01*vtrap(v+55.);bn=.125*np.exp(-(v+65.)/80.)
 return am,bm,ah,bh,an,bn

@njit(cache=True)
def _kernel(N,pre,post,ew,roles,drive,ablated,dt,steps,onset,delay,pars,cell,record_stride):
 vs=np.empty(N);va=np.empty(N);mh=np.empty(N);hh=np.empty(N);nh=np.empty(N);ca=np.zeros(N)
 for j in range(N):
  vs[j]=cell[j,4];va[j]=vs[j];am,bm,ah,bh,an,bn=gates(va[j]);mh[j]=am/(am+bm);hh[j]=ah/(ah+bh);nh[j]=an/(an+bn)
 xe=np.zeros(N);ye=np.zeros(N);xi=np.zeros(N);yi=np.zeros(N)
 delaybuf=np.zeros((delay+1,N),np.uint8);counts=np.zeros((int(np.ceil(steps*dt)),N),np.int16);voltage=np.zeros((steps//record_stride+1,min(N,12),2));bad=0
 ter,ted,tir,tid,ge,gi,gna,gk,gca,gsk,gnap,tc,alpha,kd,ena,ek,eca,ee,ei,speed,axon_bias=pars
 # Normalize each dual exponential so one event peaks at its nS weight.
 tpe=np.log(ted/ter)/(1./ter-1./ted);norme=1./(np.exp(-tpe/ted)-np.exp(-tpe/ter));tpi=np.log(tid/tir)/(1./tir-1./tid);normi=1./(np.exp(-tpi/tid)-np.exp(-tpi/tir))
 de1=np.exp(-dt/ter);de2=np.exp(-dt/ted);di1=np.exp(-dt/tir);di2=np.exp(-dt/tid)
 for k in range(steps):
  xe*=de1;ye*=de2;xi*=di1;yi*=di2
  arrivals=delaybuf[k%(delay+1)]
  for e in range(len(pre)):
   i=pre[e];j=post[e]
   if arrivals[i] and not ablated[i] and not ablated[j]:
    w=ew[e]
    if w>0:
     inc=w*ge*cell[j,5]*norme;xe[j]+=inc;ye[j]+=inc
    else:
     inc=-w*gi*cell[i,6]*normi;xi[j]+=inc;yi[j]+=inc
  arrivals[:]=0
  for j in range(N):
   if ablated[j]:vs[j]=cell[j,4];va[j]=cell[j,4];continue
   v=va[j]
   if not np.isfinite(v) or v< -160 or v>120:bad=1;break
   am,bm,ah,bh,an,bn=gates(v)
   mh[j]=am/(am+bm)+(mh[j]-am/(am+bm))*np.exp(-dt*(am+bm)*speed)
   hh[j]=ah/(ah+bh)+(hh[j]-ah/(ah+bh))*np.exp(-dt*(ah+bh)*speed)
   nh[j]=an/(an+bn)+(nh[j]-an/(an+bn))*np.exp(-dt*(an+bn)*speed)
   gNa=gna*mh[j]**3*hh[j];gK=gk*nh[j]**4
   # Instantaneous Ca activation and explicit intracellular concentration;
   # no imposed oscillatory current, phase clock or spike-triggered reset.
   cainf=1./(1.+np.exp(-(v+25.)/6.));gCa=gca*cainf*cainf;gSK=gsk*cell[j,8]*ca[j]/(ca[j]+kd);gNaP=gnap/(1.+np.exp(-(vs[j]+50.)/5.))
   Cs,Ca,gLs,gLa,EL,gain,igain,gc=cell[j,:8]
   excit=ye[j]-xe[j];inhib=yi[j]-xi[j]
   A=Cs/dt+gLs+gc+excit+inhib+gNaP
   B=Ca/dt+gLa+gc+gNa+gK+gCa+gSK
   inj=drive[j] if k*dt>=onset else 0.
   rhs1=Cs/dt*vs[j]+gLs*EL+excit*ee+inhib*ei+gNaP*ena+inj
   rhs2=Ca/dt*v+gLa*(-54.4)+gNa*ena+(gK+gSK)*ek+gCa*eca+axon_bias
   den=A*B-gc*gc;newvs=(rhs1*B+gc*rhs2)/den;newva=(rhs2*A+gc*rhs1)/den
   vs[j]=newvs;va[j]=newva;ca[j]=max(0.,ca[j]+dt*(-alpha*gCa*(newva-eca)-ca[j]/tc))
   if v<0. and newva>=0.:
    counts[min(int(k*dt),counts.shape[0]-1),j]+=1;delaybuf[(k+delay)%(delay+1),j]=1
  if bad:break
  if k%record_stride==0:
   voltage[k//record_stride,:,0]=vs[:min(N,12)];voltage[k//record_stride,:,1]=va[:min(N,12)]
 return counts,voltage,vs,va,ca,bad

def simulate(weights,roles,config=None,drive=None,ablate=()):
 p=DEFAULT.copy();p.update(config or {});W=np.asarray(weights);N=len(W);roles=list(roles);pre,post=np.nonzero(W);ew=W[pre,post].astype(float)
 cell=np.empty((N,9))
 for j,r in enumerate(roles):
  ismn=r=='MN';rin=p['rin_mn_MOhm'] if ismn else p['rin_cpg_MOhm'];gt=1000./rin;gLa=gt*.15;gc=p['coupling_nS'];gLs=gt-gc*gLa/(gc+gLa)
  cell[j]=[p['c_soma_pF']*(2. if ismn else 1.),p['c_axon_pF'],gLs*p['leak_scale'],gLa*p['leak_scale'],p['mn_leak_mV'] if ismn else p['E_leak_mV'],p['mn_gain'] if ismn else (p['background_exc_gain'] if r=='other' else 1.),p['I2_gain'] if r=='I2' else (p['I1_gain'] if r=='I1' else p['inhibitory_gain']),gc,p['mn_SK_scale'] if ismn else 1.]
  if r=='I2':cell[j,4]+=p['I2_leak_shift_mV']
 if drive is None:drive=np.array([p['drive_pA'] if r=='DN' else 0. for r in roles])
 names=['tau_e_rise_ms','tau_e_decay_ms','tau_i_rise_ms','tau_i_decay_ms','ge_nS_per_synapse','gi_nS_per_synapse','gNa_nS','gK_nS','gCa_nS','gSK_nS','gNaP_nS','ca_tau_ms','ca_alpha','ca_Kd_uM','E_Na_mV','E_K_mV','E_Ca_mV','E_exc_mV','E_inh_mV','gate_speed','axon_bias_pA']
 dt=p['dt_ms'];steps=round(p['duration_ms']/dt);mask=np.array([j in ablate for j in range(N)],dtype=np.bool_);stride=max(1,round(.5/dt))
 out=_kernel(N,pre.astype(np.int32),post.astype(np.int32),ew, np.zeros(N),np.asarray(drive,dtype=float),mask,dt,steps,p['onset_ms'],max(1,round(p['delay_ms']/dt)),np.array([p[x] for x in names]),cell,stride)
 return {'spike_counts_1ms':out[0],'voltage_first12':out[1],'final_vs':out[2],'final_va':out[3],'calcium_uM':out[4],'numerical_failure':bool(out[5]),'config':p,'roles':roles,'cell_parameters':cell,'record_interval_ms':stride*dt}
