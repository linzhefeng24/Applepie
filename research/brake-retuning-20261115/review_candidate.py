"""Inspect full membrane/current/Ca traces, with descriptive stage windows."""
from pathlib import Path
import json,sys,hashlib,numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).parent;N=R.parent/'conductance-rebuild-20261114';tag=sys.argv[1];O=R/'results'/tag;z=np.load(O/'BRK.npz');base=np.load(R.parent/'gap-evidence-20261115/diagnostics/BRK-premotor-probes.npz');t=z['time_ms'];ids=list(z['record_body_ids']);bids=list(base['body_ids']);fig,axs=plt.subplots(2,3,figsize=(14,7),sharex=True);rows=[]
for row,b in enumerate(['800051','800053']):
 j=ids.index(b);k=bids.index(b);axs[row,0].plot(base['time_ms'],base['voltage'][:,k,0],label='previous soma',alpha=.7);axs[row,0].plot(t,z['voltage'][:,j,0],label='candidate soma',lw=.7);axs[row,0].plot(t,z['voltage'][:,j,1],label='candidate axon',lw=.5);axs[row,1].plot(t,z['conductances_nS'][:,j,0],label='gE');axs[row,1].plot(t,z['conductances_nS'][:,j,1],label='gI');axs[row,2].plot(t,z['calcium'][:,j]);axs[row,0].set_ylabel(b);s=(t>=1000)&(t<1450);i=list(z['body_ids']).index(b);rows.append({'body_id':b,'late_spikes':int(z['spikes'][1000:1450,i].sum()),'late_mean_Vs_Va_mV':z['voltage'][s,j].mean(0).tolist(),'late_max_Va_mV':float(z['voltage'][s,j,1].max()),'late_mean_gE_gI_nS':z['conductances_nS'][s,j].mean(0).tolist(),'late_mean_currents_exc_inh_coupling_external_pA':z['currents_pA'][s,j].mean(0).tolist()})
for a,title in zip(axs[0],['Membrane(mV)','Conductance(nS)','Intracellular Ca(uM)']):a.set_title(title)
for a in axs.flat:a.grid(alpha=.2);a.axvspan(200,1500,color='orange',alpha=.08)
for a in axs[:,0:2].flat:a.legend(fontsize=7)
for a in axs[-1]:a.set_xlabel('Time(ms)')
fig.suptitle(tag+': sustained BRK input, no imposed relay activity');fig.tight_layout();fig.savefig(O/'full-relay-review.png',dpi=150)
conditions=[]
for p in sorted(O.glob('*-diagnosis.json')):
 d=json.load(open(p));conditions.append({'case':d['case'],'numerical_failure':d['numerical_failure'],'control_equal':d['control_full_spike_array_identical_to_previous'],'IN07B001':[x for x in d['cells'] if x['type']=='IN07B001']})
(O/'review.json').write_text(json.dumps({'method':'manual full-trace review; no fitted score or automatic adoption','tag':tag,'source_sha256':hashlib.sha256((O/'BRK.npz').read_bytes()).hexdigest(),'late_window_ms':[1000,1450],'BRK_relay_observations':rows,'conditions':conditions},indent=2)+'\n');print(rows)
