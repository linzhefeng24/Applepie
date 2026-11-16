"""One memory-bounded stage; exits to release its complete compiler/AD heap."""
from pathlib import Path
import argparse,hashlib,json,resource,sys,time
parser=argparse.ArgumentParser();parser.add_argument('--work',type=Path,required=True);parser.add_argument('--spool',type=Path,required=True);parser.add_argument('--stage',choices=['forward','physics','backward'],required=True);parser.add_argument('--gradient',action='store_true');parser.add_argument('--neural-ms',type=int,default=1400);parser.add_argument('--physical-steps',type=int,default=4000);args=parser.parse_args()
sys.path.insert(0,str(args.work.resolve()))
import numpy as np
import jax
jax.config.update('jax_enable_x64',True)
import jax.numpy as j
from training_context import JointContext
from layout import attach
start=time.monotonic();cache=args.work/'cache/lowmem-jax';jax.config.update('jax_compilation_cache_dir',str(cache));jax.config.update('jax_persistent_cache_min_compile_time_secs',0)
ctx=JointContext();spool=args.spool
ctx.cfg['neural_end_ms']=args.neural_ms;ctx.physics.clock_indices=ctx.physics.clock_indices[:args.physical_steps]
assert int(ctx.physics.clock_indices[-1])<args.neural_ms
with np.load(spool/'input.npz',allow_pickle=False) as z:raw=j.asarray(z['raw'])
report={'stage':args.stage,'raw_sha256':hashlib.sha256(np.asarray(raw).tobytes()).hexdigest(),'manual_model_sha256':ctx.cfg['anchor_model_sha256'],'precision':'float64','physical_steps':len(ctx.physics.clock_indices),'neural_ms':ctx.cfg['neural_end_ms']}
if args.stage=='forward':
 u=jax.jit(ctx.neural_u)(raw);u.block_until_ready();np.savez_compressed(spool/'forward.npz',u=np.asarray(u))
elif args.stage=='physics':
 with np.load(spool/'forward.npz',allow_pickle=False) as z:u=j.asarray(z['u'])
 def gather(x):return x[ctx.physics.clock_indices][:,ctx.order]
 control=gather(u)
 if args.gradient:
  (value,aux),du=jax.jit(jax.value_and_grad(ctx.native_physics.objective,has_aux=True))(control)
  # Same repeated-index accumulation as autodiff of the original u gather.
  cot=jax.jit(lambda x,g:jax.vjp(gather,x)[1](g)[0])(u,du)
 else:value,aux=jax.jit(ctx.native_physics.objective)(control);cot=j.zeros_like(u)
 value.block_until_ready();np.savez_compressed(spool/'physics.npz',joint_loss=np.asarray(value),cotangent=np.asarray(cot),**{k:np.asarray(v) for k,v in aux.items()})
 report.update(joint_loss=float(value),all_finite=bool(j.isfinite(value)&j.all(j.isfinite(cot))))
elif args.stage=='backward':
 report['layout']=attach(ctx.neural,args.work)
 with np.load(spool/'physics.npz',allow_pickle=False) as z:cot=j.asarray(z['cotangent'])
 gradient=jax.jit(lambda x,c:jax.vjp(ctx.neural_u,x)[1](c)[0])(raw,cot);gradient.block_until_ready();g=np.asarray(gradient);np.savez_compressed(spool/'gradient.npz',gradient=g)
 report.update(gradient_norm=float(np.linalg.norm(g)),all_finite=bool(np.isfinite(g).all()))
report.update(seconds=time.monotonic()-start,peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
(spool/(args.stage+'-report.json')).write_text(json.dumps(report,indent=2)+'\n');print('LOW_MEMORY_STAGE '+json.dumps(report),flush=True)
