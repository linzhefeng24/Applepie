"""Check all-cell forward against the archived exact original network baseline."""
from pathlib import Path
import argparse,hashlib,json,time
import numpy as np
import jax
jax.config.update('jax_enable_x64',True)
import jax.numpy as j
from full_hh import FullDifferentiableHH
R=Path(__file__).resolve().parent;ROOT=R.parents[1]
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--ms',type=int,default=260);args=p.parse_args()
jax.config.update('jax_compilation_cache_dir',str(R/'cache/jax-neural'));jax.config.update('jax_persistent_cache_min_compile_time_secs',0)
ctx=FullDifferentiableHH();raw=j.zeros((ctx.n_groups,len(ctx.cfg['train_fields'])));start=time.monotonic();print('Full forward',args.ms,'ms','cells',len(ctx.model.ids),'edges',len(ctx.model.weight),flush=True)
u,sp=jax.jit(lambda x:ctx.forward(x,end_ms=args.ms))(raw);u.block_until_ready();sp=np.asarray(sp);path=ROOT/ctx.cfg['baseline_neural']
with np.load(path,allow_pickle=False) as z:ref=z['spikes'][:args.ms]
report={'physical_neural_model_sha256':ctx.model.sha256,'neural_ms':args.ms,'cells':len(ctx.model.ids),'edges':len(ctx.model.weight),'shared_variables':int(raw.size),'seconds':time.monotonic()-start,'spike_mismatch_bins':int(np.count_nonzero(sp!=ref)),'spikes_exactly_equal':bool(np.array_equal(sp,ref)),'u_finite':bool(np.isfinite(u).all()),'total_spikes':int(sp.sum()),'reference_spikes':int(ref.sum()),'source_sha256':hashlib.sha256((R/'full_hh.py').read_bytes()).hexdigest(),'versions':{'jax':jax.__version__,'numpy':np.__version__}}
(R/f'neural-forward-{args.ms}ms.json').write_text(json.dumps(report,indent=2)+'\n');np.savez_compressed(R/'cache'/f'neural-forward-{args.ms}ms.npz',u=np.asarray(u),spikes=sp.astype(np.int16));print(json.dumps(report,indent=2),flush=True)
assert report['spikes_exactly_equal'] and report['u_finite']
