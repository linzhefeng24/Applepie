"""Check parameter-externalized package against the chosen frozen neural run."""
from pathlib import Path
import json,sys,hashlib
import numpy as np
R=Path(__file__).parent;P=R/'build/UnifiedFlyModel';sys.path.insert(0,str(P/'02_code'));from flymodel import Model
reference=R.parents[1]/'research/brake-retuning-20261115/results/terminal-r2/BRK.npz';old=np.load(reference);m=Model(P/'01_model/model.yaml');r=m.run_neural('BRK',record_ids=list(old['record_body_ids']),record_interval_ms=.5);n=len(old['time_ms']);rows={k:float(np.max(abs(r[k][:n]-old[k]))) for k in ['voltage','calcium','currents_pA','conductances_nS']};d={'source':'new packaged implementation checked against selected frozen run','model_sha256':m.sha256,'reference_sha256':hashlib.sha256(reference.read_bytes()).hexdigest(),'all_spikes_identical':bool(np.array_equal(r['spikes'],old['spikes'])),'recorded_state_max_abs_difference':rows,'parameters_externalized':True,'selected_model':'one MaleCNS3988 R2 model','reference_recorded_rows':n};(R/'source-equivalence.json').write_text(json.dumps(d,indent=2)+'\n');assert d['all_spikes_identical'],d;assert rows['voltage']<1e-7,d;print(d)
