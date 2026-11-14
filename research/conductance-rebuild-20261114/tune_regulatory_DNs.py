"""Fit unresolved positive quantal-conductance scales for regulatory DNs.
Cell identities, edge counts and signs unchanged. Frequencies are neural
surrogates, not measured step rates; no claims of gait coordination or speed.
"""
from pathlib import Path
import json,time,numpy as np
from network import load,simulate_network
from metrics import summarize
R=Path(__file__).parent;p=json.load(open(R/'configs/adult-network-selected.json'));p['duration_ms']=1200.;w,roles,meta=load('full');records=[]
for typ in ['DNg97','DNg55']:
 bodies=[str(x['bodyId']) for x in meta if x['type']==typ]
 for gain in [1.,3.,10.]:
  q={**p,'source_gain_by_body_id':{b:gain for b in bodies}};drive=np.array([p['drive_pA'] if role=='DN' or x['type']==typ else 0. for role,x in zip(roles,meta)]);print('Regulatory',typ,gain,flush=True);r=simulate_network(w,roles,meta,q,drive=drive);s=summarize(r);row={'type':typ,'source_conductance_gain':gain,'source_body_ids':bodies,'config':q,'summary':s};records.append(row);(R/'results/regulatory-DN-tuning.json').write_text(json.dumps(records,indent=2));np.savez_compressed(R/'results'/f'regulatory-{typ}-{gain:g}.npz',spikes=r['spike_counts_1ms'],voltage=r['voltage_first12'],body_ids=[int(x['bodyId']) for x in meta]);print('Done',typ,gain,'core f',[s['cells'][j]['burst_frequency_hz'] for j in [1,2]],flush=True)
