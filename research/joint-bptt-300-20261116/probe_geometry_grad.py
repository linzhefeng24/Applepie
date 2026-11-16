"""Locate invalid active-feature geometry derivatives independently of forces."""
from pathlib import Path
import json,time
import numpy as np
import jax
jax.config.update('jax_enable_x64',True)
import jax.numpy as j
from mujoco.mjx._src import smooth
from physics import ABPhysics
from native_whitebox import NativeWhitebox
from contact_geometry import attach
R=Path(__file__).resolve().parent;jax.config.update('jax_compilation_cache_dir',str(R/'cache/jax-whitebox'));cfg=json.loads((R/'config.json').read_text());p=ABPhysics(cfg);b=NativeWhitebox(p);u=np.asarray(p.controls[0,p.muscles]);r=b.native_step_numpy(tuple(np.asarray(x) for x in p.initial),0,u)
d=jax.jit(smooth.kinematics)(p.m,p.template.replace(qpos=p.initial[0]));jax.block_until_ready(d);packed=j.asarray(r[5]);geoms=j.asarray(r[6]);valid=(packed[:,0]<1e5).astype(j.float64)
rows=[]
for field in ['dist','pos','frame']:
 def objective(position,rotation):
  result=attach(p.m,d.replace(geom_xpos=position,geom_xmat=rotation),packed,geoms);value=getattr(result.contact,field);mask=valid.reshape((len(valid),)+(1,)*(value.ndim-1));return j.sum(value*mask)
 a=time.time();v,g=jax.jit(jax.value_and_grad(objective,argnums=(0,1)))(d.geom_xpos,d.geom_xmat);jax.block_until_ready(g);row={'field':field,'finite':all(np.isfinite(x).all() for x in g),'gradient_norm':[float(j.linalg.norm(x)) for x in g],'seconds':time.time()-a};rows.append(row);print(json.dumps(row),flush=True)
(R/'geometry-gradient-report.json').write_text(json.dumps(rows,indent=2)+'\n')
