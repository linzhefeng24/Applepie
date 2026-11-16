"""Resolve perturbation-size/contact sensitivity using an already computed VJP."""
from pathlib import Path
import json
import numpy as np
from physics import ABPhysics
from native_whitebox import NativeWhitebox
R=Path(__file__).resolve().parent;p=ABPhysics(json.loads((R/'config.json').read_text()));body=NativeWhitebox(p)
with np.load(R/'cache/whitebox-gradient-200.npz') as z:u=z['u'];gradient=z['gradient']
initial=tuple(np.asarray(x) for x in p.initial);target=np.asarray(p.target[:len(u)]);jq=np.asarray(p.joint_ids)
def evaluate(controls):
 state=initial;loss=0.;topology=[]
 for k,row in enumerate(controls):
  result=body.native_step_numpy(state,k,row);state=result[:4];loss+=np.sum((state[0][jq]-target[k])**2)/target.size
  topology.append(tuple((tuple(c.geom),int(c.dim),int(c.exclude)) for c in body.data.contact))
 return loss,topology
base,topology=evaluate(u);rng=np.random.default_rng(42);checks=[]
for i in range(3):
 direction=rng.normal(size=u.shape);direction/=abs(direction).max();ad=float(np.sum(gradient*direction))
 for eps in [1e-5,3e-5,1e-4,3e-4,1e-3]:
  plus,pt=evaluate(u+eps*direction);minus,mt=evaluate(u-eps*direction);fd=(plus-minus)/(2*eps)
  checks.append(dict(direction=i,epsilon=eps,adjoint=ad,native_finite_difference=fd,relative_error=abs(ad-fd)/max(abs(ad),abs(fd),1e-20),changed_topology_steps=sum(x!=a or x!=b for x,a,b in zip(topology,pt,mt))))
report={'steps':len(u),'baseline_loss':base,'checks':checks,'purpose':'Diagnose gradient mismatch; does not waive the training gate'}
(R/'direction-refinement-200.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
