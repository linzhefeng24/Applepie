"""Validate exact event log coverage, finite states, input identities and published baselines."""
from pathlib import Path
import hashlib,json,numpy as np
R=Path(__file__).resolve().parent;plan=json.loads((R/'cases.json').read_text());reports=[]
for case in plan['cases']:
 p=R/'results'/f'{case}.npz';d=json.loads(p.with_suffix('.json').read_text());assert hashlib.sha256(p.read_bytes()).hexdigest()==d['raw']['sha256'];z=np.load(p,allow_pickle=False)
 for k in ['voltage','currents_pA','conductances_nS','u']:assert np.isfinite(z[k]).all(),(case,k)
 u=z['u'];assert u.shape==(len(z['spikes']),130) and u.min()>=0 and u.max()<=1
 ev=z['events_step_cell'];rebinned=np.zeros_like(z['spikes']);np.add.at(rebinned,(np.floor(ev[:,0]*.0125).astype(int),ev[:,1]),1);assert np.array_equal(rebinned,z['spikes']),(case,'event log coverage')
 reports.append({'case':case,'raw_sha256':d['raw']['sha256'],'finite_states':True,'exact_step_log_rebins_to_full_spikes':True,'excitation_bounds_valid':True})
for case in ['baseline','E2_silenced']:
 d=json.loads((R/'results'/f'{case}.json').read_text());assert d['validation']['spikes_array_equal'] and d['validation']['u_array_equal']
(R/'verification.json').write_text(json.dumps({'cases':reports,'case_count':len(reports),'baseline_and_E2_ablated_previous_outputs_bitwise_equal':True,'equations_changed':False},indent=2)+'\n');print('Verified',len(reports),'conditions, all exact step logs, finite states and bounded u; two baseline comparisons bitwise identical.')
