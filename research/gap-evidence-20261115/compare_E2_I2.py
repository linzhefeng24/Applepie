"""Causal counterfactual: only add all annotated I2 ablations to E2 ablation.
No parameter adjustment, no disappearance-of-all-spikes criterion.
"""
from pathlib import Path
import json,hashlib,numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).parent;N=R.parent/'conductance-rebuild-20261114';B=N/'results/manual-mechanism';names=['expanded-shared-extensor-direct-DN-weak-E2-silenced','expanded-shared-extensor-direct-DN-weak-E2-I2-silenced'];m=json.load(open(B/'neurons.json'));ii=[i for i,x in enumerate(m) if x['type']=='IN17A001'];ii.sort(key=lambda i:(m[i].get('somaNeuromere') or '',m[i].get('somaSide') or ''));cfgs=[json.load(open(B/(s+'-config.json'))) for s in names];assert cfgs[0]['parameters']==cfgs[1]['parameters'];assert cfgs[0]['drive_pA']==cfgs[1]['drive_pA'];assert cfgs[0]['graph_sha256']==cfgs[1]['graph_sha256'];added=set(cfgs[1]['ablate_body_ids'])-set(cfgs[0]['ablate_body_ids']);assert added=={x['bodyId'] for x in m if x['type']=='IN19A007'};fig,axs=plt.subplots(6,2,figsize=(13,12),sharex=True);rows=[]
for col,name in enumerate(names):
 p=B/(name+'.npz');z=np.load(p);sp=z['spikes'];rec=list(z['record_body_ids']);t=z['time_ms'];out=[]
 for row,i in enumerate(ii):
  x=m[i];j=rec.index(x['bodyId']);times=np.repeat(np.arange(400,1600),sp[400:,i]);isi=np.diff(times);out.append({'body_id':x['bodyId'],'segment':x.get('somaNeuromere'),'side':x.get('somaSide'),'rate_Hz':len(times)/1.2,'spike_times_ms':times.tolist(),'ISI_ms':isi.tolist(),'median_ISI_ms':float(np.median(isi)) if len(isi) else None});axs[row,col].plot(t,z['voltage'][:,j,0],lw=.65);axs[row,col].set_ylabel(x['bodyId']);axs[row,col].grid(alpha=.2);axs[row,col].set_xlim(400,1600)
 mn=[i for i,x in enumerate(m) if x['class']=='motor neuron'];i2=[i for i,x in enumerate(m) if x['type']=='IN19A007'];rows.append({'condition':name,'raw_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'active_MN_count':int((sp[400:,mn].sum(0)>0).sum()),'I2_spikes':sp[400:,i2].sum(0).tolist(),'E1_observations':out,'numerical_failure':json.load(open(B/(name+'-diagnosis.json')))['numerical_failure']})
axs[0,0].set_title('E2 ablated');axs[0,1].set_title('E2+I2 ablated; identical physiology and input')
for a in axs[-1]:a.set_xlabel('Time(ms)')
fig.tight_layout();fig.savefig(R/'diagnostics/E2-versus-E2-I2-causal.png',dpi=150);(R/'diagnostics/E2-I2-causal-review.json').write_text(json.dumps({'status':'new counterfactual integration compared with existing E2 integration','parameters_graph_drive_identical':True,'only_added_ablation_body_ids':sorted(added),'conditions':rows,'interpretation_policy':'Compare full spike trains and membrane patterns, not disappearance of all activity. No automatic pass or unique biological interpretation.'},indent=2)+'\n');print([(x['condition'],x['active_MN_count'],[(y['body_id'],y['rate_Hz'],y['median_ISI_ms']) for y in x['E1_observations']]) for x in rows])
