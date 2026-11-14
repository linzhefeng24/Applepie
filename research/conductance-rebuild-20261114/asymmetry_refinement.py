"""Type-shared neural parameter trials with native-muscle torque constraints.
No imposed phase oscillators, added edges, force injection, or time-varying
free muscle controls. Constant NN->muscle gains fit only the first60%.
Torque here uses fixed native reference geometry; actual body tests are separate.
"""
from pathlib import Path
import csv,json,time,hashlib
import numpy as np
from scipy.optimize import minimize_scalar
from scipy.signal import find_peaks
from network import load,simulate_network
from grouped_parameters import group_key,regularization
from muscle_readout import integrate
from metrics import summarize
R=Path(__file__).parent;O=R/'results/asymmetry';O.mkdir(exist_ok=True)
T=np.load(R/'data/old-A-muscle-targets.npz');TR=np.load(R/'data/tibia-reference-transmission.npz');C=TR['coeff'];B=TR['bias'];target=T['target_a'];split=1200;dt=float(T['dt_s']);target_tau=target@C.T+B
norm=np.maximum(np.std(target_tau[:split],axis=0),.05*np.max(abs(C),axis=1));norm=np.maximum(norm,1e-12)
W,roles,meta=load('onehop',full_vnc=True);lookup={int(x['bodyId']):i for i,x in enumerate(meta)};cross={r['model_channel']:r for r in csv.DictReader(open(R/'data/model-130-channel-candidate-crosswalk.csv',encoding='utf-8-sig'))};pools=[]
for mid in T['muscle_ids']:pools.append([lookup[int(s)] for s in cross[str(mid)]['candidate_MANC_body_ids'].split(';') if s and int(s) in lookup])
mapped=np.array([bool(p) for p in pools]);base=json.load(open(R/'configs/adult-network-selected.json'));base['duration_ms']=1600.
F='motor neuron|type:Ti flexor MN';E='motor neuron|type:Ti extensor MN'
TRIALS=[('baseline',{}),('flexor_gain',{F:{'excitatory_gain':1.5},E:{'excitatory_gain':.75}}),('extensor_gain',{F:{'excitatory_gain':.75},E:{'excitatory_gain':1.5}}),('flexor_adaptation',{F:{'SK_scale':1.5},E:{'SK_scale':.75}}),('extensor_adaptation',{F:{'SK_scale':.75},E:{'SK_scale':1.5}}),('flexor_slow',{F:{'gate_speed':.85},E:{'gate_speed':1.15}}),('extensor_slow',{F:{'gate_speed':1.15},E:{'gate_speed':.85}}),('flexor_combined',{F:{'excitatory_gain':1.5,'SK_scale':1.5},E:{'excitatory_gain':.75,'SK_scale':.75}}),('extensor_combined',{F:{'excitatory_gain':.75,'SK_scale':.75},E:{'excitatory_gain':1.5,'SK_scale':1.5}})]

def readout(spikes,tau_ms=40.,torque_weight=.10):
 rates=np.array([np.mean(spikes[:,pool],axis=1)*1000. if pool else np.zeros(len(spikes)) for pool in pools]).T
 state=np.zeros(130);filtered=np.empty_like(rates);decay=np.exp(-1./tau_ms)
 for k in range(len(rates)):state=decay*state+(1-decay)*rates[k];filtered[k]=state
 ix=400+np.arange(4000)//10-1;signal=filtered[ix]/100.;pred=np.empty_like(target);gains=np.zeros(130)
 def activation(j,g):return integrate(signal[:,j],g,T['initial_a'][j],*T['dynprm'][j,:2],dt)[1::2]
 for j in range(130):
  if mapped[j] and signal[:,j].max()>0:
   fit=minimize_scalar(lambda g:np.mean((activation(j,g)[:split]-target[:split,j])**2),bounds=(0,10),method='bounded');gains[j]=fit.x
  pred[:,j]=activation(j,gains[j])
 # Coordinate refinement of constant readout gains: adds a torque objective,
 # not an independently specified time-series. Target/model force parameters fixed.
 tau=pred@C.T+B
 for sweep in range(2 if torque_weight>0 else 0):
  for j in range(130):
   if not mapped[j] or signal[:,j].max()==0 or np.max(abs(C[:,j]))==0:continue
   other=tau[:split]-pred[:split,j,None]*C[None,:,j]
   def loss(g):
    a=activation(j,g)[:split];activation_loss=np.mean((a-target[:split,j])**2)/mapped.sum();torque_loss=torque_weight*np.mean(((other+a[:,None]*C[None,:,j]-target_tau[:split])/norm)**2)
    return activation_loss+torque_loss
   fit=minimize_scalar(loss,bounds=(0,10),method='bounded',options={'xatol':1e-4});old=pred[:,j].copy();gains[j]=fit.x;pred[:,j]=activation(j,fit.x);tau+=(pred[:,j]-old)[:,None]*C[None,:,j]
 return pred,gains,signal,tau

def score(pred,tau,groups):
 a_train=float(np.sqrt(np.mean((pred[:split,mapped]-target[:split,mapped])**2)));q_train=float(np.sqrt(np.mean(((tau[:split]-target_tau[:split])/norm)**2)))
 metrics={'activation_train_RMSE':a_train,'torque_train_normalized_RMSE':q_train,'activation_holdout_RMSE':float(np.sqrt(np.mean((pred[split:,mapped]-target[split:,mapped])**2))),'torque_holdout_normalized_RMSE':float(np.sqrt(np.mean(((tau[split:]-target_tau[split:])/norm)**2))),'group_regularization':regularization(groups)}
 metrics['training_score']=a_train+.10*q_train+.002*metrics['group_regularization'];return metrics

if __name__=='__main__':
 records=[]
 for label,groups in TRIALS:
  start=time.time();p={**base,'group_parameters':groups};out=simulate_network(W,roles,meta,p);s=summarize(out);pred,gain,signal,tau=readout(out['spike_counts_1ms']);sc=score(pred,tau,groups);rec={'trial':label,'config':p,'metrics':sc,'periodic_MN':s['rhythmic_MN'],'numerical_failure':out['numerical_failure'],'graph_scope':'1454-cell full-VNC-source induced subgraph; not intact full VNC','runtime_s':time.time()-start};records.append(rec)
  np.savez_compressed(O/f'{label}.npz',predicted_a=pred,target_a=target,time_s=T['time_s'],muscle_ids=T['muscle_ids'],gain=gain,predicted_u_native=np.clip(signal*gain[None,:],0,1),reference_geometry_tibia_torque=tau,spikes=out['spike_counts_1ms'],body_ids=[int(x['bodyId']) for x in meta])
  (O/'trials.json').write_text(json.dumps(records,indent=2));print(label,sc,'MN',s['rhythmic_MN'],'sec',round(time.time()-start,1),flush=True)
 eligible=[r for r in records if not r['numerical_failure'] and r['periodic_MN']>0];best=min(eligible,key=lambda x:x['metrics']['training_score']);(O/'selected.json').write_text(json.dumps(best,indent=2));(O/'scope.json').write_text(json.dumps({'selection':'training score only, no holdout tuning','score':'activation train RMSE +0.10*normalized fixed-reference torque RMSE +0.002*group-prior penalty','readout':'Causal40ms spike filter,1ms delay; nonnegative constant gains0..10; native activation, no phase oracle','motion_validation_required':True,'individual_offsets_enabled':False,'structural_edges_modified':False,'known_adult_intrinsic_targets_changed':False},indent=2));print('SELECTED',best['trial'],flush=True)
