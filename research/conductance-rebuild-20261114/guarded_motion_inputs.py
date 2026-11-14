"""Revert the Ti-extensor kinetic change that caused an E2-lesion residual;
keep the shared flexor adjustment and frozen NMJ gains. No per-cell exception.
"""
from pathlib import Path
import json,numpy as np
from asymmetry_refinement import pools,T,O,R
from muscle_readout import integrate
rows=json.load(open(O/'guard-refinement.json'));p=next(x['config'] for x in rows if x['variant']=='flexor_only');(R/'configs/asymmetry-guarded.json').write_text(json.dumps(p,indent=2));name=json.load(open(O/'motion-physical-selection.json'))['selected']['name'];old=np.load(O/(name+'.npz'));gain=old['constant_gain'];tau=float(old['tau_ms'])
for mode,src in [('guarded','baseline'),('guarded_E2','E2_silenced'),('guarded_fine','fine_baseline'),('guarded_fine_E2','fine_E2_silenced')]:
 z=np.load(O/('guarded-fine-'+src[5:]+'.npz' if src.startswith('fine_') else f'guard-flexor_only-{src}.npz'));spikes=z['spikes'];rates=np.array([np.mean(spikes[:,pool],axis=1)*1000. if pool else np.zeros(len(spikes)) for pool in pools]).T;filtered=np.empty_like(rates);state=np.zeros(130);decay=np.exp(-1./tau)
 for k in range(len(rates)):state=decay*state+(1-decay)*rates[k];filtered[k]=state
 ix=400+np.arange(10000)//10-1;u=np.clip(filtered[ix]/100*gain[None,:],0,1);a=np.array([integrate(u[:,j],1.,T['initial_a'][j],*T['dynprm'][j,:2],float(T['dt_s']))[1::2] for j in range(130)]).T;np.savez_compressed(O/('long-input-'+mode+'.npz'),u=u,activation=a,muscle_ids=T['muscle_ids'],constant_gain=gain,tau_ms=tau)
