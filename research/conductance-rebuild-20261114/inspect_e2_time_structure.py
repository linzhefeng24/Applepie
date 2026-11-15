"""Compare intact and E2-ablated temporal structure, not spike-count silence.
The published condition concerns rhythmicity. These traces permit scoped manual
judgment and do not automatically declare an experimental pass.
"""
from pathlib import Path
import json,hashlib
import numpy as np
from scipy.ndimage import gaussian_filter1d
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).parent;B=R/'results/manual-mechanism';meta=json.load(open(B/'neurons.json'));ids=[x['bodyId'] for x in meta];cases=['expanded-shared-extensor-direct-DN-weak','expanded-shared-extensor-direct-DN-weak-E2-silenced'];bodies=['10707','13905','11657','12134','10690','13163'];fig,axs=plt.subplots(len(bodies),2,figsize=(13,12),sharex=True);records=[]
for col,case in enumerate(cases):
 path=B/(case+'.npz');z=np.load(path);sp=z['spikes'];rec=list(z['record_body_ids']);t=z['time_ms'];volt=z['voltage'];rows=[]
 for row,b in enumerate(bodies):
  i=ids.index(b);k=rec.index(b);times=np.repeat(np.arange(400,1600),sp[400:,i]);isi=np.diff(times);axs[row,col].plot(t,volt[:,k,0],lw=.6);axs[row,col].set_ylabel(b+' '+meta[i]['type']);axs[row,col].set_xlim(400,1600);axs[row,col].grid(alpha=.15);rows.append({'body_id':b,'type':meta[i]['type'],'spike_times_ms':times.tolist(),'ISI_ms_min_median_max':np.quantile(isi,[0,.5,1]).tolist() if len(isi) else []})
 axs[0,col].set_title('Intact' if col==0 else 'E2 ablated');records.append({'condition':case,'source_npz_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'cells':rows})
for ax in axs[-1]:ax.set_xlabel('Time (ms)')
fig.suptitle('Core and MN membrane traces: tonic firing is distinct from population rhythm');fig.tight_layout();fig.savefig(B/'E2-temporal-structure.png',dpi=140);plt.close(fig);(B/'E2-temporal-structure.json').write_text(json.dumps({'method':__doc__,'records':records,'status':'manual review; residual activity is not itself a rhythmicity criterion'},indent=2)+'\n')
