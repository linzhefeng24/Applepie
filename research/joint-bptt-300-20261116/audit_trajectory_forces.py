"""Find the first physical-stage discrepancy along the failing directional test."""
from pathlib import Path
import json
import numpy as np
import jax
jax.config.update('jax_enable_x64',True)
import jax.numpy as j
from physics import ABPhysics
from native_whitebox import NativeWhitebox
R=Path(__file__).resolve().parent
jax.config.update('jax_compilation_cache_dir',str(R/'cache/jax-whitebox'));jax.config.update('jax_persistent_cache_min_compile_time_secs',0)
p=ABPhysics(json.loads((R/'config.json').read_text()));body=NativeWhitebox(p)
keys=['actuator_force','qfrc_actuator','qfrc_passive','qfrc_bias','qfrc_constraint','qacc','qacc_warmstart']
@jax.jit
def forces(state,k,u,acc,contacts,geoms):
 d=body.whitebox_data(state,k,u,acc,contacts,geoms)
 return tuple(getattr(d,key) for key in keys)
state=tuple(np.asarray(x) for x in p.initial);u=.1+.8*np.asarray(p.controls[:200,p.muscles]);rows=[]
for k,row in enumerate(u):
 result=body.native_step_numpy(state,k,row)
 if k in [0,9,19,49,99,149,199]:
  fields=forces(state,k,j.asarray(row),j.asarray(result[3]),j.asarray(result[5]),j.asarray(result[6]));jax.block_until_ready(fields)
  error={key:float(abs(np.asarray(x)-getattr(body.data,key)).max()) for key,x in zip(keys,fields)}
  rows.append({'step':k,'errors':error,'contacts':int(body.data.ncon),'solver_iterations':int(body.data.solver_niter[0])});print(rows[-1],flush=True)
 state=result[:4]
(R/'trajectory-force-audit.json').write_text(json.dumps(rows,indent=2)+'\n')
