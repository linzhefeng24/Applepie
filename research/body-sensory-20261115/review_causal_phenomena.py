"""Review full traces and intervention pairs; no pooled loss or automatic ranking."""
from pathlib import Path
import json,hashlib
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).parent;N=R.parent/'conductance-rebuild-20261114';ids=[100513,13157,14517,165560,12443,12804];legs=['LF','LM','LH','RF','RM','RH'];fig,axs=plt.subplots(6,3,figsize=(14,14),sharex=True)
for case in ['motor','motor_web']:
 z=np.load(N/'results/sensory-command-probes/r6'/(case+'.npz'));t=z['time_ms'];print(case,{k:z[k].shape for k in z.files})
 for i,(leg,b) in enumerate(zip(legs,ids)):
  j=list(map(str,z['body_ids'])).index(str(b));axs[i,0].plot(t,z['voltage'][:,j,0],lw=.6,label=case);axs[i,1].plot(t,z['voltage'][:,j,1],lw=.6,label=case);rate=np.convolve(z['spikes'][:,j],np.ones(50)/.05,mode='same');axs[i,2].plot(np.arange(len(rate)),rate,label=case);axs[i,0].set_ylabel(leg)
for a,title in zip(axs[0],['Chief soma voltage (mV)','Chief axon voltage (mV)','Chief rate (50ms smoothing, Hz)']):a.set_title(title)
for a in axs.flat:a.grid(alpha=.2)
for a in axs[-1]:a.set_xlabel('Time (ms)')
axs[0,0].legend();fig.tight_layout();fig.savefig(R/'results/chief-r6-full-traces.png',dpi=150)
rows=[]
for case in ['passive','motor','motor_web','motor_chief_off']:
 p=R/'results/A-ground'/(case+'-r6-position-r3')/'manifest.json';d=json.load(open(p));row={'condition':case,'legs':[]}
 for leg in legs:
  z=np.load(p.parent/(leg+'.npz'));row['legs'].append({'leg':leg,'hook_terminal_spikes_200_400ms':z['spikes'][200:400,:2,2].sum(0).tolist(),'position_terminal_spikes_200_400ms':z['spikes'][200:400,2:,2].sum(0).tolist(),'load_touch_terminal_spikes_200_400ms':z['load_spikes'][200:400,:,2].sum(0).tolist()})
 rows.append(row)
fig,axs=plt.subplots(6,3,figsize=(14,14),sharex=True)
for i,leg in enumerate(legs):
 for case in ['passive','motor','motor_web','motor_chief_off']:
  z=np.load(R/'results/A-ground'/(case+'-r6-position-r3')/(leg+'.npz'));t=z['time_ms'];axs[i,0].plot(t,z['calcium'][:,:2,2].sum(1),label=case);axs[i,1].plot(t,z['calcium'][:,2:,2].sum(1));axs[i,2].plot(t,z['load_calcium'][:,0,2]);axs[i,0].set_ylabel(leg)
for a,title in zip(axs[0],['Hook terminal total Ca (uM)','Position terminal total Ca (uM)','Load terminal Ca (uM)']):a.set_title(title)
for a in axs.flat:a.grid(alpha=.2)
for a in axs[-1]:a.set_xlabel('Time (ms)')
axs[0,0].legend(fontsize=7);fig.tight_layout();fig.savefig(R/'results/body-chief-causal-traces-position-r3.png',dpi=150)
(R/'results/causal-phenomena-review-position-r3.json').write_text(json.dumps({'status':'descriptive model interventions, not all biological phenomena verified','interval_ms':[200,400],'caveat':'only last200ms of body replay overlaps chief command; no repeating/warping body motion','conditions':rows},indent=2)+'\n');print(rows)
