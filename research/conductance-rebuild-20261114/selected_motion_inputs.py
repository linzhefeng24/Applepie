"""Decode actual stored HH outputs with fixed selected NMJ gains; no refitting."""
from pathlib import Path
import json,numpy as np
from asymmetry_refinement import pools,T,O,R
from muscle_readout import integrate
sel=json.load(open(O/'motion-physical-selection.json'))['selected']['name'];saved=np.load(O/(sel+'.npz'));tau=float(saved['tau_ms']);gain=saved['constant_gain'];duration_steps=10000
sources={'dynamic':np.load(O/(json.load(open(O/'selected.json'))['trial']+'.npz'))['spikes']}
for name in ['E2_silenced','fine']:
 p=O/('neural-validation-'+name+'.npz')
 if p.exists():sources[name]=np.load(p)['spikes']
for name,spikes in sources.items():
 rates=np.array([np.mean(spikes[:,p],axis=1)*1000. if p else np.zeros(len(spikes)) for p in pools]).T;decay=np.exp(-1/tau);state=np.zeros(130);filtered=np.empty_like(rates)
 for k in range(len(rates)):state=decay*state+(1-decay)*rates[k];filtered[k]=state
 ix=400+np.arange(duration_steps)//10-1;u=np.clip(filtered[ix]/100.*gain[None,:],0,1);a=np.array([integrate(u[:,j],1.,T['initial_a'][j],*T['dynprm'][j,:2],float(T['dt_s']))[1::2] for j in range(130)]).T
 np.savez_compressed(O/('long-input-'+name+'.npz'),u=u,activation=a,muscle_ids=T['muscle_ids'],tau_ms=tau,constant_gain=gain)
 if name=='dynamic':np.testing.assert_allclose(u[:4000],saved['predicted_u_native'],atol=1e-14,rtol=0)
 print(name,'decoded',len(u),'native steps',flush=True)
