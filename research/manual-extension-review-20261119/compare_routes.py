"""Matched causal comparisons of concrete feedback and core→MN routes."""
from pathlib import Path
import json,numpy as np
R=Path(__file__).resolve().parent;D=R/'results'
def load(case):return np.load(D/(case+'.npz'),allow_pickle=False)
def read(case):
 z=load(case);ids=z['body_ids'].tolist();rec=z['record_indices'].tolist();cells={}
 for bid in ['10045','10056','800173','800863','801884','800288','903216','803183','801173','800061','802072']:
  i=ids.index(bid);ts=np.flatnonzero(z['spikes'][:,i]);ts=ts[(ts>=200)&(ts<1500)];starts=ts[np.r_[True,np.diff(ts)>60]] if len(ts) else ts
  q={'spikes':len(ts),'spike_times_ms':ts.tolist(),'gap60_burst_onsets_ms':starts.tolist(),'gap_definition_not_a_rhythm_pass_criterion':True}
  if i in rec:q['minimum_inhibitory_synaptic_current_pA']=float(z['currents_pA'][:,rec.index(i),1].min())
  cells[bid]=q
 return cells
cases=['DN_drive','I1_exc_x2','I1_exc_x4','I1_exc_x2_cut_feedback','I1_exc_x2_E2_silenced','I1_exc_x2_cut_E2_MN','E1_silenced','E2_silenced']
results={case:read(case) for case in cases if (D/(case+'.npz')).exists()}
report={'cases':results,'interpretation':[
 'New E1/E2/I1 exact T1 identities were absent from original frozen model. Structural restoration alone is not functional reproduction.',
 'In candidate baseline both T1 I1 cells are silent. Gain2 recruits them after E1 and E2; source current remains tonic.',
 'Cutting I1 feedback at matched gain2 changes E1 inhibition and spike/burst timing, showing a functioning feedback contribution, not exclusive pacemaking.',
 '800061/802072 are concrete mapped promotor MN candidates; their earliest response can precede E2 firing, so this direct E2 route is not the only recruitment route.',
 'Spiking persisting after E1/E2 silencing is reported with exact times; no claim that all such residual spiking is rhythmic solely from counts.',
 'All conclusions are within this HH model and sign assumptions, not biological identification of a real pacemaker.'
]};(R/'matched_route_comparisons.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
for case,cells in results.items():print(case,{bid:q['spikes'] for bid,q in cells.items()})
