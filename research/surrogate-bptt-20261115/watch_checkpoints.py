"""Keep each new best checkpoint while the training process is running."""
from pathlib import Path
import time,json,shutil,os
import numpy as np
R=Path(os.environ.get('BPTT_OUTPUT',str(Path(__file__).resolve().parent)));out=R/'checkpoints';out.mkdir(exist_ok=True)
while True:
 try:
  with np.load(R/'best-parameters.npz',allow_pickle=False) as z:epoch=int(z['epoch'])
  dest=out/f'best-epoch-{epoch:03d}.npz'
  if not dest.exists():
   shutil.copy2(R/'best-parameters.npz',dest)
   with np.load(dest,allow_pickle=False) as z:assert int(z['epoch'])==epoch
   print('Saved',dest.name,flush=True)
 except (OSError,ValueError,EOFError,KeyError):pass
 if (R/'local-fit.npz').exists() or (R/'training-failure.json').exists():break
 time.sleep(2)
