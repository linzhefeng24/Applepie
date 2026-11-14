"""Joint qualitative neuronal-response trials; no muscle fitting.
Optogenetic current is an unknown engineering proxy, not calibrated light dose.
Somatic voltage and model Ca are not calibrated experimental GCaMP signals.
"""
from pathlib import Path
import json,hashlib,numpy as np
from scipy import sparse
from network import simulate_network
from grouped_parameters import group_key
R=Path(__file__).parent;O=R/'results/experimental-panel';protocol=json.load(open(O/'protocol.json'));base=json.load(open(R/'configs/adult-network-selected.json'));base.update(dt_ms=.00625,duration_ms=2400.,onset_ms=400.,group_parameters={});records=[]
# Predeclare one shared multiplier policy across the annotated target types.
# One value for each similar type/side; zero individual offsets.
for gain in [1.,1.5,2.]:
 for a in protocol['assays']:
  name=a['id'];meta=json.load(open(O/(name+'-neurons.json')));w=sparse.load_npz(O/(name+'-connectivity.npz')).toarray();src=[i for i,x in enumerate(meta) if x['bodyId'] in a['source_ids']];tar=[i for i,x in enumerate(meta) if x['bodyId'] in a['target_ids']];roles=['MN' if x['class']=='motor neuron' else 'other' for x in meta];p={**base,'group_parameters':{group_key(meta[i]):{'excitatory_gain':gain} for i in tar}};out={}
  for cond in ['control','stimulated']:
   drive=np.zeros(len(meta));drive[src]=160. if cond=='stimulated' else 0.;r=simulate_network(w,roles,meta,p,drive=drive);v=r['voltage_first12'];start=int(600/r['record_interval_ms']);firing=r['spike_counts_1ms'][600:,tar].sum(axis=0)/1.8;values={'target_rate_hz':firing.tolist(),'target_soma_mV':v[start:,tar,0].mean(axis=0).tolist(),'target_final_model_calcium_uM':r['calcium_uM'][tar].tolist(),'source_rate_hz':(r['spike_counts_1ms'][600:,src].sum(axis=0)/1.8).tolist(),'numerical_failure':r['numerical_failure']};out[cond]=values;np.savez_compressed(O/f'{name}-gain{gain:g}-{cond}.npz',spikes=r['spike_counts_1ms'],voltage=v,final_calcium_uM=r['calcium_uM'],body_ids=[x['bodyId'] for x in meta])
  dv=np.array(out['stimulated']['target_soma_mV'])-out['control']['target_soma_mV'];dc=np.array(out['stimulated']['target_final_model_calcium_uM'])-out['control']['target_final_model_calcium_uM'];dr=np.array(out['stimulated']['target_rate_hz'])-out['control']['target_rate_hz'];direction=bool(np.all((dv>1.)|(dr>1.)) and np.all(dc>0) and not any(x['numerical_failure'] for x in out.values()));rec={'assay':name,'target_excitatory_gain_multiplier':gain,'config':p,'config_sha256':hashlib.sha256(json.dumps(p,sort_keys=True).encode()).hexdigest(),'observed':out,'delta_soma_mV':dv.tolist(),'delta_rate_hz':dr.tolist(),'delta_final_model_calcium_uM':dc.tolist(),'qualitative_model_direction_supported':direction,'status':'partial' if direction else 'failed_candidate','limitations':['path-focused context','male anatomy vs experimental assay','uncalibrated model Ca and optogenetic current','not full duration time-resolved GCaMP fit','no behavioral conclusion']};records.append(rec);(O/'trials.json').write_text(json.dumps(records,indent=2));print(name,gain,'direction',direction,'dV',dv.tolist(),'dr',dr.tolist(),flush=True)
