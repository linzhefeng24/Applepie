"""Inspect sustained drive versus transient premotor/MN responses, not endpoints."""
from pathlib import Path
import json,numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).parent;N=R.parent/'conductance-rebuild-20261114';O=N/'results/frozen-neural-panel-brake-extension-r9';m=json.load(open(N/'results/mcns-brake-extension/neurons.json'));z=np.load(O/'BRK.npz');cfg=json.load(open(O/'BRK-config.json'));ids=list(map(str,z['body_ids']));source=[ids.index(b) for b in cfg['selected_body_ids']['BRK']];relay=np.load(R/'diagnostics/BRK-premotor-probes.npz');rids=list(relay['body_ids']);relay_ids=[rids.index(b) for b in ['800051','800053']];mn=[i for i,x in enumerate(m) if x['type']=='Ti extensor MN'];groups={'BRK_sources':(z['spikes'],source),'IN07B001_T1':(relay['spikes'],relay_ids),'Ti_extensor_MN':(z['spikes'],mn)};fig,axs=plt.subplots(3,1,figsize=(11,8),sharex=True);rows={}
for ax,(name,(sp,ii)) in zip(axs,groups.items()):
 rate=np.convolve(sp[:,ii].mean(1),np.ones(50)/.05,mode='same');ax.plot(np.arange(len(rate)),rate);ax.set_ylabel(name+' meanHz');ax.axvspan(200,1500,color='orange',alpha=.1);ax.grid(alpha=.2);rows[name]=[{'window_ms':[a,b],'mean_Hz':float(sp[a:b,ii].sum()/len(ii)/((b-a)/1000))} for a,b in [(200,450),(500,950),(1000,1450)]]
axs[-1].set_xlabel('Time(ms)');fig.suptitle('BRK input persists while selected premotor and MN output decays');fig.tight_layout();fig.savefig(R/'diagnostics/BRK-sustained-source-transient-output.png',dpi=150)
(R/'diagnostics/BRK-timecourse-review.json').write_text(json.dumps({'status':'post-hoc full-timecourse review of actual saved runs; no new integration','observations':rows,'interpretation':'BRK source does not stop. Selected relay excitation weakens and remains below firing threshold; overall inhibition also weakens, so pure stronger inhibition is not established. Missing sensory/state drive and uncalibrated intrinsic/synaptic properties remain competing explanations.'},indent=2)+'\n');print(rows)
