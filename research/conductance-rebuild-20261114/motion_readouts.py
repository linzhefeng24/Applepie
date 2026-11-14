"""Second-stage developmental objective: actual repeated joint motion.
After fixed-reference torque matching failed the motion criterion, test causal
NMJ filtering and constant gain scales. No target waveform or imposed oscillation
is injected; all time dependence still comes from the HH spikes.
"""
from pathlib import Path
import json,numpy as np
from asymmetry_refinement import readout,score,T,R,O
from muscle_readout import integrate
best=json.load(open(O/'selected.json'));z=np.load(O/(best['trial']+'.npz'));records=[]
for tau in [2.,5.,10.,20.,40.]:
 pred,g,signal,_=readout(z['spikes'],tau_ms=tau,torque_weight=0.)
 for scale in [.75,1.,1.5]:
  name=f'motion_tau{tau:g}_gain{scale:g}';u=np.clip(signal*g[None,:]*scale,0,1);a=np.array([integrate(u[:,j],1.,T['initial_a'][j],*T['dynprm'][j,:2],float(T['dt_s']))[1::2] for j in range(130)]).T
  np.savez_compressed(O/(name+'.npz'),predicted_u_native=u,predicted_a=a,target_a=T['target_a'],muscle_ids=T['muscle_ids'],time_s=T['time_s']);records.append({'name':name,'tau_ms':tau,'constant_gain_scale':scale,'neural_candidate':best['trial'],'group_parameters':best['config']['group_parameters'],'selection_scope':'Developmental actual-body motion criterion; no held-out walking claim'})
(O/'motion-readout-grid.json').write_text(json.dumps({'criteria_frozen_before_body_runs':{'peak_to_peak_deg':5,'min_peaks':2,'min_troughs':2,'prominence_deg':2,'evaluation_s':[.08,.4],'min_body_up_z':.8},'trials':records},indent=2));print('Generated',len(records),'motion candidates',flush=True)
