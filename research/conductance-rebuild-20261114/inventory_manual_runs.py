"""Completed deterministic conditions, never a biological success percentage."""
from pathlib import Path
import json,hashlib
R=Path(__file__).parent;entries=[];motor=[]
for folder in sorted((R/'results').glob('frozen-neural-panel-*')):
 for f in sorted(folder.glob('*-diagnosis.json')):
  d=json.loads(f.read_text());entries.append({'directory':str(folder.relative_to(R)),'case':d['condition'],'bank_sha256':d['bank_sha256'],'numerical_failure':d['numerical_failure']})
for f in sorted((R/'results/manual-mechanism').glob('*-diagnosis.json')):
 d=json.loads(f.read_text())
 if 'cells' in d and 'numerical_failure' in d:motor.append({'diagnosis':str(f.relative_to(R)),'numerical_failure':d['numerical_failure']})
(R/'results/manual-run-inventory.json').write_text(json.dumps({'kind':__doc__,'analysis_code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'complete_frozen_condition_runs':len(entries),'frozen_runs':entries,'complete_regional_motor_runs':len(motor),'regional_motor_runs':motor},indent=2)+'\n');print('Frozen conditions:',len(entries),'regional motor conditions:',len(motor))
