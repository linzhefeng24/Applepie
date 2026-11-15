"""Collate human-reviewed mechanisms; no loss, threshold-based pass or ranking."""
from pathlib import Path
import json,sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).parent;tag=sys.argv[1] if len(sys.argv)>1 else 'r4';O=R/'results'/('frozen-neural-panel-'+tag)
rows=[]
for f in sorted(O.glob('*-diagnosis.json')):
 d=json.loads(f.read_text());rows.append({'condition':d['condition'],'bank_sha256':d['bank_sha256'],'numerical_failure':d['numerical_failure'],'elapsed_s':d['elapsed_s'],'cells':d['cells']})
(O/'observations.json').write_text(json.dumps({'method':'descriptive full-protocol data for manual review; no automatic score or pass classification','conditions':rows},indent=2)+'\n')
panels=[('DNg100',['BPN','BPN+FG','BPN+BB','BPN+BRK']),('DNg97',['P9','P9+FG','P9+BB']),('DNa02',['P9','P9+FG','P9+BB']),('LBL40',['MDN','MDN+FG','MDN+BB','MDN+BRK'])];fig,axs=plt.subplots(2,2,figsize=(12,7))
for ax,(target,cases) in zip(axs.flat,panels):
 for case in cases:
  path=O/(case+'.npz')
  if not path.exists():continue
  cfg=json.load(open(O/(case+'-config.json')));B=R/cfg.get('graph_directory','results/mcns-command-v2');meta=json.load(open(B/'neurons.json'));ids=[i for i,x in enumerate(meta) if x['type']==target];d=np.load(path);sp=d['spikes'][:,ids].mean(axis=1);rate=np.convolve(sp,np.ones(50)/.05,mode='same');ax.plot(np.arange(len(rate)),rate,lw=1,label=case)
 ax.axvspan(450,950,color='orange',alpha=.12);ax.axvline(200,color='gray',ls=':');ax.set(title=target,xlabel='Time (ms)',ylabel='Mean firing, 50 ms smoothing (Hz)',xlim=(0,1600));ax.legend(fontsize=7);ax.grid(alpha=.15)
fig.suptitle(tag+': fixed hand-selected bank; orange = later halt input, no waveform fitting');fig.tight_layout();fig.savefig(O/'neural-overview.png',dpi=150);plt.close(fig);print(tag,'complete conditions',len(rows))
