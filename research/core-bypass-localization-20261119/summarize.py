"""Named-neuron timelines and matched interventions; no scalar fitting objective."""
from pathlib import Path
import json,numpy as np
R=Path(__file__).resolve().parent;cases={}
for p in sorted((R/'results').glob('*.json')):
 d=json.loads(p.read_text());z=np.load(p.with_suffix('.npz'));u=z['u'];assert u.shape==(len(z['spikes']),130) and np.isfinite(u).all() and np.logical_and(u>=0,u<=1).all()
 cases[p.stem]={'neurons':d['neurons'],'spikes_total':d['spikes_total'],'u_nonzero_channels':int((u.max(axis=0)>0).sum()),'anatomical_counts_changed':d['anatomical_counts_changed'],'changes':d['applied_changes'],'baseline_validation':d['validation']}
s={'scope':'Mechanistic model observations, not completed laboratory behavior reproduction','complete_cases':len(cases),'cases':cases,'intervention_table_I1':[{ 'condition':k,'left_I1_801884':cases[k]['neurons']['801884']['count'],'right_I1_803183':cases[k]['neurons']['803183']['count']} for k in ['baseline','cut_E2_I1','cut_E3_I1','cut_E2_E3_I1','E2_silenced'] if k in cases]};(R/'summary.json').write_text(json.dumps(s,indent=2)+'\n')
for k,v in cases.items():print(k,'u active',v['u_nonzero_channels'],{b:(v['neurons'][b]['count'],v['neurons'][b]['first_ms']) for b in ['801884','803183','800061','802072']})
