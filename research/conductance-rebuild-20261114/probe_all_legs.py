"""Transfer fixed candidate to a full-VNC-source induced subgraph.
All annotated motor cells plus one-hop core targets are retained with every
edge between retained nodes. NOT the full 23532-neuron network.
"""
from pathlib import Path
import json,time,sys
import numpy as np
from network import load
from model import simulate
from metrics import summarize
R=Path(__file__).parent;prefix='adult-all-legs-subgraph' if len(sys.argv)>1 else 'all-legs-subgraph';conf='adult-network-selected.json' if len(sys.argv)>1 else 'downstream-selected.json';p=json.load(open(R/'configs'/conf));p['duration_ms']=1800.;w,roles,meta=load('onehop',full_vnc=True);print('All-VNC-source subset',len(w),'MN',roles.count('MN'),'edges',np.count_nonzero(w),flush=True)
r=simulate(w,roles,p);s=summarize(r);rec={'scope':'Induced one-hop core-target + all-MN subgraph from 23532-cell MANC author graph; not complete intact VNC','neurons':len(w),'motor_cells':roles.count('MN'),'config':p,'summary':s,'metadata':meta};(R/f'results/{prefix}.json').write_text(json.dumps(rec,indent=2));np.savez_compressed(R/f'results/{prefix}.npz',spikes=r['spike_counts_1ms'],voltage=r['voltage_first12'],body_ids=[int(x['bodyId']) for x in meta]);print('Rhythmic MN',s['rhythmic_MN'],flush=True)
