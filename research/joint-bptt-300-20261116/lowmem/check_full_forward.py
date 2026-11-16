"""Verify all1400ms u and all3988-cell spike bins after nested scan layout."""
from pathlib import Path
import argparse,json,sys,time
import numpy as np
import jax
jax.config.update('jax_enable_x64',True)
p=argparse.ArgumentParser();p.add_argument('--work',type=Path,required=True);p.add_argument('--reference',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();sys.path.insert(0,str(a.work.resolve()))
from training_context import JointContext
from layout import attach
ctx=JointContext();layout=attach(ctx.neural,a.work);start=time.monotonic();u,spikes=jax.jit(lambda x:ctx.neural.forward(x,end_ms=1400))(ctx.reference);u.block_until_ready()
with np.load(a.reference,allow_pickle=False) as z:old_u=z['u'];old_spikes=z['spikes']
report={'neural_ms':1400,'cells':3988,'u_exact':bool(np.array_equal(np.asarray(u),old_u)),'spike_bins_exact':bool(np.array_equal(np.asarray(spikes),old_spikes)),'max_u_abs_difference':float(abs(np.asarray(u)-old_u).max()),'spike_mismatch_bins':int(np.count_nonzero(np.asarray(spikes)!=old_spikes)),'seconds':time.monotonic()-start,'layout':layout,'optimizer_updates':0}
a.out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));assert report['u_exact'] and report['spike_bins_exact']
