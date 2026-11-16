"""Verify complete AB forward identity, including carried warmstart and auxiliaries."""
from pathlib import Path
import hashlib,json,time
import numpy as np
from physics import ABPhysics
from native_whitebox import NativeWhitebox
R=Path(__file__).resolve().parent
p=ABPhysics(json.loads((R/'config.json').read_text()));body=NativeWhitebox(p)
report={'cases':{},'source_sha256':{n:hashlib.sha256((R/n).read_bytes()).hexdigest() for n in ['physics.py','native_whitebox.py']}}
for case in ['A','B']:
 start=time.monotonic();reference=p.native.replay_ab(case);reference_warmstart=p.native.data.qacc_warmstart.copy();bank=p.native.load_ab(case);p.native.reset(case)
 state=tuple(np.asarray(x).copy() for x in [p.native.data.qpos,p.native.data.qvel,p.native.data.act,p.native.data.qacc_warmstart])
 assert np.array_equal(bank['controls'][:,p.native.nonmuscle_indices],body.controls[:,p.native.nonmuscle_indices])
 errors=dict(qpos=0.,qvel=0.,activation=0.);counts=np.zeros(len(body.dims),dtype=int);row=0
 for k,u in enumerate(bank['controls'][:,body.indices]):
  result=body.native_step_numpy(state,k,u);state=result[:4];counts=np.maximum(counts,result[4])
  if (k+1)%bank['sample_stride']==0:
   for name,value,target in zip(errors,state[:3],[reference['qpos'][row],reference['qvel'][row],reference['all_activation'][row]]):errors[name]=max(errors[name],float(abs(value-target).max()))
   row+=1
 errors['final_warmstart']=float(abs(state[3]-reference_warmstart).max())
 report['cases'][case]={'max_abs_errors':errors,'steps':len(bank['controls']),'max_contacts_by_condim':counts.tolist(),'seconds':time.monotonic()-start,'archived_native_metrics':reference['metrics']}
 assert max(errors.values())==0,errors
report['passed']=True
(R/'native-forward-identity.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
