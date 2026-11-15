"""Locate real remaining input sources after an ablation; no scalar objective.
Event-load ranks are descriptive proxies. Full target currents remain in NPZ.
"""
from pathlib import Path
import json,hashlib,sys
import numpy as np
from scipy import sparse
from network import type_pair_conductances
R=Path(__file__).parent;B=R/'results/manual-mechanism';mode=sys.argv[1];m=[{**x,'connectome_namespace':'MANC'} for x in json.load(open(B/'neurons.json'))];path=B/(mode+'.npz');z=np.load(path);assert list(z['body_ids'])==[x['bodyId'] for x in m];cfg=json.load(open(B/(mode+'-config.json')));W=sparse.load_npz(B/'connectivity.npz');effective,interventions=type_pair_conductances(W.toarray(),m,cfg['parameters'].get('type_pair_conductance_gains',[]));effective=sparse.csc_matrix(effective);lookup={x['bodyId']:i for i,x in enumerate(m)};hz=z['spikes'][400:].sum(axis=0)/1.2;rows=[]
for body in z['record_body_ids']:
 j=lookup[body]
 if m[j]['class']!='motor neuron':continue
 col=effective[:,j].tocoo();events=[]
 for i,w in zip(col.row,col.data):
  if hz[i]<=0:continue
  gain=z['cell_parameters'][i,12]*(z['cell_parameters'][j,5] if w>0 else z['cell_parameters'][i,6]);events.append({'body_id':m[i]['bodyId'],'type':m[i]['type'],'rate_hz':float(hz[i]),'anatomical_signed_weight':float(W[i,j]),'effective_signed_weight':float(w),'signed_event_load_proxy':float(w*gain*hz[i])})
 events.sort(key=lambda x:abs(x['signed_event_load_proxy']),reverse=True);rows.append({'target_body_id':body,'target_type':m[j]['type'],'target_rate_hz':float(hz[j]),'active_inputs':events})
report={'mode':mode,'window_ms':[400,1600],'raw_result_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'graph_sha256':hashlib.sha256((B/'connectivity.npz').read_bytes()).hexdigest(),'analysis_code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'type_pair_interventions':interventions,'method':__doc__,'targets':rows};(B/(mode+'-input-diagnosis.json')).write_text(json.dumps(report,indent=2)+'\n');print([(x['target_body_id'],round(x['target_rate_hz'],1),[(s['body_id'],s['type']) for s in x['active_inputs'][:3]]) for x in rows])
