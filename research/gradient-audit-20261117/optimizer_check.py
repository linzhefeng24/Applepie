"""Recover consecutive immutable states and verify the actual Adam update."""
from pathlib import Path
import io,json,zipfile,hashlib
import numpy as np
R=Path(__file__).resolve().parent
files=[Path('/tmp/applepie-gradient-audit/joint-main-e0036-p0-36-335bb225242f.zip'),Path('/tmp/applepie-best-video/joint-main-e0037-p0-37-7f5f28cf16ca.zip')]
banks=[]
for p in files:
 with zipfile.ZipFile(p) as z:
  with np.load(io.BytesIO(z.read('optimizer.npz')),allow_pickle=False) as a:banks.append({k:a[k] for k in a.files})
a,b=banks;assert int(a['completed_updates'])==36 and int(b['completed_updates'])==37
m=b['adam_m'];v=b['adam_v'];t=37;direction=(m/(1-.9**t))/(np.sqrt(v/(1-.999**t))+1e-8);predicted=a['raw']-.002*direction
update_error=float(abs(predicted-b['raw']).max());effective_gradient=(m-.9*a['adam_m'])/.1;v_expected=.999*a['adam_v']+.001*effective_gradient**2
reg_gradient=20*np.expm1(a['raw'])*np.exp(a['raw'])/a['raw'].size
report={'updates':[36,37],'immutable_inputs':[{'name':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files],'adam_update_max_error':update_error,'second_moment_max_error':float(abs(v-v_expected).max()),'clipped_combined_gradient_norm':float(np.linalg.norm(effective_gradient)),'manual_regularizer_gradient_norm_at_update36':float(np.linalg.norm(reg_gradient)),'logged_combined_gradient_norm_at_update36':15648.114332636424,'regularizer_to_combined_gradient_norm_ratio':float(np.linalg.norm(reg_gradient)/15648.114332636424),'note':'Combined norm includes surrogate/cotangent-clipped neural path, not an exact hard-forward derivative. A small norm ratio suggests weak regularizer gradient influence; it does not prove every coordinate is dominated.'}
assert update_error<1e-14 and report['second_moment_max_error']<1e-14
(R/'optimizer.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
