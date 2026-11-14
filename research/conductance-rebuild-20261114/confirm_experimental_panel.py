"""No refitting: finer-step / alternate-dose checks of both neuronal assays."""
from pathlib import Path
import json,numpy as np
from scipy import sparse
from network import simulate_network
R=Path(__file__).parent;O=R/'results/experimental-panel';prot=json.load(open(O/'protocol.json'));old=json.load(open(O/'trials.json'));records=[];configs={}
for a in prot['assays']:
 name=a['id'];p=next(x['config'] for x in old if x['assay']==name and x['target_excitatory_gain_multiplier']==1.);p={**p,'dt_ms':.003125};configs[name]=p;meta=json.load(open(O/(name+'-neurons.json')));w=sparse.load_npz(O/(name+'-connectivity.npz')).toarray();src=[i for i,x in enumerate(meta) if x['bodyId'] in a['source_ids']];tar=[i for i,x in enumerate(meta) if x['bodyId'] in a['target_ids']];roles=['MN' if x['class']=='motor neuron' else 'other' for x in meta];reference=None
 for dose in [0.,80.,160.,240.]:
  drive=np.zeros(len(meta));drive[src]=dose;r=simulate_network(w,roles,meta,p,drive=drive);vs=r['voltage_first12'][int(600/r['record_interval_ms']):,tar,0].mean(axis=0);ca=r['calcium_uM'][tar];rate=r['spike_counts_1ms'][600:,tar].sum(axis=0)/1.8
  if dose==0:reference=(vs,ca,rate)
  dv=vs-reference[0];dc=ca-reference[1];dr=rate-reference[2];row={'assay':name,'dose_pA':dose,'dt_ms':p['dt_ms'],'delta_soma_mV':dv.tolist(),'delta_final_model_calcium_uM':dc.tolist(),'delta_rate_hz':dr.tolist(),'qualitative_direction_supported':bool(dose>0 and np.all((dv>1)|(dr>1)) and np.all(dc>0) and not r['numerical_failure']),'numerical_failure':r['numerical_failure'],'scope':'local-context qualitative proxy; not calibrated GCaMP or behavioral pass'};records.append(row);np.savez_compressed(O/f'{name}-confirm-dose{dose:g}.npz',spikes=r['spike_counts_1ms'],voltage=r['voltage_first12'],final_calcium_uM=r['calcium_uM']);(O/'confirmation.json').write_text(json.dumps({'configs':configs,'results':records},indent=2));print(name,dose,row['qualitative_direction_supported'],dv.tolist(),flush=True)
