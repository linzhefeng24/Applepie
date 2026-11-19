"""Standalone network entry: from initial state to spikes, arbitrary cell states and u(t).
All physiological parameters are read from the packaged model, not defined here.
"""
from pathlib import Path
import argparse,json,numpy as np
from flymodel import Model
p=argparse.ArgumentParser();p.add_argument('--model',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--record',nargs='*',default=['10045','10056','800173','800863','801884','800288','903216','803183']);a=p.parse_args()
m=Model(a.model);r=m.run_neural(record_ids=a.record);r['u']=m.muscle_excitation(r);a.output.parent.mkdir(parents=True,exist_ok=True);np.savez_compressed(a.output,**r);print(json.dumps({'model_sha256':m.sha256,'spikes':int(r['spikes'].sum()),'u_shape':list(r['u'].shape),'recorded_ids':a.record,'file':str(a.output)}))
