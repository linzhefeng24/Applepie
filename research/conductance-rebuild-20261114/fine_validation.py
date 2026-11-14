"""Independent finer-step confirmation; never hide the coarse-step failure."""
from pathlib import Path
import json,sys,time
import numpy as np
from network import load,simulate_network
from metrics import summarize
R=Path(__file__).parent;dt=float(sys.argv[1]);condition=sys.argv[2];p=json.load(open(R/'configs/adult-network-selected.json'));p.update(dt_ms=dt,duration_ms=1000.);w,roles,meta=load('full');abl=[j for j,x in enumerate(meta) if x['type']=='INXXX466'] if condition=='E2_silenced' else [];print('Start fine',condition,dt,flush=True);t=time.time();r=simulate_network(w,roles,meta,p,ablate=abl);s=summarize(r);label=f'fine-full-{condition}-dt{dt:g}';(R/'results'/f'{label}.json').write_text(json.dumps({'config':p,'condition':condition,'summary':s,'scope':'full4604-cell T1 graph','runtime_s':time.time()-t},indent=2));np.savez_compressed(R/'results'/f'{label}.npz',spikes=r['spike_counts_1ms'],voltage=r['voltage_first12'],body_ids=[int(x['bodyId']) for x in meta]);print('Finish',condition,dt,'MN',s['rhythmic_MN'],'core',[s['cells'][j]['burst_frequency_hz'] for j in [1,2]],'runtime',time.time()-t,flush=True)
