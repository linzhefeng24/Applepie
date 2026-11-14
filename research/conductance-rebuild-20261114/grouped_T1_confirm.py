from pathlib import Path
import sys,json,numpy as np
from network import load,simulate_network
from metrics import summarize
R=Path(__file__).parent;O=R/'results/asymmetry';label=sys.argv[1];p=json.load(open(R/'configs/asymmetry-guarded.json'));p['duration_ms']=1200.;w,roles,meta=load('full');abl=[i for i,x in enumerate(meta) if x['type']=='INXXX466'] if label=='E2_silenced' else [];out=simulate_network(w,roles,meta,p,ablate=abl);s=summarize(out);(O/('full-T1-grouped-'+label+'.json')).write_text(json.dumps({'config':p,'condition':label,'scope':'all4604 T1 nodes, coarse0.025ms, new shared-flexor parameters','summary':s},indent=2));np.savez_compressed(O/('full-T1-grouped-'+label+'.npz'),spikes=out['spike_counts_1ms'],body_ids=[int(x['bodyId']) for x in meta]);print(label,s['rhythmic_MN'],flush=True)
