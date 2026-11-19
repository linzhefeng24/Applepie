"""Report actual spike intervals and feedback ablations, not a fitted endpoint loss."""
from pathlib import Path
import json,numpy as np
R=Path(__file__).resolve().parent;out={}
for name,end in [('T1L_core3_4s',3900),('T1L_core3',1500),('T1L_core3_E2_silenced',1500),('T1L_core3_I1_silenced',1500),('T1L_core3_cut_feedback',1500),('T1L_core_plus_E3',1500),('DN_VNC_only',1500),('DN_VNC_only_E2_silenced',1500),('DN_VNC_only_I1_I2_silenced',1500)]:
 z=np.load(R/'results'/f'{name}.npz');ids=z['body_ids'].tolist();ev=z['events_step_cell'];cells={}
 for bid in ['10056','800173','800863','801884']:
  t=(ev[ev[:,1]==ids.index(bid),0]+1)*.0125;t=t[(t>=1000 if end>1500 else t>=500)&(t<end)];isi=np.diff(t)
  cells[bid]={'actual_spike_times_ms':t.tolist(),'ISI_ms':isi.tolist(),'median_ISI_ms':float(np.median(isi)) if len(isi) else None,'inverse_median_ISI_Hz':float(1000/np.median(isi)) if len(isi) else None,'definition':'single-cell interspike interval; not burst-envelope frequency; does not establish perfect periodicity'}
 out[name]=cells
report={'observation':'Minimal DN+E1+E2+I1 motif transforms sustained fast DN spiking into slower sequential core activity, dependent on inhibitory feedback. Reduced-network diagnostic, not six-leg walking or full-network necessity.','cells':out,'glutamate_sign_caveat':'I1 inhibitory output follows the source model receptor/sign assumption, not a measured receptor distribution.'};(R/'local_rhythm_report.json').write_text(json.dumps(report,indent=2)+'\n')
print({k:{bid:round(q['inverse_median_ISI_Hz'],2) if q['inverse_median_ISI_Hz'] else None for bid,q in v.items()} for k,v in out.items()})
