"""Write a full model from the explicit selected parameter document, then verify trial identity."""
from pathlib import Path
import hashlib,json,os,sys,numpy as np,yaml
from build import encode
R=Path(__file__).resolve().parent;P=Path(os.environ.get('MANUAL_R2_PACKAGE',str(R.parents[1]/'research/manual-full-rerun-20261119/cache/extracted/Manual_FreeBody')));sys.path.insert(0,str(P/'02_code'));from flymodel import Model
m=Model(R/'cache/extended_model.yaml');selection=json.loads((R/'selected_trial.json').read_text());assert m.sha256==selection['base_model_sha256'];cols=m.config['neural']['cell_parameter_columns'];changed=[]
for q in selection['updates']:
 assert q['parameter'] in cols,cols
 j=cols.index(q['parameter'])
 for i,n in enumerate(m.neurons):
  if n.get('type')==q['type']:m.cells[i,j]=q['value'];changed.append(m.ids[i])
expected=json.loads((R/'results/I1_exc_x2.json').read_text());assert hashlib.sha256(m.cells.tobytes()).hexdigest()==expected['cell_parameters_sha256']
m.config['neural']['cell_parameters']=encode(values=m.cells);m.config['parameter_provenance']['selected_manual_trial']=selection
p=R/'cache/selected_manual_model.yaml'
with p.open('w') as f:yaml.dump(m.config,f,Dumper=yaml.CSafeDumper,sort_keys=False,allow_unicode=True)
np.savez_compressed(R/'selected_manual_parameters.npz',cell_parameters=m.cells,global_parameters=m.global_values,HH_kinetics=m.kinetics,body_ids=np.array(m.ids))
report={'selected_model_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'cell_array_sha256':hashlib.sha256(m.cells.tobytes()).hexdigest(),'matches_run':'I1_exc_x2','changed_ids':changed,'parameter_origin':'manual_not_measured','not_a_replacement_for_original_R2':True};(R/'selected_model_manifest.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
