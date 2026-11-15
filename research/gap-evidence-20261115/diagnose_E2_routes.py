"""All six E1/I1 outputs after E2 ablation, with actual surviving input routes.
Old expanded MANC assay only, not a fresh run or MaleCNS extension result.
Signed event loads are observational, not a causal path intervention.
"""
from pathlib import Path
import json,hashlib,numpy as np
from scipy import sparse
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).parent;N=R.parent/'conductance-rebuild-20261114';B=N/'results/manual-mechanism';m=json.load(open(B/'neurons.json'));W=sparse.load_npz(B/'connectivity.npz').tocsc();p=B/'expanded-shared-extensor-direct-DN-weak-E2-silenced.npz';z=np.load(p);cfg=json.load(open(B/'expanded-shared-extensor-direct-DN-weak-E2-silenced-config.json'));t=z['time_ms'];rec=list(z['record_body_ids']);rates=z['spikes'][400:].sum(0)/1.2;cp=z['cell_parameters'];ii=[i for i,x in enumerate(m) if x['type']=='IN17A001'];ii.sort(key=lambda i:(m[i].get('somaNeuromere') or '',m[i].get('somaSide') or ''));fig,axs=plt.subplots(6,2,figsize=(13,13),sharex=True);rows=[]
for row,i in enumerate(ii):
 x=m[i];j=rec.index(x['bodyId']);sel=(t>=400)&(t<1600);ax=axs[row,0];ax.plot(t,z['voltage'][:,j,0],lw=.6);ax.set_ylabel(x['bodyId']+' '+str(x.get('somaNeuromere'))+' '+str(x.get('somaSide')));axs[row,1].plot(t,z['conductances_nS'][:,j,0],label='gE');axs[row,1].plot(t,z['conductances_nS'][:,j,1],label='gI');a=W[:,i].tocoo();sources=[]
 for src,w in zip(a.row,a.data):
  effective=float(w*cp[src,12]*(cp[i,5] if w>0 else cp[src,6]));sources.append({'pre':m[src]['bodyId'],'type':m[src]['type'],'signed_count':float(w),'source_rate_Hz':float(rates[src]),'signed_count_gain_event_rate':effective*float(rates[src])})
 sources.sort(key=lambda a:abs(a['signed_count_gain_event_rate']),reverse=True);times=np.repeat(np.arange(400,1600),z['spikes'][400:,i]);rows.append({'body_id':x['bodyId'],'segment':x.get('somaNeuromere'),'side':x.get('somaSide'),'rate_Hz':float(rates[i]),'spike_times_ms':times.tolist(),'ISI_ms':np.diff(times).tolist(),'strongest_surviving_input_event_loads':sources[:10]})
for a in axs.flat:a.grid(alpha=.2);a.set_xlim(400,1600)
axs[0,0].set_title('E1 soma voltage(mV), all six legs');axs[0,1].set_title('Actual incoming conductance(nS)');axs[0,1].legend()
for a in axs[-1]:a.set_xlabel('Time(ms)')
fig.tight_layout();fig.savefig(R/'diagnostics/E2-all-six-core-traces.png',dpi=150);silent_i1=[x['bodyId'] for i,x in enumerate(m) if x['type']=='IN16B036' and rates[i]==0];report={'status':'new all-six-leg inspection of existing saved MANC run; no new integration','source_npz_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'E1_outputs':rows,'silent_I1_body_ids':silent_i1,'interpretation':'All6 I1 silent, LF/RF E1 mainly tonic; other four E1 retain sparse irregular spikes. Surviving input routes and exact time trains saved; cannot infer every expanded MN rhythm is abolished from the front-leg result.'};(R/'diagnostics/E2-all-six-route-review.json').write_text(json.dumps(report,indent=2)+'\n');print([(x['body_id'],x['rate_Hz'],[(s['type'],round(s['signed_count_gain_event_rate'],1)) for s in x['strongest_surviving_input_event_loads'][:3]]) for x in rows])
