"""Check checkpoint nesting against the original scan, including tails/adjoints."""
from pathlib import Path
import json
import numpy as np
import jax
jax.config.update('jax_enable_x64',True)
import jax.numpy as j
from layout import nested_scan
@jax.custom_vjp
def clip_adjoint(x):return x
def cf(x):return x,None
def cb(res,g):return (j.clip(g,-.7,.7),)
clip_adjoint.defvjp(cf,cb)
def step_factory(p):
 def step(state,k):
  state=j.tanh(state*p+j.sin(k*.03));state=j.where((k+1)%17==0,jax.lax.stop_gradient(state),state);state=clip_adjoint(state)
  return state,state**2
 return step
rows=[]
for length in [1,19,20,37,200]:
 xs=j.arange(length);init=j.ones(3)*.1
 def objective(p,blocked):
  step=step_factory(p);state,out=nested_scan(step,init,xs,20) if blocked else jax.lax.scan(jax.checkpoint(step),init,xs)
  return j.sum(out)+j.sum(state)
 av,ag=jax.jit(jax.value_and_grad(lambda p:objective(p,False)))(j.array([.4,.5,.6]))
 bv,bg=jax.jit(jax.value_and_grad(lambda p:objective(p,True)))(j.array([.4,.5,.6]))
 error=float(abs(np.asarray(ag-bg)).max());assert np.allclose(av,bv,rtol=1e-13,atol=1e-13) and error<1e-12
 rows.append({'steps':length,'max_gradient_abs_error':error,'loss_abs_error':float(abs(av-bv))})
report={'passed':True,'cases':rows,'scope':'Nested storage and adjoint algebra only; not a full-network/physics validation'}
(Path(__file__).parent/'layout-check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
