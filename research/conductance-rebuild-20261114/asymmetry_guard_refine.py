"""Manual follow-up after the E2-lesion residual was identified as a hindleg
Ti-extensor MN. Test shared type parameters; never silence that individual cell.
"""
from pathlib import Path
import json,numpy as np
from network import load,simulate_network
from metrics import summarize
R=Path(__file__).parent;O=R/'results/asymmetry';base=json.load(open(O/'selected.json'))['config'];w,roles,meta=load('onehop',full_vnc=True);abl=[i for i,x in enumerate(meta) if x['type']=='INXXX466'];F='motor neuron|type:Ti flexor MN';E='motor neuron|type:Ti extensor MN';trials=[('unmodified_types',{}),('flexor_only',{F:{'gate_speed':.85}}),('flexor_and_extensor_gain',{F:{'gate_speed':.85},E:{'excitatory_gain':.5}})];rows=[]
for label,groups in trials:
 p={**base,'group_parameters':groups};conditions=['E2_silenced'] if label=='unmodified_types' else ['baseline','E2_silenced']
 for name in conditions:
  out=simulate_network(w,roles,meta,p,ablate=abl if name=='E2_silenced' else []);s=summarize(out);row={'variant':label,'condition':name,'config':p,'summary':s};rows.append(row);np.savez_compressed(O/f'guard-{label}-{name}.npz',spikes=out['spike_counts_1ms'],body_ids=[int(x['bodyId']) for x in meta]);(O/'guard-refinement.json').write_text(json.dumps(rows,indent=2));print(label,name,'periodicMN',s['rhythmic_MN'],flush=True)
