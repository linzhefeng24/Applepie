"""Independent full1400ms surrogate-adjoint smoke check, with zero optimizer updates.
This checks differentiation plumbing, not finite-difference truth for hard spikes.
"""
from pathlib import Path
import hashlib,json,time
import numpy as np
import jax
jax.config.update('jax_enable_x64',True)
import jax.numpy as j
from full_hh import FullDifferentiableHH
R=Path(__file__).resolve().parent
jax.config.update('jax_compilation_cache_dir',str(R/'cache/jax-neural'));jax.config.update('jax_persistent_cache_min_compile_time_secs',0)
model=FullDifferentiableHH();raw=j.zeros((model.n_groups,len(model.cfg['train_fields'])))
def objective(x):
 u,_=model.forward(x,end_ms=1400)
 return j.mean(u[200:]**2)
print('Full1400ms neural surrogate VJP, no parameter updates',flush=True);start=time.monotonic();value,gradient=jax.jit(jax.value_and_grad(objective))(raw);value.block_until_ready();g=np.asarray(gradient)
report={'neural_ms':1400,'cells':len(model.model.ids),'edges':len(model.model.weight),'parameter_anchor':'manual raw0','completed_optimizer_updates':0,'test_objective':'mean neural u squared; plumbing check only, not training objective','test_value':float(value),'gradient_norm':float(np.linalg.norm(g)),'all_gradients_finite':bool(np.isfinite(g).all()),'nonzero_shared_groups':int(np.count_nonzero(np.linalg.norm(g,axis=1))),'seconds':time.monotonic()-start,'full_hh_sha256':hashlib.sha256((R/'full_hh.py').read_bytes()).hexdigest(),'neural_config_sha256':hashlib.sha256((R/'neural-config.json').read_bytes()).hexdigest()}
(R/'neural-adjoint-1400ms.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));assert report['all_gradients_finite'] and report['gradient_norm']>0
