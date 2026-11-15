"""Full-protocol opponent voltage traces from the shared r8 graph."""
from pathlib import Path
import json
import numpy as np
from scipy.ndimage import uniform_filter1d
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).parent;O=R/'results/frozen-neural-panel-unified-r8';meta={x['bodyId']:x for x in json.load(open(R/'results/mcns-unified/neurons.json'))};fig,axs=plt.subplots(2,2,figsize=(11,7))
for ax,case in zip(axs.flat,['PFL3L','PFL3R','PFL2','PFL3L+PFL2']):
 z=np.load(O/(case+'.npz'));tm=z['time_ms'];v=z['voltage'];cfg=json.load(open(O/(case+'-config.json')))
 for j,b in enumerate(z['record_body_ids']):
  if meta[b]['type']=='DNa02':ax.plot(tm,uniform_filter1d(v[:,j,0],size=10,mode='nearest'),lw=1,label=meta[b]['somaSide']+' DNa02')
 for p in cfg['protocol']:ax.axvspan(p['on_ms'],p['off_ms'],alpha=.07,color='orange' if p['population']=='PFL2' and len(cfg['protocol'])>1 else 'gray')
 ax.set(title=case,xlabel='Time (ms)',ylabel='Soma voltage (mV), 5ms display smoothing',xlim=(0,1600),ylim=(-85,-25));ax.legend(fontsize=8);ax.grid(alpha=.15)
fig.suptitle('Same unified graph and r8 physiology; only source stimulation changes');fig.tight_layout();fig.savefig(O/'steering-responses.png',dpi=150);plt.close(fig)
