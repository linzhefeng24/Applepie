"""Build a self-contained, credential-free CPU benchmark/continuation bundle."""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,zipfile
import numpy as np
import yaml
R=Path(__file__).resolve().parent;ROOT=R.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
parser=argparse.ArgumentParser();parser.add_argument('--checkpoint',type=Path,required=True);parser.add_argument('--metadata',type=Path,required=True);parser.add_argument('--out',type=Path,required=True);a=parser.parse_args()
cfg=json.loads((R/'server/package-config.json').read_text());meta=json.loads(a.metadata.read_text())
assert meta['source_revision']==cfg['training_source_revision']
assert sha(a.checkpoint)==meta['sha256'] and a.checkpoint.stat().st_size==meta['bytes']
assert sha(R/'train_chunk.py')==cfg['trainer_original_sha256']
stage=a.out/'Applepie_Server_JointBPTT';assert not stage.exists(),'Use a fresh output directory';stage.mkdir(parents=True)
def copy(p):
 target=stage/p.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
for p in R.iterdir():
 if p.is_file() and p.suffix in ['.py','.json','.txt','.md']:copy(p)
for p in (R/'server').iterdir():
 if p.is_file():copy(p)
for p in (R/'reference').iterdir():
 if p.is_file():copy(p)
for directory in ['research/physics-bptt-20261116/source','research/single-model-delivery-20261115/runtime']:
 for p in (ROOT/directory).rglob('*'):
  if p.is_file() and '__pycache__' not in p.parts:copy(p)
inputs=['research/single-model-delivery-20261115/build.py','research/single-model-delivery-20261115/phenomena_template.json','research/single-model-delivery-20261115/build/UnifiedFlyModel/01_model/model.yaml','research/conductance-rebuild-20261114/grouped_parameters.py','research/conductance-rebuild-20261114/results/mcns-brake-extension/neurons.json','research/conductance-rebuild-20261114/results/mcns-brake-extension/unsigned-connectivity.npz','research/brake-retuning-20261115/results/terminal-r2/BRK.npz','research/brake-retuning-20261115/configs/brake-terminal-r2.json','research/conductance-rebuild-20261114/data/model-130-channel-candidate-crosswalk.csv','research/conductance-rebuild-20261114/data/phenomena-inventory.json','research/conductance-rebuild-20261114/results/frozen-neural-panel-unified-r9/PFL3L-config.json','research/conductance-rebuild-20261114/results/frozen-neural-panel-brake-extension-r9/BRK-config.json','research/surrogate-bptt-20261115/input-identity.json','research/surrogate-bptt-20261115/archived-baseline.json','research/surrogate-bptt-20261115/baseline-spike-events.npz','research/assets/flymimic-legacy-AB-twofile.zip']
for name in inputs:copy(ROOT/name)
for name in ['setup.sh','setup_auto.sh','run.sh','server.py','README_zh.md']:shutil.copy2(R/'server'/name,stage/name)
checkpoint=stage/'checkpoint';checkpoint.mkdir();shutil.copy2(a.checkpoint,checkpoint/'optimizer.zip');shutil.copy2(a.metadata,checkpoint/'origin.json')
# Offline compatibility only: avoid eagerly executing git when source is supplied.
trainer=stage/R.relative_to(ROOT)/'train_chunk.py';text=trainer.read_text();old="source=os.environ.get('TRAIN_SOURCE_REF',subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip())";new="source=os.environ.get('TRAIN_SOURCE_REF') or subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()";assert text.count(old)==1;trainer.write_text(text.replace(old,new))
# Reconstruct only the verified binned spike baseline, not lost voltages/states.
archive=json.loads((ROOT/'research/surrogate-bptt-20261115/archived-baseline.json').read_text());events=ROOT/'research/surrogate-bptt-20261115/baseline-spike-events.npz';assert sha(events)==archive['sparse_event_file_sha256']
model=stage/'research/single-model-delivery-20261115/build/UnifiedFlyModel/01_model/model.yaml';assert sha(model)==cfg['baseline_model_sha256'];modelcfg=yaml.load(model.read_text(),Loader=yaml.CSafeLoader)
spikes=np.zeros(archive['binned_spikes_shape'],dtype=archive['binned_spikes_dtype'])
with np.load(events,allow_pickle=False) as z:np.add.at(spikes,(np.floor(z['step']*modelcfg['neural']['solver']['dt_ms']).astype(int),z['cell']),1)
assert hashlib.sha256(spikes.tobytes()).hexdigest()==archive['binned_spikes_sha256']
baseline=stage/'research/single-model-delivery-20261115/build/UnifiedFlyModel/04_results/data/neural_state.npz';baseline.parent.mkdir(parents=True,exist_ok=True);np.savez_compressed(baseline,spikes=spikes,artifact_scope=np.array('Verified reconstruction of binned spikes only; not full membrane/state records'))
validation=json.loads((R/'validation-report.json').read_text())
for name,digest in validation['critical_source_sha256'].items():assert sha(stage/R.relative_to(ROOT)/name)==digest,name
files=[]
for p in sorted(stage.rglob('*')):
 if p.is_file():
  raw=p.read_bytes();assert b'lzf'+b'123456' not in raw
  files.append({'path':str(p.relative_to(stage)),'sha256':sha(p),'bytes':p.stat().st_size})
manifest={'package_code_revision':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'training_source_revision':cfg['training_source_revision'],'manual_anchor_model_sha256':cfg['baseline_model_sha256'],'checkpoint':meta,'offline_compatibility_patch':{'file':str(trainer.relative_to(stage)),'original_sha256':cfg['trainer_original_sha256'],'bundled_sha256':sha(trainer),'change':'Lazy git lookup only; numerical loss, regularization, optimizer and model unchanged'},'baseline_reconstruction':'Binned spikes only; independent elementwise-array SHA256 verified against archived baseline; full membrane/state records not claimed','derivative_limitations':validation['limitation'],'files':files}
(stage/'PACKAGE_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
bundle=a.out/cfg['bundle_name']
with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED) as z:
 for p in sorted(stage.rglob('*')):
  if p.is_file():z.write(p,p.relative_to(stage))
asset={'name':bundle.name,'sha256':sha(bundle),'bytes':bundle.stat().st_size,'code_revision':manifest['package_code_revision'],'training_source_revision':cfg['training_source_revision'],'source_url':f"https://github.com/linzhefeng24/Applepie/releases/download/{cfg['github_release_tag']}/{bundle.name}",'input_checkpoint':meta}
(a.out/'server-package-manifest.json').write_text(json.dumps(asset,indent=2)+'\n');print(json.dumps(asset,indent=2))
