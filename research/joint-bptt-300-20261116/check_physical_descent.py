"""Native finite perturbation evidence for an approximate physical adjoint.
The strict directional failure remains a failure; a descent test does not
relabel the derivative exact, nor authorize training by itself.
"""
from pathlib import Path
import json
import numpy as np
from physics import ABPhysics
from native_whitebox import NativeWhitebox
R=Path(__file__).resolve().parent;p=ABPhysics(json.loads((R/'config.json').read_text()));body=NativeWhitebox(p)
with np.load(R/'cache/whitebox-gradient-200.npz') as z:u=z['u'];gradient=z['gradient']
initial=tuple(np.asarray(x) for x in p.initial);target=np.asarray(p.target[:len(u)]);jq=np.asarray(p.joint_ids)
def value(control):
 state=initial;loss=0.
 for k,row in enumerate(control):state=body.native_step_numpy(state,k,row)[:4];loss+=np.sum((state[0][jq]-target[k])**2)/target.size
 return loss
base=value(u);direction=-gradient/abs(gradient).max();rows=[]
for epsilon in [1e-4,1e-3,.003,.01]:
 loss=value(u+epsilon*direction);rows.append(dict(epsilon=epsilon,native_loss=loss,actual_change=loss-base,linear_prediction=float(epsilon*np.sum(gradient*direction))))
report={'baseline_loss':base,'gradient_norm':float(np.linalg.norm(gradient)),'steps':200,'checks':rows,'all_steps_descend':all(x['actual_change']<0 for x in rows),'strict_directional_gate_passed':False,'training_allowed':False}
(R/'physical-descent-check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
