"""At least1000 real Adam updates, resumable exact optimizer states, no early stop.
Each update uses the complete declared training interval; no minibatch count is
misrepresented as an epoch. Training-only prefix saves work on unused future
holdout states without changing the causal training loss or its gradient.
"""
from pathlib import Path
import os,json,time,math,hashlib,argparse,platform,subprocess
import numpy as np
import jax
import jax.numpy as j
from jax_hh import DifferentiableHH
R=Path(__file__).resolve().parent;OUT=R/'cache/longrun';OUT.mkdir(parents=True,exist_ok=True)
p=argparse.ArgumentParser();p.add_argument('--chunk-updates',type=int,default=50);a=p.parse_args()
ctx=DifferentiableHH();cfg=ctx.cfg;minimum=int(cfg['minimum_epochs']);assert minimum>=1000
prefix=int(cfg['training_prefix_end_ms']);target=ctx.target[:prefix];mask=ctx.train_mask[:prefix,None]&ctx.mapped[None,:]
def objective(raw):
 u,_=ctx.forward(raw,end_ms=prefix);_,delta=ctx.parameters(raw)
 mse=j.sum(j.where(mask,(u-target)**2,0.))/j.sum(mask);reg=cfg['regularization_lambda']*j.mean(delta**2)
 return mse+reg,(mse,reg)
vg=jax.jit(jax.value_and_grad(objective,has_aux=True));eval_full=jax.jit(ctx.forward)
state_path=OUT/'latest-optimizer.npz';history_path=OUT/'history.json'
if state_path.exists():
 with np.load(state_path,allow_pickle=False) as z:
  raw=j.asarray(z['raw']);mt=j.asarray(z['adam_m']);vt=j.asarray(z['adam_v']);completed=int(z['completed_updates']);best_raw=np.array(z['best_raw']);best=float(z['best_objective']);best_step=int(z['best_step'])
 history=json.loads(history_path.read_text())
else:
 with np.load(R/cfg['warm_start'],allow_pickle=False) as z:raw=j.asarray(z['raw'])
 mt=j.zeros_like(raw);vt=j.zeros_like(raw);completed=0;best_raw=np.asarray(raw);best=float('inf');best_step=0;history=[]
assert raw.shape==(ctx.n_groups,len(cfg['train_fields']))
assert 1<=a.chunk_updates<=cfg['chunk_updates']
stop=min(minimum,completed+a.chunk_updates)
def atomic_json(path,value):
 tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(value,indent=2)+'\n');tmp.replace(path)
def save():
 with (OUT/'latest.tmp').open('wb') as f:np.savez_compressed(f,raw=np.asarray(raw),adam_m=np.asarray(mt),adam_v=np.asarray(vt),completed_updates=completed,best_raw=best_raw,best_objective=best,best_step=best_step)
 (OUT/'latest.tmp').replace(state_path)
 np.savez_compressed(OUT/'best-parameters.npz',raw=best_raw,relative_factors=cfg['relative_bound']*np.tanh(best_raw),epoch=best_step)
 atomic_json(history_path,history)
# Every resumed process checks the immutable baseline on its actual CPU/JAX build.
z=j.zeros_like(raw);_,sp=eval_full(z);sp.block_until_ready();assert np.array_equal(np.asarray(sp),ctx.data['baseline_spikes'])
atomic_json(OUT/'forward-check.json',{'baseline_spikes_identical':True,'checked_on_chunk_start':completed,'full_baseline_ms':ctx.duration,'training_prefix_ms':prefix})
def snapshot():
 u,sp=eval_full(j.asarray(best_raw));u.block_until_ready();u=np.asarray(u)
 train=np.asarray(ctx.train_mask);test=np.asarray(ctx.test_mask);mapped=ctx.data['mapped']
 report={'completed_updates':completed,'minimum_updates':minimum,'complete':completed>=minimum,'best_training_step':best_step,'best_training_objective':best,'best_train_mse':float(np.mean((u[train][:,mapped]-ctx.data['target'][train][:,mapped])**2)),'best_holdout_mse':float(np.mean((u[test][:,mapped]-ctx.data['target'][test][:,mapped])**2)),'best_max_relative_shift':float(np.max(abs(cfg['relative_bound']*np.tanh(best_raw)))),'baseline_model_sha256':ctx.model.sha256,'epoch_definition':cfg['epoch_definition'],'warm_start':cfg['warm_start'],'warm_start_sha256':hashlib.sha256((R/cfg['warm_start']).read_bytes()).hexdigest(),'optimizer_state_resumed':completed>a.chunk_updates,'python':platform.python_version(),'source_revision':os.environ.get('TRAIN_SOURCE_REF',subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()),'software':{k:__import__('importlib.metadata',fromlist=['version']).version(k) for k in ['jax','jaxlib','numpy','numba','scipy']},'method':'local surrogate-gradient BPTT; final full hard-network validation is separate; no early stopping before1000'}
 np.savez_compressed(OUT/'best-local-fit.npz',u=u,target=ctx.data['target'],mapped=mapped)
 atomic_json(OUT/'chunk-report.json',report);atomic_json(OUT/'run-config.json',cfg)
 return report
print('Starting',completed,'target',minimum,'this_chunk_end',stop,flush=True)
while completed<=stop:
 start=time.perf_counter();(value,aux),grad=vg(raw);value.block_until_ready();g=np.asarray(grad)
 if not np.isfinite(g).all():
  save();atomic_json(OUT/'failure.json',{'completed_updates':completed,'reason':'nonfinite gradient; update not counted'});raise FloatingPointError('Nonfinite gradient; no invented epochs')
 mse,reg=map(float,aux);d=cfg['relative_bound']*np.tanh(np.asarray(raw));norm=float(np.linalg.norm(g/max(1.,float(np.max(abs(g)))))*max(1.,float(np.max(abs(g)))))
 row={'parameters_after_updates':completed,'train_mse':mse,'regularization':reg,'objective':float(value),'max_relative_shift':float(np.max(abs(d))),'gradient_norm':norm,'seconds':time.perf_counter()-start}
 if value<best:best=float(value);best_raw=np.array(raw);best_step=completed
 if history and history[-1]['parameters_after_updates']==completed:history[-1]=row
 else:history.append(row)
 print(json.dumps(row),flush=True);save()
 if completed and completed%cfg['durable_checkpoint_every']==0 and completed<stop and os.environ.get('GITHUB_ACTIONS')=='true':
  snapshot();subprocess.run([__import__('sys').executable,str(R/'checkpoint_service.py'),'publish'],check=True)
 if completed==stop:break
 grad=grad*j.minimum(1.,cfg['gradient_clip_norm']/j.maximum(norm,1e-30))
 mt=.9*mt+.1*grad;vt=.999*vt+.001*grad*grad
 frac=completed/minimum;floor=cfg['learning_rate_floor_fraction'];lr=cfg['learning_rate']*(floor+(1-floor)*.5*(1+math.cos(math.pi*frac)))
 raw=raw-lr*(mt/(1-.9**(completed+1)))/(j.sqrt(vt/(1-.999**(completed+1)))+1e-8)
 completed+=1;save()
# Holdout is evaluated for reporting only, never checkpoint selection.
report=snapshot();print(json.dumps(report,indent=2),flush=True)
