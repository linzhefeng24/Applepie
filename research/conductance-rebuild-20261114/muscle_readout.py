"""Causal spike-to-u-to-a candidate readout. Gains fit on training only.
Preserves ambiguity and missing maps. Uses independently checked native MuJoCo
activation law, original initial activations and 0.1ms Euler integration.
No freely specified per-channel trajectory, phase oracle or target-state reset.
"""
from pathlib import Path
import csv,json,sys
import numpy as np
from numba import njit
from scipy.optimize import minimize_scalar
R=Path(__file__).parent
@njit(cache=True)
def muscle_derivative(u,a,ta,td):
 aa=min(1.,max(0.,a));uu=min(1.,max(0.,u));t=ta*(.5+1.5*aa) if uu>aa else td/(.5+1.5*aa)
 return (uu-aa)/max(t,1e-10)
@njit(cache=True)
def integrate(signal,gain,a0,ta,td,dt):
 out=np.empty(len(signal));a=a0
 for t in range(len(signal)):
  u=min(1.,max(0.,signal[t]*gain));a=a+dt*muscle_derivative(u,a,ta,td);a=min(1.,max(0.,a));out[t]=a
 return out

def main():
 check=np.load(R/'data/native-muscle-derivative-check.npz');err=0.
 for k in range(check['u'].shape[0]):
  for j in range(130):err=max(err,abs(muscle_derivative(check['u'][k,j],check['a'][k,j],*check['dynprm'][j,:2])-check['reference'][k,j]))
 assert err<1e-9,err
 z=np.load(R/'data/old-A-muscle-targets.npz');dt=float(z['dt_s']);native=[]
 for j in range(130):native.append(integrate(z['target_u'][:,j],1.,z['initial_a'][j],*z['dynprm'][j,:2],dt)[1::2])
 native=np.array(native).T;native_err=float(np.max(abs(native-z['target_a'])))
 assert native_err<1e-8,native_err
 prefix='adult-muscle-readout' if len(sys.argv)>1 else 'muscle-readout';source='adult-all-legs-subgraph.npz' if len(sys.argv)>1 else 'all-legs-subgraph.npz';n=np.load(R/'results'/source);spikes=n['spikes'].astype(float);lookup={int(b):i for i,b in enumerate(n['body_ids'])};cross={x['model_channel']:x for x in csv.DictReader(open(R/'data/model-130-channel-candidate-crosswalk.csv',encoding='utf-8-sig'))}
 pools=[];mapped=[];rates=[]
 for mid in z['muscle_ids']:
  row=cross[str(mid)];pool=[int(s) for s in row['candidate_MANC_body_ids'].split(';') if s and int(s) in lookup];pools.append(pool);mapped.append(bool(pool));rates.append(np.mean(spikes[:,[lookup[b] for b in pool]],axis=1)*1000. if pool else np.zeros(len(spikes)))
 rates=np.array(rates).T;target=z['target_a'];split=1200;results=[];best=None
 # Absolute neural window fixed before readout fitting; 400-800ms after starting
 # simulation, neither picked from the target nor shifted using holdout data.
 for tau_ms in [2.,5.,10.,20.,40.]:
  decay=np.exp(-1./tau_ms);filtered=np.empty_like(rates);state=np.zeros(130)
  for k in range(len(rates)):state=decay*state+(1-decay)*rates[k];filtered[k]=state
  ix=np.maximum(0,np.minimum(len(filtered)-1,400+np.arange(4000)//10-1));signal=filtered[ix]/100.;pred=[];gains=[];nonzero=[]
  for j in range(130):
   sig=signal[:,j];a0=z['initial_a'][j];ta,td=z['dynprm'][j,:2]
   if not mapped[j] or sig.max()==0:g=0.
   else:
    def loss(g):return np.mean((integrate(sig,g,a0,ta,td,dt)[1::2][:split]-target[:split,j])**2)
    opt=minimize_scalar(loss,bounds=(0.,10.),method='bounded',options={'xatol':1e-5});g=float(opt.x)
   pred.append(integrate(sig,g,a0,ta,td,dt)[1::2]);gains.append(g);nonzero.append(bool(sig.max()>0))
  pred=np.array(pred).T;mask=np.array(mapped);nonzero=np.array(nonzero);train=float(np.sqrt(np.mean((pred[:split,mask]-target[:split,mask])**2)));test=float(np.sqrt(np.mean((pred[split:,mask]-target[split:,mask])**2)));row={'tau_ms':tau_ms,'train_RMSE_mapped':train,'holdout_RMSE_mapped':test,'mapped_channels':int(mask.sum()),'neural_signal_channels':int(nonzero.sum()),'holdout_RMSE_all130_including_missing_zero_readouts':float(np.sqrt(np.mean((pred[split:]-target[split:])**2)))};results.append(row)
  if best is None or train<best[0]:best=(train,pred,gains,signal,row)
  print(row,flush=True)
 _,pred,gains,signal,selected=best
 np.savez_compressed(R/f'results/{prefix}.npz',predicted_a=pred,target_a=target,time_s=z['time_s'],muscle_ids=z['muscle_ids'],mapped=np.array(mapped),gain=gains,presynaptic_rate_signal=signal,predicted_u_native=np.clip(signal*np.asarray(gains)[None,:],0,1))
 report={'neural_spike_source':source,'candidate_filters':results,'selection_policy':'minimum training RMSE only; last40 percent is holdout and never used for parameter selection','selected':selected,'native_derivative_max_error':err,'native_activation_replay_max_error':native_err,'old_reported_three_channel_RMSE_0_446_comparable':False,'reason_not_comparable':'New scope/graph and channel set; original readout checkpoint missing','MN_to_MTU_verified':False,'missing_mapping_channels':[str(x) for x,ok in zip(z['muscle_ids'],mapped) if not ok],'candidate_pool_body_ids':{str(mid):pool for mid,pool in zip(z['muscle_ids'],pools)},'body_walking_tested':False,'sources':'Author-signed full-VNC-source subgraph; candidate MN-muscle crosswalk; oldA target; native MuJoCo3.3.2 derivative oracle'}
 (R/f'results/{prefix}.json').write_text(json.dumps(report,indent=2))
if __name__=='__main__':main()
