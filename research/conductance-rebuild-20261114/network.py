"""Connectivity-preserving network scopes; no fabricated inter-leg connections."""
from pathlib import Path
import json
import numpy as np
from scipy import sparse
ROOT=Path(__file__).parent

def load(scope='motor',full_vnc=False):
 if full_vnc and (ROOT/'data/all-legs-induced-connectivity.npz').exists():
  rows=json.load(open(ROOT/'data/all-legs-induced-neurons.json'));W=sparse.load_npz(ROOT/'data/all-legs-induced-connectivity.npz');ids0=np.array([int(x['bodyId']) for x in rows])
 elif full_vnc:
  import csv
  base=Path('/workspace/reproduction/neuromuscular/available-chain');rows=list(csv.DictReader(open(base/'neuron-metadata.csv')));W=sparse.load_npz(base/'MANC-central-connections-20251006.npz');ids0=np.array([int(x['bodyId']) for x in rows])
 else:
  rows=json.load(open(ROOT/'data/t1-neurons.json'));W=sparse.load_npz(ROOT/'data/t1-author-connectivity.npz');ids0=np.array([int(x['bodyId']) for x in rows])
 lookup={int(x):i for i,x in enumerate(ids0)};core=[lookup[x] for x in [10093,10707,11751,13905,10242]]
 if scope=='core':keep=set(core)
 elif scope=='motor':keep=set(core)|{i for i,x in enumerate(rows) if x['class']=='motor neuron'}
 elif scope=='onehop':keep=set(core)|set(W[core].nonzero()[1])|{i for i,x in enumerate(rows) if x['class']=='motor neuron'}
 elif scope=='full':keep=set(range(len(rows)))
 else:raise ValueError(scope)
 order=core+sorted(keep-set(core));metadata=[{**rows[i],'connectome_namespace':'MANC'} for i in order];matrix=W[order][:,order].toarray()
 roles=['DN','E1','E2','I1','I2']+['MN' if rows[i]['class']=='motor neuron' else 'other' for i in order[5:]]
 return matrix,roles,metadata


def type_pair_conductances(weights,metadata,parameters):
 """Unknown type-pair synaptic efficacy, separate from structural counts.
 Same source/target types in one namespace share a positive multiplier.
 This permits testing a real direct-DN bypass without removing its edges.
 """
 if not parameters:return weights,[]
 out=np.array(weights,dtype=float,copy=True);records=[]
 for p in parameters:
  gain=float(p['gain'])
  if not np.isfinite(gain) or not .05<=gain<=5:raise ValueError('Type-pair conductance prior must be within0.05..5; no edge deletion')
  pre=[i for i,x in enumerate(metadata) if x.get('connectome_namespace')==p['namespace'] and x.get('type')==p['source_type']]
  post=[i for i,x in enumerate(metadata) if x.get('connectome_namespace')==p['namespace'] and x.get('type')==p['target_type']]
  if not pre or not post:raise KeyError('Type pair absent from namespace')
  block=out[np.ix_(pre,post)];count=int(np.count_nonzero(block))
  if not count:raise ValueError('No structural connection for requested type pair')
  out[np.ix_(pre,post)]=block*gain;records.append({**p,'affected_existing_edges':count,'source_body_ids':[metadata[i]['bodyId'] for i in pre],'target_body_ids':[metadata[i]['bodyId'] for i in post]})
 return out,records

def receptor_conductances(weights,metadata,parameters):
 """Scale effective synaptic conductance, never the stored structural graph.
 GABAA and GluCl are target response hypotheses for negative GABA/glutamate
 edges. Other GABA receptor kinetics and transmitter mixtures remain absent.
 Namespace-qualified type groups prevent accidental cross-dataset transfer.
 Zero permits an explicit receptor-block experiment; healthy gains are priors.
 """
 if not parameters:return weights,[]
 from grouped_parameters import group_key
 keys=[str(x.get('connectome_namespace',''))+'|'+group_key(x) for x in metadata]
 unknown=set(parameters)-set(keys)
 if unknown:raise KeyError('Receptor groups absent from graph: '+str(sorted(unknown)))
 nt=np.array([str(x.get('predictedNt','')).lower() for x in metadata]);out=np.array(weights,dtype=float,copy=True);applied=[]
 for key,values in parameters.items():
  targets=np.array([i for i,k in enumerate(keys) if k==key]);record={'target_group':key,'target_body_ids':[metadata[i]['bodyId'] for i in targets],'receptors':{}}
  for receptor,gain in values.items():
   if receptor not in ['GABAA','GluCl']:raise ValueError('Unknown receptor '+receptor)
   if not np.isfinite(gain) or not 0<=gain<=5:raise ValueError('Receptor response prior must be within0..5')
   pre=np.flatnonzero(nt==('gaba' if receptor=='GABAA' else 'glutamate'));block=out[np.ix_(pre,targets)];negative=block<0;count=int(negative.sum());block[negative]*=gain;out[np.ix_(pre,targets)]=block;record['receptors'][receptor]={'gain':gain,'affected_negative_edges':count}
  applied.append(record)
 return out,applied

def simulate_network(weights,roles,metadata,params,drive=None,ablate=(),drive_waveform=None,record_indices=None):
 from model import simulate
 source=params.get('source_gain_by_body_id',{})
 gains=np.array([source.get(str(row['bodyId']),1.) for row in metadata],dtype=float)
 if not np.isfinite(gains).all() or np.any(gains<=0):raise ValueError('Source conductance scales must be finite positive; no edge removal or sign flip')
 from grouped_parameters import resolve
 overrides,_=resolve(metadata,params.get('group_parameters',{}),params.get('individual_leak_offsets_mV',{}),params.get('class_parameters',{}),params.get('family_parameters',{}),params.get('cell_parameters',{}))
 effective,pairs=type_pair_conductances(weights,metadata,params.get('type_pair_conductance_gains',[]))
 effective,interventions=receptor_conductances(effective,metadata,params.get('target_receptor_gains',{}))
 result=simulate(effective,roles,params,drive=drive,ablate=ablate,source_gains=gains,cell_overrides=overrides,drive_waveform=drive_waveform,record_indices=record_indices)
 result['receptor_interventions']=interventions
 result['type_pair_interventions']=pairs
 return result
