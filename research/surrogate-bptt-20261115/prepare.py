"""Instrument a baseline without changing dynamics, then construct exact boundaries."""
from pathlib import Path
import hashlib,importlib.util,json,sys,shutil
import numpy as np
R=Path(__file__).resolve().parent;ROOT=R.parents[1]
cfg=json.loads((R/'config.json').read_text());D=ROOT/'research/single-model-delivery-20261115'
sys.path.insert(0,str(D/'runtime/02_code'));sys.path.insert(0,str(ROOT/'research/conductance-rebuild-20261114'))
from flymodel import Model
from grouped_parameters import group_key
m=Model(ROOT/cfg['baseline_model']);cache=R/'cache';cache.mkdir(exist_ok=True)
source=D/'runtime/02_code/flymodel/dynamics.py'
text=source.read_text();old='counts[min(int(k * dt / aux[8]), counts.shape[0] - 1), j] += 1'
assert text.count(old)==1
text=text.replace('int(np.ceil(steps * dt / aux[8]))','steps').replace(old,'counts[k, j] += 1')
# This copy only increases observation resolution; it does not alter any state update.
module=R/'instrumented_boundary_kernel.py';module.write_text(text)
spec=importlib.util.spec_from_file_location('instrumented_boundary_kernel',module);mod=importlib.util.module_from_spec(spec);sys.modules[spec.name]=mod;spec.loader.exec_module(mod)
events_path=cache/'baseline_spike_events.npz'
if not events_path.exists():
 import flymodel.simulator as simulator
 simulator._kernel=mod._kernel
 print('Recording exact full-network baseline spike events',flush=True)
 r=m.run_neural(cfg['experiment'],record_ids=m.neuron_ids(type='DNg100'))
 step,cell=np.nonzero(r['spikes']);del r;m.last_result=None
 np.savez_compressed(events_path,step=step.astype(np.int32),cell=cell.astype(np.int32))
shutil.copy2(events_path,R/'baseline-spike-events.npz')
with np.load(events_path,allow_pickle=False) as z:step=z['step'];event_cell=z['cell']
dt=m.config['neural']['solver']['dt_ms'];duration=m.config['experiments'][cfg['experiment']]['duration_ms'];steps=round(duration/dt)
with np.load(ROOT/cfg['baseline_neural'],allow_pickle=False) as z:baseline_spikes=z['spikes']
rebinned=np.zeros_like(baseline_spikes);np.add.at(rebinned,(np.floor(step*dt).astype(int),event_cell),1)
assert np.array_equal(rebinned,baseline_spikes),'Observation instrumentation changed baseline spikes'
local=sorted({i for x in m.mapping for i in x['MN_indices']}|{i for i,x in enumerate(m.neurons) if x['type'] in cfg['local_types']});local=np.asarray(local,dtype=np.int32);loc={int(i):j for j,i in enumerate(local)}
groups=sorted({group_key(m.neurons[i]) for i in local if m.neurons[i]['type'] not in cfg['frozen_types']});gi={g:j for j,g in enumerate(groups)};assignment=np.array([gi.get(group_key(m.neurons[i]),-1) for i in local],dtype=np.int32)
# Internal matrices store raw effective signed counts; gains remain dynamic parameters.
We=np.zeros((len(local),len(local)));Wi=np.zeros_like(We)
external_edges={}
for a,b,w in zip(m.pre,m.post,m.weight):
 if int(b) not in loc:continue
 j=loc[int(b)]
 if int(a) in loc:
  (We if w>0 else Wi)[j,loc[int(a)]]+=abs(w)
 else:external_edges.setdefault(int(a),[]).append((j,float(w)))
external_e=np.zeros((steps,len(local)),dtype=np.float64);external_i=np.zeros_like(external_e)
delay=max(1,round(m.config['neural']['solver']['delay_ms']/dt))
for k,i in zip(step,event_cell):
 when=int(k)+delay
 if when>=steps:continue
 for j,w in external_edges.get(int(i),[]):
  if w>0:external_e[when,j]+=w*m.cells[i,12]
  else:external_i[when,j]+=-w*m.cells[i,6]*m.cells[i,12]
# Remove zero columns; sparse local sources are much fewer than the mapped MN pool.
ecols=np.flatnonzero(We.any(0));icols=np.flatnonzero(Wi.any(0))
readout=np.zeros((len(m.mapping),len(local)))
for j,x in enumerate(m.mapping):
 for i in x['MN_indices']:readout[j,loc[i]]=1/len(x['MN_indices'])
ms=np.arange(round(duration));target=np.zeros((len(ms),len(m.mapping)))
with np.load(ROOT/cfg['target_file'],allow_pickle=False) as z:
 target_ids=list(z['muscle_ids']);native_t=np.arange(len(z['target_u']))*float(z['dt_s'])*1000
 for j,x in enumerate(m.mapping):target[:,j]=np.interp((ms-cfg['target_start_ms'])/cfg['target_time_stretch'],native_t,z['target_u'][:,target_ids.index(x['muscle_id'])])
mask=np.array([bool(x['MN_indices']) for x in m.mapping])
np.savez(cache/'local_inputs.npz',local=local,assignment=assignment,cell=m.cells[local],external_e=external_e,external_i=external_i,We=We[:,ecols],Wi=Wi[:,icols],ecols=ecols,icols=icols,readout=readout,target=target,mapped=mask,baseline_spikes=baseline_spikes[:,local])
identity={'baseline_model_sha256':m.sha256,'baseline_neural_sha256':hashlib.sha256((ROOT/cfg['baseline_neural']).read_bytes()).hexdigest(),'target_sha256':hashlib.sha256((ROOT/cfg['target_file']).read_bytes()).hexdigest(),'instrumented_source_sha256':hashlib.sha256(module.read_bytes()).hexdigest(),'original_kernel_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'baseline_spikes_reproduced_exactly':True,'local_cells':len(local),'local_body_ids':[m.ids[i] for i in local],'groups':groups,'variables':len(groups)*len(cfg['train_fields']),'train_parameter_names':[m.config['neural']['cell_parameter_columns'][i] for i in cfg['train_fields']],'local_exc_sources':len(ecols),'local_inh_sources':len(icols),'dt_ms':dt,'duration_ms':duration,'mapped_channels':int(mask.sum()),'unmapped_channels':int((~mask).sum()),'target_time_stretch':cfg['target_time_stretch'],'target_policy':'same global time mapping for every channel; no individual phase shifts','training_boundary':'baseline spike event replay, not free-running outer network'}
(R/'input-identity.json').write_text(json.dumps(identity,indent=2)+'\n');print(json.dumps(identity,indent=2),flush=True)
