"""Real MANC motor-command→chief9A subgraph, shared biophysical prior.
No hook/claw EM neurons are fabricated in this upstream graph.
"""
from pathlib import Path
import json,hashlib,sys,platform
from importlib.metadata import version
import numpy as np
from scipy import sparse
from grouped_parameters import group_key
from network import simulate_network
R=Path(__file__).parent;B=R/'results/sensory-command-context';O=R/'results/sensory-command-probes';O.mkdir(exist_ok=True);mode=sys.argv[1];m=json.load(open(B/'neurons.json'));W=sparse.load_npz(B/'connectivity.npz');p=json.load(open(R/'configs/manual-neural-bank-r9.json'))['parameters'];p=json.loads(json.dumps(p));available={group_key(x) for x in m};p['group_parameters']={k:v for k,v in p['group_parameters'].items() if k in available};p.update(duration_ms=1600.,onset_ms=200.,dt_ms=.0125)
for x in m:
 if x['bodyId'] in ['10093','10339','10107','10103']:
  key=group_key(x);p['group_parameters'][key]={**p['group_parameters'].get(key,{}),'K':.8,'axon_bias_pA':5.}
lookup={x['bodyId']:i for i,x in enumerate(m)};chief=['100513','13157','14517','165560','12443','12804'];drive=np.zeros(len(m));ablate=[]
if mode in ['motor','motor_web','motor_chief_off']:
 for b in ['10093','10339']:drive[lookup[b]]=160.
if mode=='motor_web':
 for b in ['10107','10103']:drive[lookup[b]]=160.
if mode=='motor_chief_off':ablate=[lookup[b] for b in chief]
if mode=='chief_LF':drive[lookup['100513']]=160.
if mode not in ['passive','motor','motor_web','motor_chief_off','chief_LF']:raise ValueError(mode)
config={'mode':mode,'parameters':p,'parameter_sha256':hashlib.sha256(json.dumps(p,sort_keys=True).encode()).hexdigest(),'stimulated_body_ids':[m[i]['bodyId'] for i in np.flatnonzero(drive)],'ablated_body_ids':[m[i]['bodyId'] for i in ablate],'input_current_pA':160.,'input_on_ms':200.,'input_off_ms':1600.,'graph_sha256':hashlib.sha256((B/'connectivity.npz').read_bytes()).hexdigest(),'metadata_sha256':hashlib.sha256((B/'neurons.json').read_bytes()).hexdigest(),'code_hashes':{n:hashlib.sha256((R/n).read_bytes()).hexdigest() for n in ['model.py','network.py','grouped_parameters.py','sensory_command_probe.py']},'command':[sys.executable,*sys.argv],'python':platform.python_version(),'versions':{n:version(n) for n in ['numpy','scipy','numba']},'randomness':'deterministic','status':'started; no fitted output or phase forcing'};(O/(mode+'-config.json')).write_text(json.dumps(config,indent=2)+'\n');r=simulate_network(W.toarray(),['other']*len(m),m,p,drive=drive,ablate=ablate,record_indices=np.arange(len(m)));n=r['valid_record_count'];tmp=O/(mode+'.npz.tmp')
with tmp.open('wb') as f:np.savez_compressed(f,spikes=r['spike_counts_1ms'],body_ids=[x['bodyId'] for x in m],voltage=r['voltage_first12'][:n],calcium=r['calcium_first12_uM'][:n],currents=r['synaptic_currents_pA'][:n],time_ms=r['record_time_ms'],cell_parameters=r['cell_parameters'])
tmp.replace(O/(mode+'.npz'));summary={'condition':mode,'numerical_failure':r['numerical_failure'],'chief9A':[{'body_id':b,'current_type':m[lookup[b]]['type'],'rate_after400ms_hz':float(r['spike_counts_1ms'][400:,lookup[b]].sum()/1.2)} for b in chief],'status':'real-cell upstream simulation; sensory prototype not part of connectome count'};(O/(mode+'-diagnosis.json')).write_text(json.dumps(summary,indent=2)+'\n');print(summary,flush=True)
