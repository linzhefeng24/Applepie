"""Materialize one standalone model.yaml from a verified base and shared patch.
The resolved cell array remains the only operational parameter table. Factors
and source hashes are audit provenance; no old trajectory is added to inputs.
"""
from pathlib import Path
import argparse,base64,hashlib,io,json,sys
import numpy as np
import yaml
R=Path(__file__).resolve().parent;ROOT=R.parents[1]
sys.path.insert(0,str(ROOT/'research/single-model-delivery-20261115/runtime/02_code'));sys.path.insert(0,str(ROOT/'research/conductance-rebuild-20261114'))
from flymodel import Model
from grouped_parameters import group_key
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--base',type=Path,required=True);p.add_argument('--patch',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
if a.output.resolve()==a.base.resolve():raise ValueError('Keep the baseline file immutable')
m=Model(a.base);patch=json.loads(a.patch.read_text());assert patch['baseline_model_sha256']==m.sha256
assert patch['baseline_cell_array_sha256']==hashlib.sha256(m.cells.tobytes()).hexdigest()
columns=m.config['neural']['cell_parameter_columns'];assert [columns[i] for i in patch['field_indices']]==patch['field_names']
for i,row in enumerate(m.neurons):
 delta=patch['group_relative_factors'].get(group_key(row))
 if delta is not None:
  delta=np.asarray(delta);assert np.isfinite(delta).all() and np.max(abs(delta))<=.2+1e-12
  m.cells[i,patch['field_indices']]*=1+delta
assert hashlib.sha256(m.cells.tobytes()).hexdigest()==patch['candidate_cell_array_sha256']
b=io.BytesIO();np.savez_compressed(b,values=m.cells);raw=b.getvalue();m.config['neural']['cell_parameters']={'encoding':'base64_npz_no_pickle','sha256':hashlib.sha256(raw).hexdigest(),'payload':base64.b64encode(raw).decode()}
m.config['identity']['name']='MaleCNS3988_R2_regularized_surrogate_BPTT_candidate';m.config['identity']['baseline_model_sha256']=m.sha256;m.config['identity']['parameter_patch_sha256']=hashlib.sha256(a.patch.read_bytes()).hexdigest()
m.config['parameter_provenance']['regularized_BPTT']={'kind':'model_fit_not_measured_physiology','method':'shared-type surrogate-gradient BPTT; local replay-boundary training then full original hard-network validation','relative_bound':.2,'regularization':'0.1 * mean(relative_shift**2)','selected_checkpoint_epoch':patch['checkpoint_epoch'],'max_relative_change':patch['max_relative_change'],'scope':'No anatomy, transmitter sign, muscle parameters or NMJ readout changes. Not proof of all laboratory phenomena or left-right alternation.'}
a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text('# Standalone bounded BPTT candidate; see parameter_provenance and original limitations.\n'+yaml.dump(m.config,Dumper=yaml.CSafeDumper,allow_unicode=True,sort_keys=False,width=120))
check=Model(a.output);assert np.array_equal(check.cells,m.cells)
print(json.dumps({'file':str(a.output),'bytes':a.output.stat().st_size,'sha256':check.sha256,'cell_array_sha256':hashlib.sha256(check.cells.tobytes()).hexdigest()},indent=2))
