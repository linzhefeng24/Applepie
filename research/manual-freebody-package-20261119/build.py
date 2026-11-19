"""Assemble a standalone manual-R2 free-body replay with immutable source checks.
Original neural parameters and original AB physical parameters are both retained.
The old8MB fixed-body add-on omitted the model; this new bundle includes it.
"""
from pathlib import Path
import shutil,json,zipfile,hashlib
R=Path(__file__).resolve().parent;ROOT=R.parents[1];P=R/'cache/Manual_FreeBody';P.mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
base=ROOT/'research/single-model-delivery-20261115/build/UnifiedFlyModel';model=base/'01_model/model.yaml';neural=base/'04_results/data/neural_state.npz';archive=ROOT/'research/assets/flymimic-legacy-AB-twofile.zip'
assert sha(model)=='858d1818b8d8394c95bb62a6ce60474cb534a83b94265ef8615e367c110d262c'
assert sha(neural)=='4153fa8f1d29bb1bd987281d68d8407767bb9dd4e2ff1644673218b33e3fc027'
assert sha(archive)=='60a720b2a367556c7408b82d6d63998039b091dab3652ea027fe42f4cb37267a'
for d in ['01_model','02_code','03_phenomena','04_results/data','04_results/videos']:(P/d).mkdir(parents=True,exist_ok=True)
shutil.copyfile(model,P/'01_model/model.yaml');shutil.copyfile(neural,P/'04_results/data/neural_state.npz')
with zipfile.ZipFile(archive) as z:
 (P/'01_model/body_parameters.yaml').write_bytes(z.read('parameters.yaml'));(P/'02_code/native_ab.py').write_bytes(z.read('simulation.py'))
runtime=ROOT/'research/single-model-delivery-20261115/runtime/02_code/flymodel';shutil.copytree(runtime,P/'02_code/flymodel',dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
shutil.copyfile(base/'03_phenomena/phenomena.json',P/'03_phenomena/phenomena.json')
shutil.copyfile(base/'requirements.txt',P/'requirements.txt');shutil.copyfile(R/'run_manual.py',P/'02_code/run_manual.py');shutil.copyfile(R/'replay.yaml',P/'01_model/replay.yaml')
shutil.copyfile(R/'PACKAGE_README.md',P/'README.md')
(P/'run_demo.sh').write_text('#!/usr/bin/env bash\nset -euo pipefail\ncd "$(dirname "$0")"\npython3 02_code/run_manual.py --render\n')
(P/'run_demo.bat').write_text('@echo off\r\ncd /d "%~dp0"\r\npython 02_code\\run_manual.py --render\r\npause\r\n')
manifest={'manual_model_sha256':sha(model),'manual_cells_sha256':'c4d83f204c0ed79cddafd40ebf269f8d9059d6330be38e6b90254a3d36f79ac8','saved_neural_sha256':sha(neural),'native_body_archive_sha256':sha(archive),'native_body_yaml_sha256':sha(P/'01_model/body_parameters.yaml'),'native_body_code_sha256':sha(P/'02_code/native_ab.py'),'manual_parameter_origin':'Pre-BPTT R2, research/brake-retuning-20261115/results/terminal-r2/BRK.npz; no optimizer checkpoint used','source_scope':'Canonical AB body and its initial/warmstart/all11 auxiliary schedules; neural muscle controls replace130 muscle channels','old_package_note':'FixedBody_20261115.zip was an add-on and did not contain model.yaml; this standalone package does','files':{str(p.relative_to(P)):{'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(P.rglob('*')) if p.is_file() and '__pycache__' not in str(p)}}
(P/'01_model/provenance.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');(R/'input-identities.json').write_text(json.dumps({k:v for k,v in manifest.items() if k!='files'},ensure_ascii=False,indent=2)+'\n');print(P)
