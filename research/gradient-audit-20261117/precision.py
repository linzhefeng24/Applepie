"""Reuse cached physical VJP and shrink native perturbations without retraining."""
from pathlib import Path
import sys,json,time
import numpy as np
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R.parents[1]/'research/joint-bptt-physical-bounds-20261117'))
from physics import ABPhysics
from native_whitebox import NativeWhitebox
with np.load(R/'cache-physics-gradient.npz') as z:u=z['u'];g=z['gradient']
p=ABPhysics(json.loads((R.parent/'joint-bptt-physical-bounds-20261117/config.json').read_text()));b=NativeWhitebox(p);initial=tuple(np.asarray(x) for x in p.initial);ids=np.asarray(p.joint_ids);target=np.asarray(p.target)
def value(control):
 state=initial;loss=0.
 for k,row in enumerate(control):state=b.native_step_numpy(state,k,row)[:4];loss+=np.sum((state[0][ids]-target[k])**2)/target.size
 return float(loss)
rng=np.random.default_rng(42);mask=(u>.02)&(u<.98);directions=[('random0',rng.normal(size=u.shape)*mask),('random1',rng.normal(size=u.shape)*mask),('negative_gradient',-g*mask)];out={'scope':'full400ms native physical loss; same cached VJP and directions as physics.json; smaller perturbations','checks':[]};start=time.monotonic()
for name,d in directions:
 d/=max(abs(d).max(),1e-30);ad=float(np.sum(g*d))
 for eps in [1e-7,1e-6,3e-6]:
  plus=value(u+eps*d);minus=value(u-eps*d);fd=(plus-minus)/(2*eps);row={'direction':name,'epsilon':eps,'adjoint_projection':ad,'native_central_difference':fd,'relative_error':abs(ad-fd)/max(abs(ad),abs(fd),1e-20),'loss_plus':plus,'loss_minus':minus};out['checks'].append(row);print(json.dumps(row),flush=True);(R/'physics-precision-incomplete.json').write_text(json.dumps(out,indent=2)+'\n')
out['seconds']=time.monotonic()-start;(R/'physics-precision.json').write_text(json.dumps(out,indent=2)+'\n');(R/'physics-precision-incomplete.json').unlink()
