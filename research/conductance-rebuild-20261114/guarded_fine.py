from pathlib import Path
import json,numpy as np,sys
from network import load,simulate_network
from metrics import summarize
R=Path(__file__).parent;O=R/'results/asymmetry';p=json.load(open(R/'configs/asymmetry-guarded.json'));p['dt_ms']=.00625;w,roles,meta=load('onehop',full_vnc=True);label=sys.argv[1] if len(sys.argv)>1 else 'baseline';abl=[i for i,x in enumerate(meta) if x['type']=='INXXX466'] if label=='E2_silenced' else [];r=simulate_network(w,roles,meta,p,ablate=abl);s=summarize(r);np.savez_compressed(O/('guarded-fine-'+label+'.npz'),spikes=r['spike_counts_1ms'],body_ids=[int(x['bodyId']) for x in meta]);(O/('guarded-fine-'+label+'.json')).write_text(json.dumps({'config':p,'condition':label,'summary':s},indent=2));print(label,s['rhythmic_MN'],flush=True)
