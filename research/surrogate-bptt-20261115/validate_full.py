"""Export shared-type parameter factors and test original full hard-spike HH.
No replay of boundary spikes is used in these full-network validation runs.
"""
from pathlib import Path
import hashlib,json,sys,platform
from importlib.metadata import version
import numpy as np
R=Path(__file__).resolve().parent;ROOT=R.parents[1];cfg=json.loads((R/'config.json').read_text());identity=json.loads((R/'input-identity.json').read_text())
sys.path.insert(0,str(ROOT/'research/single-model-delivery-20261115/runtime/02_code'));sys.path.insert(0,str(ROOT/'research/conductance-rebuild-20261114'))
from flymodel import Model
from grouped_parameters import group_key
checkpoint=Path(sys.argv[1]) if len(sys.argv)>1 else R/'best-parameters.npz';tag=sys.argv[2] if len(sys.argv)>2 else 'candidate';out=R/'full-validation'/tag;out.mkdir(parents=True,exist_ok=True)
with np.load(checkpoint,allow_pickle=False) as z:delta=z['relative_factors'];epoch=int(z['epoch'])
assert np.isfinite(delta).all() and np.max(abs(delta))<=cfg['relative_bound']+1e-12
m=Model(ROOT/cfg['baseline_model']);base=m.cells.copy();groups=dict(zip(identity['groups'],delta));affected=[]
for i,x in enumerate(m.neurons):
 key=group_key(x)
 if key in groups:
  m.cells[i,cfg['train_fields']]*=1+groups[key];affected.append(x['bodyId'])
patch={'schema':'shared_neural_parameter_patch_v1','baseline_model_sha256':m.sha256,'checkpoint_epoch':epoch,'checkpoint_sha256':hashlib.sha256(checkpoint.read_bytes()).hexdigest(),'field_indices':cfg['train_fields'],'field_names':identity['train_parameter_names'],'group_relative_factors':{k:v.tolist() for k,v in groups.items()},'affected_body_ids':affected,'max_relative_change':float(np.max(abs(delta))),'rms_relative_change':float(np.sqrt(np.mean(delta**2))),'baseline_cell_array_sha256':hashlib.sha256(base.tobytes()).hexdigest(),'candidate_cell_array_sha256':hashlib.sha256(m.cells.tobytes()).hexdigest(),'scope':'same group factors applied to every matching member of the full3988 graph, including homologues outside the training pool','anatomical_connections_changed':False,'transmitter_signs_changed':False,'NMJ_readout_changed':False}
patchbytes=(json.dumps(patch,indent=2)+'\n').encode();(out/'parameter-patch.json').write_bytes(patchbytes);patchsha=hashlib.sha256(patchbytes).hexdigest()
np.savez_compressed(out/'resolved-cell-parameters.npz',values=m.cells)
with np.load(R/'cache/local_inputs.npz',allow_pickle=False) as z:target=z['target'];mapped=z['mapped']
tr=(np.arange(len(target))>=cfg['target_start_ms'])&(np.arange(len(target))<cfg['train_end_ms']);te=(np.arange(len(target))>=cfg['train_end_ms'])&(np.arange(len(target))<cfg['evaluation_end_ms'])
def errors(u):return {'train_mse_mapped':float(np.mean((u[tr][:,mapped]-target[tr][:,mapped])**2)),'holdout_mse_mapped':float(np.mean((u[te][:,mapped]-target[te][:,mapped])**2)),'holdout_mse_all130':float(np.mean((u[te]-target[te])**2))}
with np.load(ROOT/cfg['baseline_neural'],allow_pickle=False) as z:old={k:z[k] for k in z.files}
report={'status':'in_progress','tag':tag,'model_sha256':m.sha256,'parameter_patch_sha256':patchsha,'checkpoint_epoch':epoch,'baseline_full_network':errors(m.muscle_excitation(old)),'regularization':cfg['regularization_lambda']*float(np.mean(delta**2)),'max_relative_change':patch['max_relative_change'],'rms_relative_change':patch['rms_relative_change'],'cell_parameters_changed':len(affected),'python':platform.python_version(),'versions':{k:version(k) for k in ['numpy','numba','scipy','jax','jaxlib']},'conditions':{}}
record=sorted({b for b in ['10045','10056','523769','10360','519624','10975','14986','519129','39880','800041','800051','800053','801214','801246','800621','812953','800158','809935'] if b in m.lookup}|{m.ids[i] for i,x in enumerate(m.neurons) if x['type'] in cfg['local_types']})
if (out/'report.json').exists():
 previous=json.loads((out/'report.json').read_text())
 if previous.get('parameter_patch_sha256')==patchsha:report=previous
protocols=sys.argv[3:] or ['DN_drive','quiet','BRK','PFL3_left','BPN_FG']
for protocol in protocols:
 if protocol in report['conditions'] and not report['conditions'][protocol].get('numerical_failure'):
  print('Already completed',protocol,flush=True);continue
 print('Original full hard network:',tag,protocol,flush=True)
 try:r=m.run_neural(protocol,record_ids=record)
 except Exception as e:
  report['conditions'][protocol]={'numerical_failure':repr(e)};(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');raise
 r['parameter_patch_sha256']=np.array(patchsha);r['cell_parameters_sha256']=np.array(patch['candidate_cell_array_sha256']);r['run_id']=np.array(hashlib.sha256(str(r['run_id']).encode()+patchsha.encode()).hexdigest())
 np.savez_compressed(out/(protocol+'.npz'),**r)
 row={'numerical_failure':False,'run_id':str(r['run_id']),'spikes':int(r['spikes'].sum()),'rates_500_950_Hz':{b:float(r['spikes'][500:950,m.lookup[b]].sum()/0.45) for b in record},'rates_1000_1450_Hz':{b:float(r['spikes'][1000:1450,m.lookup[b]].sum()/0.45) for b in record}}
 if protocol=='DN_drive':
  u=m.muscle_excitation(r);row.update(errors(u));np.savez_compressed(out/'muscle-u.npz',u=u,target_u=target,mapped=mapped,muscle_ids=[x['muscle_id'] for x in m.mapping])
 report['conditions'][protocol]=row;(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'protocol':protocol,**{k:v for k,v in row.items() if 'mse' in k}}),flush=True)
report['status']='completed';(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
