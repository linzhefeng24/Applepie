"""Bitwise regression against preceding edge-scan implementation, not a model fit."""
from pathlib import Path
import importlib.util,json,time,numpy as np,subprocess,hashlib
from model import simulate
R=Path(__file__).parent;ref=subprocess.check_output(['git','show','6dda175:research/conductance-rebuild-20261114/model.py'],cwd=R);Path('/tmp/neural_model_before_sparse_events.py').write_bytes(ref.replace(b'@njit(cache=True)',b'@njit(cache=False)'));spec=importlib.util.spec_from_file_location('neural_old_event_scan','/tmp/neural_model_before_sparse_events.py');old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old);cases=[]
W=np.load(R/'data/core.npz')['weights'];p=json.load(open(R/'configs/core-selected.json'));cases.append(('recorded_core',W,['DN','E1','E2','I1','I2'],p,None))
rng=np.random.default_rng(512)
for n in [12,40]:
 w=rng.integers(-40,60,(n,n)).astype(float);w[rng.random((n,n))>.15]=0.;np.fill_diagonal(w,0);q={'duration_ms':500.,'onset_ms':100.,'dt_ms':.0125,'drive_pA':160.};wave=np.zeros((500,n));wave[100:350,:2]=160;cases.append((f'event_pulse_{n}',w,['DN']*2+['other']*(n-2),q,wave))
records=[]
for name,w,roles,p,wave in cases:
 a=old.simulate(w,roles,p,drive_waveform=wave);b=simulate(w,roles,p,drive_waveform=wave);keys=['spike_counts_1ms','voltage_first12','calcium_first12_uM','synaptic_currents_pA','synaptic_conductances_nS'];checks={}
 for k in keys:np.testing.assert_array_equal(a[k],b[k]);checks[k]='bitwise identical'
 records.append({'case':name,'checks':checks,'numerical_failure':b['numerical_failure']});print(name,'bitwise identical',flush=True)
(R/'results/event-traversal-regression.json').write_text(json.dumps({'reference_revision':'6dda175','reference_model_sha256':hashlib.sha256(ref).hexdigest(),'checks':records},indent=2))
