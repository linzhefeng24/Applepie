"""Rank real inhibitory inputs for manual diagnosis, not an objective.
The rate×signed-count ranking approximates mean inhibitory conductance, not
precise event currents; actual currents are separately retained in raw traces.
"""
from pathlib import Path
import json,sys,numpy as np
from scipy import sparse
R=Path(__file__).parent;O=R/'results/mcns-command-v2';case=sys.argv[1];m=json.load(open(O/'neurons.json'));W=sparse.load_npz(O/'signed-hypothesis-connectivity.npz').tocsc();z=np.load(O/(case+'.npz'));rate=z['spikes'][400:].sum(axis=0).astype(float);records=[]
for j,x in enumerate(m):
 if x['type'] not in ['DNg100','DNg97']:continue
 col=W[:,j].tocoo();pairs=[(int(i),float(v),float(-v*rate[i])) for i,v in zip(col.row,col.data) if v<0 and rate[i]>0];pairs.sort(key=lambda a:a[2],reverse=True);total=sum(v for _,_,v in pairs);records.append({'target_body_id':x['bodyId'],'target_type':x['type'],'side':x['somaSide'],'source_conductance_ranking':[{'source_body_id':m[i]['bodyId'],'type':m[i]['type'],'nt':m[i]['predictedNt'],'source_hz':rate[i],'signed_weight':w,'fraction_rate_weight':v/max(total,1e-12)} for i,w,v in pairs[:12]],'warning':'Approximate attribution; do not interpret this as measured transmitter conductance or fitted parameter'})
(O/(case+'-input-ranking.json')).write_text(json.dumps(records,indent=2));print([(x['target_type'],x['side'],[(a['type'],round(a['fraction_rate_weight'],2)) for a in x['source_conductance_ranking'][:3]]) for x in records])
# Additional actual candidate-family outputs, never assign MF14 to an unknown ID.
idx=[i for i,x in enumerate(m) if x['type']=='INXXX468' or x.get('mancType')=='INXXX468'];print('LUL130 candidate-family cells',[(m[i]['bodyId'],m[i]['somaNeuromere'],m[i]['somaSide'],rate[i]) for i in idx])
