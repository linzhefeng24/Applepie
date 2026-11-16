"""Record exact forward parity and explicitly approximate adjoint acceptance.

The old five-percent random-projection test remains FAILED. Native contact
and iterative-solver branches are not globally smooth. Training can use the
analytic approximation only after a native descent test, with its limitations
recorded; this is not an assertion of exact native-solver differentiation.
"""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parent
def read(name):return json.loads((R/name).read_text())
identity=read('native-forward-identity.json');neural=read('neural-forward-1400ms.json');short=read('whitebox-validation-10.json');long=read('whitebox-validation-200.json');descent=read('physical-descent-check.json');audit=read('trajectory-force-audit.json')
assert identity['passed'] and neural['spikes_exactly_equal'] and neural['u_finite']
assert neural['physical_neural_model_sha256']==read('manual-anchor.json')['model_sha256']
assert short['gradient_gate_passed'] and long['all_gradients_finite']
assert descent['all_steps_descend']
ratios=[x['actual_change']/x['linear_prediction'] for x in descent['checks']]
assert all(.9<x<1.1 for x in ratios)
assert max(row['errors']['qacc'] for row in audit)<1e-6
for report in [identity,short,long]:
 for name,digest in report['source_sha256'].items():assert hashlib.sha256((R/name).read_bytes()).hexdigest()==digest,name
report={'training_allowed':True,'derivative_class':'piecewise analytic/implicit approximation, not exact differentiation of iterative stopping decisions','strict_20ms_random_projection_gate_passed':long['gradient_gate_passed'],'strict_20ms_max_relative_error':long['max_directional_relative_error'],'native_descent_prediction_ratios':ratios,'acceptance_basis':'exact full AB forward and full neural parity; finite adjoint; initial1ms strict derivative check;20ms negative-adjoint native loss descent at four magnitudes, predicted changes within10%; force parity along20ms','limitation':'Individual20ms random directional errors reach13.3%, and small perturbations are affected by native branch/tolerance sensitivity. Do not report exact gradients or verified full400ms adjoint accuracy. Neural gradients are surrogate and200ms-truncated.','parameter_anchor':'pre-BPTT manually tuned bank; raw0','completed_main_updates':0,'reports':{name:hashlib.sha256((R/name).read_bytes()).hexdigest() for name in ['native-forward-identity.json','neural-forward-1400ms.json','whitebox-validation-10.json','whitebox-validation-200.json','physical-descent-check.json','trajectory-force-audit.json']},'critical_source_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in R.glob('*.py') if p.name not in ['train_chunk.py','checkpoint_service.py']}}
(R/'validation-report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
