"""Locate nonfinite derivatives by physical equation stage."""
from pathlib import Path
import json,time
import numpy as np
import jax
jax.config.update('jax_enable_x64',True)
import jax.numpy as j
from mujoco.mjx._src import forward
from physics import ABPhysics
from native_whitebox import NativeWhitebox
R=Path(__file__).resolve().parent;jax.config.update('jax_compilation_cache_dir',str(R/'cache/jax-whitebox'))
p=ABPhysics(json.loads((R/'config.json').read_text()));b=NativeWhitebox(p);s=p.initial;u=.1+.8*p.controls[0,p.muscles];actual=b.native_step_numpy(tuple(np.asarray(x) for x in s),0,np.asarray(u));qa=j.asarray(actual[3]);contacts=j.asarray(actual[5]);geoms=j.asarray(actual[6])
def equations(state,u):
 d=b.whitebox_data(state,0,u,qa,contacts,geoms);e=forward.euler(p.m,d)
 return d.act_dot,d.qfrc_actuator,d.qfrc_passive,d.qacc,e.qpos[p.joint_ids]
rng=np.random.default_rng(42);tangent=tuple(j.asarray(rng.normal(size=x.shape)) for x in s);tu=j.asarray(rng.normal(size=u.shape))
print('compile stage JVP',flush=True);a=time.time();primal,tangent_out=jax.jit(lambda state,u,t,tu:jax.jvp(equations,(state,u),(t,tu)))(s,u,tangent,tu);jax.block_until_ready(tangent_out)
rows=[{'field':name,'finite':bool(np.isfinite(t).all()),'nan_count':int(np.isnan(t).sum()),'max_abs':float(j.max(j.abs(t)))} for name,t in zip(['activation_derivative','actuator_force','passive_force','constrained_acceleration','next_leg_angles'],tangent_out)]
report={'seconds':time.time()-a,'stages':rows};(R/'step-jvp-report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2),flush=True)
