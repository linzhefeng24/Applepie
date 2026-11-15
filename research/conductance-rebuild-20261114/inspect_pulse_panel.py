"""Draw complete measured states for human inspection; never rank parameters."""
from pathlib import Path
import json,sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).parent;O=R/'results'/('frozen-neural-panel-'+(sys.argv[2] if len(sys.argv)>2 else 'r4'));mode=sys.argv[1];d=np.load(O/(mode+'.npz'));cfg=json.load(open(O/(mode+'-config.json')));meta={x['bodyId']:x for x in json.load(open(R/cfg.get('graph_directory','results/mcns-command-v2')/'neurons.json'))};ids=list(d['body_ids']);rec=list(d['record_body_ids']);t=d['time_ms'];types=['DNp09','DNg100','DNg97','DNa02','LBL40','INXXX468','IN27X001'];types=[ty for ty in types if any(meta[b]['type']==ty for b in rec)];fig,axs=plt.subplots(len(types),3,figsize=(15,2.3*len(types)),squeeze=False)
for row,ty in enumerate(types):
 for b in rec:
  m=meta[b]
  if m['type']!=ty:continue
  j=rec.index(b);i=ids.index(b);sp=d['spikes'][:,i];rate=np.convolve(sp,np.ones(25)/.025,mode='same');label=str(b)+' '+str(m.get('somaSide',''))+' '+str(m.get('somaNeuromere',''))
  axs[row,0].plot(np.arange(len(rate)),rate,lw=.8,label=label);axs[row,1].plot(t,d['voltage'][:,j,0],lw=.6);axs[row,2].plot(t,d['currents_pA'][:,j,0],lw=.65);axs[row,2].plot(t,d['currents_pA'][:,j,1],lw=.65,ls='--')
 axs[row,0].set_ylabel(ty);axs[row,0].legend(fontsize=5,ncol=2)
 for ax in axs[row]:
  for p in cfg['protocol']:ax.axvspan(p['on_ms'],p['off_ms'],alpha=.08,color='orange' if p['population'] in ['FG','BB','BRK'] else 'blue')
  ax.set_xlim(0,cfg['parameters']['duration_ms']);ax.grid(alpha=.15)
for ax,title in zip(axs[0],['25 ms smoothed firing (Hz)','Soma potential (mV)','Excitation / inhibition (pA)']):ax.set_title(title)
for ax in axs[-1]:ax.set_xlabel('Time (ms)')
fig.suptitle(mode+' | fixed hand-selected bank | full pulse and recovery');fig.tight_layout();fig.savefig(O/(mode+'-traces.png'),dpi=130);plt.close(fig)
print(O/(mode+'-traces.png'))
