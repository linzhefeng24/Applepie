"""Three electrical compartments per sensory-axon prototype, continuous HH/Ca/SK.
Actual simulated chief9A spikes drive GABA conductance at hook terminals only.
The identical external joint trajectory drives active/passive conditions. This
is a new motif model, not recovered hook/claw connectome identities.
Units ms,mV,pF,nS,pA,uM. No prescribed output mask or fitted phase/waveform.
"""
import numpy as np
from numba import njit
from model import gates

@njit(cache=True)
def solve_cable(diagonal,rhs,k01,k12):
 d1=diagonal[1]-k01*k01/diagonal[0];r1=rhs[1]+k01*rhs[0]/diagonal[0]
 d2=diagonal[2]-k12*k12/d1;r2=rhs[2]+k12*r1/d1
 v2=r2/d2;v1=(r1+k12*v2)/d1;v0=(rhs[0]+k01*v1)/diagonal[0]
 return np.array([v0,v1,v2])

@njit(cache=True)
def kernel(source_spikes,constants,C,gna,gk,gl,gca,axial,dt,steps,stride):
 EL,ENa,EK,ECa,EI,gsk,tc,alpha,kd,gpeak,tr,td,delay,rest,amp,period,on,off,cp,cv=constants
 v=np.full((4,3),-65.);mh=np.empty((4,3));hh=mh.copy();nh=mh.copy();ca=np.zeros((4,3));counts=np.zeros((int(np.ceil(steps*dt)),4,3),np.int16)
 for f in range(4):
  for j in range(3):
   am,bm,ah,bh,an,bn=gates(v[f,j]);mh[f,j]=am/(am+bm);hh[f,j]=ah/(ah+bh);nh[f,j]=an/(an+bn)
 nrec=(steps+stride-1)//stride;V=np.zeros((nrec,4,3));CA=V.copy();GI=np.zeros(nrec);TH=np.zeros(nrec);INPUT=np.zeros((nrec,4));xe=0.;ye=0.;last=-1;bad=False
 peak_time=np.log(td/tr)/(1/tr-1/td);norm=1/(np.exp(-peak_time/td)-np.exp(-peak_time/tr));de1=np.exp(-dt/tr);de2=np.exp(-dt/td)
 for k in range(steps):
  tm=k*dt;xe*=de1;ye*=de2;b=int(np.floor(tm-delay))
  if b>=0 and b!=last:
   if b<len(source_spikes):inc=source_spikes[b]*gpeak*norm;xe+=inc;ye+=inc
   last=b
  gi=max(0.,ye-xe);theta=rest;velocity=0.
  if on<=tm<off:
   phase=2*np.pi*(tm-on)/period;theta=rest+amp*np.sin(phase);velocity=amp*2*np.pi/period*1000*np.cos(phase)
  input_current=np.array([cv*max(-velocity,0.),cv*max(velocity,0.),cp*max(rest-theta,0.),cp*max(theta-rest,0.)])
  for f in range(4):
   diag=np.zeros(3);rhs=np.zeros(3);old=v[f].copy()
   for j in range(3):
    am,bm,ah,bh,an,bn=gates(old[j]);mh[f,j]=am/(am+bm)+(mh[f,j]-am/(am+bm))*np.exp(-dt*(am+bm));hh[f,j]=ah/(ah+bh)+(hh[f,j]-ah/(ah+bh))*np.exp(-dt*(ah+bh));nh[f,j]=an/(an+bn)+(nh[f,j]-an/(an+bn))*np.exp(-dt*(an+bn))
    gn=gna[j]*mh[f,j]**3*hh[f,j];gpot=gk[j]*nh[f,j]**4;cinf=1/(1+np.exp(-(old[j]+25)/6));gc=gca[j]*cinf**2;gs=gsk*ca[f,j]/(ca[f,j]+kd);inhib=gi if f<2 and j==2 else 0.
    coupling=axial[0] if j==0 else axial[1] if j==2 else axial[0]+axial[1]
    diag[j]=C[j]/dt+gl[j]+gn+gpot+gc+gs+inhib+coupling;rhs[j]=C[j]/dt*old[j]+gl[j]*EL+gn*ENa+(gpot+gs)*EK+gc*ECa+inhib*EI
    if j==0:rhs[j]+=input_current[f]
   new=solve_cable(diag,rhs,axial[0],axial[1]);v[f]=new
   for j in range(3):
    cinf=1/(1+np.exp(-(old[j]+25)/6));gc=gca[j]*cinf**2;ca[f,j]=max(0.,ca[f,j]+dt*(-alpha*gc*(new[j]-ECa)-ca[f,j]/tc))
    if old[j]<0<=new[j]:counts[min(int(tm),len(counts)-1),f,j]+=1
    if not np.isfinite(new[j]) or new[j]<-160 or new[j]>120:bad=True
  if bad:break
  if k%stride==0:
   r=k//stride;V[r]=v;CA[r]=ca;GI[r]=gi;TH[r]=theta;INPUT[r]=input_current
 return V,CA,GI,TH,INPUT,counts,bad

def simulate(source_spikes,parameters):
 p=parameters
 source_spikes=np.asarray(source_spikes,dtype=float)
 if source_spikes.ndim!=1 or not np.isfinite(source_spikes).all() or np.any(source_spikes<0):raise ValueError('Nonnegative finite 1ms source spike counts required')
 for key in ['dt_ms','duration_ms','Ca_tau_ms','GABA_rise_ms','GABA_decay_ms','movement_period_ms']:
  if not np.isfinite(p[key]) or p[key]<=0:raise ValueError(key)
 if p['GABA_decay_ms']<=p['GABA_rise_ms'] or p['chief_compound_peak_nS']<0:raise ValueError('Invalid synapse kinetics')
 for key in ['capacitance_pF','gNa_nS','gK_nS','gLeak_nS','gCa_nS','axial_nS']:
  if len(p[key])!=(2 if key=='axial_nS' else 3) or not np.isfinite(p[key]).all() or min(p[key])<=0:raise ValueError(key)
 names=['ELeak_mV','ENa_mV','EK_mV','ECa_mV','EGABA_mV','gSK_nS','Ca_tau_ms','Ca_alpha','Ca_SK_Kd_uM','chief_compound_peak_nS','GABA_rise_ms','GABA_decay_ms','conduction_delay_ms','rest_angle_deg','movement_amplitude_deg','movement_period_ms','movement_start_ms','movement_end_ms','claw_current_pA_per_deg','hook_current_pA_per_deg_s'];dt=p['dt_ms'];steps=round(p['duration_ms']/dt);stride=max(1,round(p['record_interval_ms']/dt));out=kernel(np.asarray(source_spikes,dtype=float),np.array([p[x] for x in names]),*[np.array(p[x],dtype=float) for x in ['capacitance_pF','gNa_nS','gK_nS','gLeak_nS','gCa_nS','axial_nS']],dt,steps,stride);release=(out[1][:,:,2]**p['release_Hill'])/(p['release_Kd_uM']**p['release_Hill']+out[1][:,:,2]**p['release_Hill']);return dict(voltage=out[0],calcium=out[1],gaba_nS=out[2],angle_deg=out[3],input_current_pA=out[4],spikes=out[5],numerical_failure=bool(out[6]),terminal_release_proxy=release,time_ms=np.arange(len(out[0]))*stride*dt+dt)
