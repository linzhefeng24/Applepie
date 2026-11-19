"""Check finite bounded u, spike counts and targeted named-neuron effects.
Produces observations rather than translating any proxy into behavioral success.
"""
from pathlib import Path
import json,numpy as np
R=Path(__file__).resolve().parent
results={}
for p in sorted((R/'results').glob('*.json')):
 d=json.loads(p.read_text());z=np.load(p.with_suffix('.npz'),allow_pickle=False);u=z['u'];assert u.shape==(1600,130) and np.isfinite(u).all() and u.min()>=0 and u.max()<=1
 d['muscle_observation']={'nonzero_channels':int((u.max(axis=0)>0).sum()),'max_excitation':float(u.max()),'means_are_not_phase_tests':True};results[p.stem]=d
summary={'scope':'independent model reruns; experimental behavior not established','cases':{k:{'spikes_total':v['spikes_total'],'active_MN':v['active_MN'],'MN_count':v['MN_count'],'MN_spikes_before_during_after':v['MN_spikes_before_during_after'],'muscles':v['muscle_observation'],'core_groups':{t:g for t,g in v['groups'].items() if t in ['IN17A001','INXXX466','IN16B036']}} for k,v in results.items()}}
(R/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
for k,v in summary['cases'].items():
 print(k,v['spikes_total'],v['active_MN'],v['MN_spikes_before_during_after'],v['muscles']['nonzero_channels']);print(' core', {t:sum(sum(g[w]) for w in ['spike_counts_200_600ms','spike_counts_600_1100ms','spike_counts_1100_1500ms']) for t,g in v['core_groups'].items()})
