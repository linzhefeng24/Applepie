"""Connectivity-preserving network scopes; no fabricated inter-leg connections."""
from pathlib import Path
import json
import numpy as np
from scipy import sparse
ROOT=Path(__file__).parent

def load(scope='motor',full_vnc=False):
 if full_vnc:
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
 order=core+sorted(keep-set(core));metadata=[rows[i] for i in order];matrix=W[order][:,order].toarray()
 roles=['DN','E1','E2','I1','I2']+['MN' if rows[i]['class']=='motor neuron' else 'other' for i in order[5:]]
 return matrix,roles,metadata
