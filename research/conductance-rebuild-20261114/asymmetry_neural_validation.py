from pathlib import Path
import json,numpy as np
from network import load,simulate_network
from metrics import summarize
R=Path(__file__).parent;O=R/'results/asymmetry';p=json.load(open(O/'selected.json'))['config'];w,roles,meta=load('onehop',full_vnc=True);rec=[]
for name,changes,abl in [('E2_silenced',{},[i for i,x in enumerate(meta) if x['type']=='INXXX466']),('no_DN',{'drive_pA':0.},[]),('fine',{'dt_ms':.00625},[])]:
 q={**p,**changes};r=simulate_network(w,roles,meta,q,ablate=abl);s=summarize(r);rec.append({'condition':name,'config':q,'summary':s,'scope':'1454-cell induced graph'});np.savez_compressed(O/('neural-validation-'+name+'.npz'),spikes=r['spike_counts_1ms'],body_ids=[int(x['bodyId']) for x in meta]);(O/'neural-validation.json').write_text(json.dumps(rec,indent=2));print(name,'MN',s['rhythmic_MN'],'core',[(s['cells'][j]['rhythmic'],s['cells'][j]['burst_frequency_hz']) for j in [1,2]],flush=True)
