"""One bounded type-shared test for the remaining fine-step extensor burst:
halve SK conductance for the named Ti-extensor MN pool, never mute one cell.
All outcomes are retained; this is a hypothesis, not measured physiology.
"""
from pathlib import Path
import json,numpy as np
from network import load,simulate_network
from metrics import summarize,burst_envelope
R=Path(__file__).parent;O=R/'results/asymmetry';p=json.load(open(R/'configs/asymmetry-guarded.json'));p['dt_ms']=.00625;p['group_parameters']['motor neuron|type:Ti extensor MN']={'SK_scale':.5};(R/'configs/asymmetry-SK-hypothesis.json').write_text(json.dumps(p,indent=2));w,roles,meta=load('onehop',full_vnc=True);records=[]
for condition in ['E2_silenced','baseline']:
 abl=[i for i,x in enumerate(meta) if x['type']=='INXXX466'] if condition=='E2_silenced' else [];out=simulate_network(w,roles,meta,p,ablate=abl);s=summarize(out);residual=[]
 for j,(role,c) in enumerate(zip(roles,s['cells'])):
  if role=='MN' and c['rhythmic']:residual.append({'body_id':meta[j]['bodyId'],'type':meta[j]['type'],'spike_metrics':c,'burst_metrics':burst_envelope(out['spike_counts_1ms'][:,j])})
 records.append({'condition':condition,'config':p,'summary':s,'periodic_motor_details':residual});np.savez_compressed(O/('SK-hypothesis-'+condition+'.npz'),spikes=out['spike_counts_1ms'],body_ids=[int(x['bodyId']) for x in meta]);(O/'SK-hypothesis.json').write_text(json.dumps(records,indent=2));print(condition,s['rhythmic_MN'],flush=True)
