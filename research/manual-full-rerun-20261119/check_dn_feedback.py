"""Acute diagnostic: remove incoming synapses to DNg100, keep all other edges.
No parameters are tuned and the manual model file remains unchanged.
"""
from pathlib import Path
import sys,json,hashlib,time
import numpy as np
R=Path(__file__).resolve().parent;P=R/'cache/extracted/Manual_FreeBody';sys.path.insert(0,str(P/'02_code'))
from flymodel import Model
from flymodel.dynamics import _kernel
m=Model(P/'01_model/model.yaml');s=m.config['neural']['solver'];protocol=m.config['experiments']['DN_drive'];n=len(m.ids);dnids=['10045','10056'];dni=np.array([m.lookup[x] for x in dnids]);keep=~np.isin(m.post,dni);pre=m.pre[keep];post=m.post[keep];weight=m.weight[keep];offsets=np.r_[0,np.cumsum(np.bincount(pre,minlength=n))]
wave=np.zeros((round(protocol['duration_ms']/s['input_sample_ms'])+1,n))
for e in protocol['events']:
 for id in e['neuron_ids']:wave[round(e['on_ms']/s['input_sample_ms']):round(e['off_ms']/s['input_sample_ms']),m.lookup[id]]=e['current_pA']
ids=dnids+['800003','800009','800114','800061','800072','800211'];rec=np.array([m.lookup[x] for x in ids]);start=time.monotonic()
out=_kernel(n,pre,post,weight,np.zeros(n),np.zeros(n),np.zeros(n,dtype=np.bool_),s['dt_ms'],round(protocol['duration_ms']/s['dt_ms']),0,round(s['delay_ms']/s['dt_ms']),m.global_values,m.cells,round(s['record_interval_ms']/s['dt_ms']),wave,s['input_sample_ms'],rec,offsets,m.kinetics,m.aux)
assert not out[5];stats={}
for id,i in zip(ids,rec):
 times=np.repeat(np.arange(len(out[0]))*s['spike_bin_ms'],out[0][:,i].astype(int));times=times[(times>=200)&(times<1400)];onsets=times[np.r_[True,np.diff(times)>60]] if len(times) else times
 stats[id]={'type':m.neurons[i]['type'],'spike_times_ms':times.tolist(),'burst_onsets_gap60ms':onsets.tolist()}
d={'condition':'all incoming DNg100 edges removed; original outgoing edges and all nonDN connectivity retained','removed_directed_edges':int((~keep).sum()),'neural_parameters_unchanged':True,'file_model_sha256':m.sha256,'remaining_edge_weights_sha256':hashlib.sha256(weight.tobytes()).hexdigest(),'seconds':time.monotonic()-start,'selected_neurons':stats,'scope':'mechanistic perturbation only, not replacement manual model or training'}
(R/'DN-feedback-cut.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');print(json.dumps({id:{'count':len(v['spike_times_ms']),'onsets':v['burst_onsets_gap60ms']} for id,v in stats.items()},ensure_ascii=False))
