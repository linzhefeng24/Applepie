"""Inspect saved failed dose response: injected current→DN spiking→core timing.
No new simulations. ISIs describe individual trains, not proof of a population
rate oscillation or a causal channel mechanism. Original T1 configuration only.
"""
from pathlib import Path
import hashlib,json,numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).parent;N=R.parent/'conductance-rebuild-20261114';rows=[];fig,axs=plt.subplots(4,3,figsize=(14,10),sharex=True)
for row,(name,amp) in enumerate([('drive_120',120),('baseline',160),('drive_200',200),('drive_240',240)]):
 p=N/'results'/('adult-intact-'+name+'.npz');z=np.load(p);t=np.arange(len(z['voltage']))*.5;item={'current_pA':amp,'input_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'cells':[]}
 for col,(i,label) in enumerate([(0,'DNg100'),(1,'E1'),(3,'I1')]):
  sp=z['spikes'];ts=np.repeat(np.arange(400,1200),sp[400:1200,i]);isi=np.diff(ts);item['cells'].append({'body_id':str(z['body_ids'][i]),'label':label,'rate_400_1200_Hz':len(ts)/.8,'spike_times_ms':ts.tolist(),'ISI_ms':isi.tolist(),'median_ISI_ms':float(np.median(isi)) if len(isi) else None});axs[row,col].plot(t,z['voltage'][:,i,0],lw=.7);axs[row,col].set_xlim(400,1200);axs[row,col].set_title(str(amp)+'pA '+label);axs[row,col].grid(alpha=.2)
 rows.append(item)
fig.tight_layout();fig.savefig(R/'diagnostics/dose-transfer-core-traces.png',dpi=150);(R/'diagnostics/dose-transfer-review.json').write_text(json.dumps({'status':'new inspection of previously saved failed adult T1 dose series; not a fresh integration or current-brain validation','scope':'4604cell original T1 author graph, original adult-intact config','conditions':rows,'interpretation':'DN firing increases with current; E1/I1 output does not speed up, localizing failed monotonic transfer downstream of DN recruitment. Inhibitory recovery, adaptation and recruited parallel circuits are possible causes; old traces lack edge-resolved conductances, so no unique causal attribution.'},indent=2)+'\n');print([(x['current_pA'],[(y['label'],y['rate_400_1200_Hz'],y['median_ISI_ms']) for y in x['cells']]) for x in rows])
