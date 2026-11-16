"""Recover original pre-update gradient from the immutable FIRST Adam checkpoint.
First moments m=(1-beta1)*clip(g) start at0. Norm and clip scale were archived,
so this reconstruction is algebraic, not a newly simulated baseline result.
"""
from pathlib import Path
import argparse,hashlib,io,json,zipfile
import numpy as np
p=argparse.ArgumentParser();p.add_argument('archive',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
expected='f58fc4de05c2950297dcaa3d174a35e1e489d2af14063c91788d7c47d2ce3181';assert hashlib.sha256(a.archive.read_bytes()).hexdigest()==expected
with zipfile.ZipFile(a.archive) as archive:
 report=json.loads(archive.read('chunk-report.json'));cfg=json.loads(archive.read('config.json'))
 with np.load(io.BytesIO(archive.read('optimizer.npz')),allow_pickle=False) as z:
  assert int(z['pilot_index'])==0 and int(z['phase_updates'])==1 and int(z['completed_updates'])==0
  norm=report['last']['gradient_norm'];scale=min(1.,cfg['gradient_clip_norm']/max(norm,1e-30));gradient=z['adam_m']/(1-cfg['adam_beta1'])/scale
assert report['last']['regularization_before_update']==0
a.output.parent.mkdir(parents=True,exist_ok=True);np.savez_compressed(a.output,gradient=gradient,joint_loss=report['last']['joint_mse_before_update'],archive_sha256=np.array(expected))
print('Recovered archived first gradient norm',np.linalg.norm(gradient),'source',report['source_revision'])
