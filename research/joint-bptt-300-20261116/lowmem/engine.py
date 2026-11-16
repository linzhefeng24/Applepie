"""Chain-rule stage bridge: same scalar objective/gradient, disjoint worker heaps.

Neural state-clip and existing200ms truncation stay exactly where the original
code placed them. No new stop-gradient, short horizon or lower precision is
introduced. Only raw207 factors and small u/cotangent arrays cross processes.
"""
from pathlib import Path
import json,resource,subprocess,sys,time
import numpy as np
import jax
import jax.numpy as j
from training_context import R
HERE=Path(__file__).resolve().parent

class Engine:
 def __init__(self,ctx):
  self.ctx=ctx;self.spool=R/'cache/lowmem-spool';self.spool.mkdir(parents=True,exist_ok=True)
 def evaluate(self,raw,coefficient,gradient):
  started=time.monotonic();np.savez_compressed(self.spool/'input.npz',raw=np.asarray(raw));stages=[]
  for stage in ['forward','physics']+(['backward'] if gradient else []):
   command=[sys.executable,str(HERE/'worker.py'),'--work',str(R),'--spool',str(self.spool),'--stage',stage,'--neural-ms',str(self.ctx.cfg['neural_end_ms']),'--physical-steps',str(len(self.ctx.physics.clock_indices))]
   if gradient:command.append('--gradient')
   print('LOW_MEMORY_START '+stage,flush=True)
   subprocess.run(command,check=True);stages.append(json.loads((self.spool/(stage+'-report.json')).read_text()))
  with np.load(self.spool/'physics.npz',allow_pickle=False) as z:
   qloss=j.asarray(z['joint_loss']);aux={k:j.asarray(z[k]) for k in z.files if k not in ['joint_loss','cotangent']}
  ctx=self.ctx
  def penalty(x):return coefficient*j.mean(ctx.fractional_shift(x)**2)
  reg,greg=jax.value_and_grad(penalty)(raw);shift=ctx.fractional_shift(raw)
  aux.update(joint_loss=qloss,regularization=reg,max_fractional_drift=j.max(j.abs(shift)),rms_fractional_drift=j.sqrt(j.mean(shift**2)))
  parent=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
  report={'seconds':time.monotonic()-started,'stages':stages,'parent_peak_rss_kib':parent,'conservative_parent_plus_largest_worker_peak_kib':parent+max(s['peak_rss_kib'] for s in stages),'physical_steps':len(ctx.physics.clock_indices),'neural_ms':ctx.cfg['neural_end_ms'],'gradient_computed':gradient,'new_temporal_gradient_truncation':False,'precision_changed':False,'model_or_loss_changed':False}
  out=R/'cache/train';out.mkdir(parents=True,exist_ok=True);(out/'low-memory-last.json').write_text(json.dumps(report,indent=2)+'\n')
  print('LOW_MEMORY_EVALUATION '+json.dumps(report),flush=True)
  if gradient:
   with np.load(self.spool/'gradient.npz',allow_pickle=False) as z:g=j.asarray(z['gradient'])
   return (qloss+reg,aux),g+greg
  return qloss+reg,aux
 def value_grad(self,raw,coefficient):return self.evaluate(raw,coefficient,True)
 def value_only(self,raw,coefficient):return self.evaluate(raw,coefficient,False)
