"""Continuous two-compartment HH/Ca/SK equations.
All physiological coefficients, cell arrays, delays and numerical guards are
provided by the single model.yaml. Literal indices, zeros, ones and HH channel
powers below are equation structure, not a second set of model parameters.
No reset, periodic forcing or generated target waveform is used.
"""
import numpy as np
from numba import njit

@njit(cache=True)
def vtrap(x,width,epsilon):
 if abs(x)<epsilon:return width+x/2
 return x/(1-np.exp(-x/width))

@njit(cache=True)
def gates(v,k):
 am=k[0]*vtrap(v+k[1],k[2],k[16]);bm=k[3]*np.exp(-(v+k[4])/k[5]);ah=k[6]*np.exp(-(v+k[7])/k[8]);bh=1/(1+np.exp(-(v+k[9])/k[10]));an=k[11]*vtrap(v+k[12],k[2],k[16]);bn=k[13]*np.exp(-(v+k[14])/k[15])
 return am,bm,ah,bh,an,bn

@njit(cache=True)
def _kernel(N,pre,post,ew,roles,drive,ablated,dt,steps,onset,delay,pars,cell,record_stride,waveform,waveform_dt,record_indices,row_offsets,kinetics,aux):
 vs=np.empty(N);va=np.empty(N);mh=np.empty(N);hh=np.empty(N);nh=np.empty(N);ca=np.zeros(N)
 for j in range(N):
  vs[j]=cell[j,4];va[j]=vs[j];am,bm,ah,bh,an,bn=gates(va[j],kinetics);mh[j]=am/(am+bm);hh[j]=ah/(ah+bh);nh[j]=an/(an+bn)
 xe=np.zeros(N);ye=np.zeros(N);xi=np.zeros(N);yi=np.zeros(N)
 delaybuf=np.zeros((delay+1,N),np.uint8);counts=np.zeros((int(np.ceil(steps*dt/aux[8])),N),np.int16);voltage=np.zeros((steps//record_stride+1,len(record_indices),2));ca_trace=np.zeros((steps//record_stride+1,len(record_indices)));currents=np.zeros((steps//record_stride+1,len(record_indices),4));conductances=np.zeros((steps//record_stride+1,len(record_indices),2));gating=np.zeros((steps//record_stride+1,len(record_indices),3));bad=0
 ter,ted,tir,tid,ge,gi,gsk,alpha,kd,ena,ek,eca,ee,ei=pars
 # Normalize each dual exponential so one event peaks at its nS weight.
 tpe=np.log(ted/ter)/(1./ter-1./ted);norme=1./(np.exp(-tpe/ted)-np.exp(-tpe/ter));tpi=np.log(tid/tir)/(1./tir-1./tid);normi=1./(np.exp(-tpi/tid)-np.exp(-tpi/tir))
 de1=np.exp(-dt/ter);de2=np.exp(-dt/ted);di1=np.exp(-dt/tir);di2=np.exp(-dt/tid)
 for k in range(steps):
  xe*=de1;ye*=de2;xi*=di1;yi*=di2
  arrivals=delaybuf[k%(delay+1)]
  # Row-major event traversal preserves the original addition order exactly.
  # Inactive presynaptic rows have no events, so need not scan every edge.
  for i in range(N):
   if not arrivals[i] or ablated[i]:continue
   for e in range(row_offsets[i],row_offsets[i+1]):
    j=post[e]
    if ablated[j]:continue
    w=ew[e]
    if w>0:
     inc=w*ge*cell[j,5]*cell[i,12]*norme;xe[j]+=inc;ye[j]+=inc
    else:
     inc=-w*gi*cell[i,6]*cell[i,12]*normi;xi[j]+=inc;yi[j]+=inc
  arrivals[:]=0
  for j in range(N):
   if ablated[j]:vs[j]=cell[j,4];va[j]=cell[j,4];continue
   v=va[j]
   if not np.isfinite(v) or v<aux[1] or v>aux[2]:bad=1;break
   am,bm,ah,bh,an,bn=gates(v,kinetics)
   mh[j]=am/(am+bm)+(mh[j]-am/(am+bm))*np.exp(-dt*(am+bm)*cell[j,11])
   hh[j]=ah/(ah+bh)+(hh[j]-ah/(ah+bh))*np.exp(-dt*(ah+bh)*cell[j,11])
   nh[j]=an/(an+bn)+(nh[j]-an/(an+bn))*np.exp(-dt*(an+bn)*cell[j,11])
   gNa=cell[j,13]*mh[j]**3*hh[j];gK=cell[j,14]*nh[j]**4
   # Instantaneous Ca activation and explicit intracellular concentration;
   # no imposed oscillatory current, phase clock or spike-triggered reset.
   cainf=1./(1.+np.exp(-(v+25.)/6.));gCa=cell[j,15]*cainf*cainf;gSK=gsk*cell[j,8]*ca[j]/(ca[j]+kd);gNaP=cell[j,9]/(1.+np.exp(-(vs[j]-aux[5])/aux[6]))
   Cs,Ca,gLs,gLa,EL,gain,igain,gc=cell[j,:8]
   excit=ye[j]-xe[j];inhib=yi[j]-xi[j]
   A=Cs/dt+gLs+gc+excit+inhib+gNaP
   B=Ca/dt+gLa+gc+gNa+gK+gCa+gSK
   inj=drive[j] if k*dt>=onset else 0.
   if len(waveform):inj=waveform[min(int(k*dt/waveform_dt),len(waveform)-1),j]
   rhs1=Cs/dt*vs[j]+gLs*EL+excit*ee+inhib*ei+gNaP*ena+inj
   rhs2=Ca/dt*v+gLa*aux[0]+gNa*ena+(gK+gSK)*ek+gCa*eca+cell[j,10]
   den=A*B-gc*gc;newvs=(rhs1*B+gc*rhs2)/den;newva=(rhs2*A+gc*rhs1)/den
   vs[j]=newvs;va[j]=newva;ca[j]=max(0.,ca[j]+dt*(-alpha*gCa*(newva-eca)-ca[j]/cell[j,16]))
   if v<aux[7] and newva>=aux[7]:
    counts[min(int(k*dt/aux[8]),counts.shape[0]-1),j]+=1;delaybuf[(k+delay)%(delay+1),j]=1
  if bad:break
  if k%record_stride==0:
   voltage[k//record_stride,:,0]=vs[record_indices];voltage[k//record_stride,:,1]=va[record_indices];ca_trace[k//record_stride]=ca[record_indices]
   gating[k//record_stride,:,0]=mh[record_indices];gating[k//record_stride,:,1]=hh[record_indices];gating[k//record_stride,:,2]=nh[record_indices]
   for jj in range(len(record_indices)):
    j=record_indices[jj];rec=k//record_stride;gej=ye[j]-xe[j];gij=yi[j]-xi[j];inj=drive[j] if k*dt>=onset else 0.
    if len(waveform):inj=waveform[min(int(k*dt/waveform_dt),len(waveform)-1),j]
    currents[rec,jj,0]=gej*(ee-vs[j]);currents[rec,jj,1]=gij*(ei-vs[j]);currents[rec,jj,2]=cell[j,7]*(va[j]-vs[j]);currents[rec,jj,3]=inj;conductances[rec,jj,0]=gej;conductances[rec,jj,1]=gij
 finalg=np.empty((N,2));finali=np.empty((N,4));finalgate=np.empty((N,3))
 for j in range(N):
  finalg[j,0]=ye[j]-xe[j];finalg[j,1]=yi[j]-xi[j];finali[j,0]=finalg[j,0]*(ee-vs[j]);finali[j,1]=finalg[j,1]*(ei-vs[j]);finali[j,2]=cell[j,7]*(va[j]-vs[j]);finali[j,3]=waveform[min(int((steps-1)*dt/waveform_dt),len(waveform)-1),j] if len(waveform) else drive[j];finalgate[j,0]=mh[j];finalgate[j,1]=hh[j];finalgate[j,2]=nh[j]
 return counts,voltage,vs,va,ca,bad,ca_trace,currents,conductances,gating,finalgate,finalg,finali
