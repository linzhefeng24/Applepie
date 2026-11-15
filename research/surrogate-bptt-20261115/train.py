"""Train only the declared shared relative factors, save every completed epoch."""
from pathlib import Path
import json,time,hashlib
import numpy as np
import jax
import jax.numpy as j
from jax_hh import DifferentiableHH
R=Path(__file__).resolve().parent
ctx=DifferentiableHH();cfg=ctx.cfg
forward=jax.jit(ctx.forward);vg=jax.jit(jax.value_and_grad(ctx.loss,has_aux=True))
raw=j.zeros((ctx.n_groups,len(cfg['train_fields'])));start=time.perf_counter()
print('Checking exact hard-spike local forward at baseline',flush=True)
u,sp=forward(raw);u.block_until_ready();sp=np.asarray(sp);reference=ctx.data['baseline_spikes']
check={'spikes_identical_to_full_baseline':bool(np.array_equal(sp,reference)),'mismatched_ms_cell_bins':int(np.count_nonzero(sp!=reference)),'forward_s':time.perf_counter()-start,'model_scope':cfg['scope']}
(R/'forward-check.json').write_text(json.dumps(check,indent=2)+'\n');print(json.dumps(check),flush=True)
if not check['spikes_identical_to_full_baseline']:
 raise RuntimeError('Local boundary forward differs from baseline; do not fit until resolved')
mt=j.zeros_like(raw);vt=j.zeros_like(raw);best=float('inf');history=[]
for epoch in range(cfg['epochs']+1):
 start=time.perf_counter();(value,aux),grad=vg(raw);value.block_until_ready();g=np.asarray(grad)
 if not np.isfinite(g).all():
  (R/'training-failure.json').write_text(json.dumps({'epoch':epoch,'reason':'nonfinite surrogate BPTT gradient','finite_forward_loss':float(value)},indent=2)+'\n');raise FloatingPointError('Nonfinite gradient')
 tr,te,reg=map(float,aux);scale=max(1.,float(np.max(abs(g))));norm=float(np.linalg.norm(g/scale)*scale)
 row={'epoch':epoch,'train_mse':tr,'holdout_mse':te,'regularization':reg,'objective':float(value),'gradient_norm':norm,'max_relative_shift':float(np.max(abs(cfg['relative_bound']*np.tanh(np.asarray(raw))))),'seconds':time.perf_counter()-start}
 history.append(row);(R/'training-history.json').write_text(json.dumps(history,indent=2)+'\n');print(json.dumps(row),flush=True)
 if float(value)<best:
  best=float(value);np.savez_compressed(R/'best-parameters.npz',raw=np.asarray(raw),relative_factors=cfg['relative_bound']*np.tanh(np.asarray(raw)),epoch=epoch)
 if epoch==cfg['epochs']:break
 grad=grad*j.minimum(1.,cfg['gradient_clip_norm']/j.maximum(j.asarray(norm),1e-30))
 mt=.9*mt+.1*grad;vt=.999*vt+.001*grad*grad
 raw=raw-cfg['learning_rate']*(mt/(1-.9**(epoch+1)))/(j.sqrt(vt/(1-.999**(epoch+1)))+1e-8)
with np.load(R/'best-parameters.npz') as z:best_raw=j.asarray(z['raw']);epoch=int(z['epoch'])
best_u,best_sp=forward(best_raw);best_u.block_until_ready()
np.savez_compressed(R/'local-fit.npz',predicted_u=np.asarray(best_u),target_u=ctx.data['target'],local_spikes=np.asarray(best_sp),baseline_local_spikes=reference,mapped=ctx.data['mapped'],muscle_ids=[x['muscle_id'] for x in ctx.model.mapping])
print('Selected training epoch',epoch,flush=True)
