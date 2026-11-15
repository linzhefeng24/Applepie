"""Build a self-contained distribution using the verified fixed-body release.

There is exactly one parameter/model file. Existing fixed-body trajectories and
videos are reused by hash, and the matching full neural state is included.
"""
from pathlib import Path
import hashlib,json,os,shutil,subprocess,zipfile,platform
from importlib.metadata import version
import numpy as np
R=Path(__file__).resolve().parent
D=R.parent/'single-model-delivery-20261115'
P=D/'build/UnifiedFlyModel'
F=R/'build/fixed-results'
F.mkdir(parents=True,exist_ok=True)
asset=R/'build/FixedBody_20261115.zip'
expected=json.loads((R/'fixed-input-manifest.json').read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(asset)==expected['sha256'] and asset.stat().st_size==expected['bytes']
with zipfile.ZipFile(asset) as z:
 assert z.testzip() is None
 for name in z.namelist():assert not Path(name).is_absolute() and '..' not in Path(name).parts
 z.extractall(F)
fixed=json.loads((F/'report.json').read_text())
assert fixed['model_sha256']==sha(P/'01_model/model.yaml')
assert fixed['neural_input_sha256']==sha(P/'04_results/data/neural_state.npz')
with np.load(P/'04_results/data/neural_state.npz',allow_pickle=False) as z:
 assert str(z['run_id'])==fixed['neural_run_id']
with np.load(F/'body_state.npz',allow_pickle=False) as z:
 assert bool(z['fixed_root']) and str(z['neural_run_id'])==fixed['neural_run_id']
 assert np.isfinite(z['qpos']).all()
assert fixed['position_max_drift_native']==fixed['quaternion_max_drift']==0
assert fixed['ground_normal_force_max_native']>0
shutil.copy2(F/'body_state.npz',P/'04_results/data/body_state.npz')
if (P/'04_results/videos').exists():shutil.rmtree(P/'04_results/videos')
shutil.copytree(F/'videos',P/'04_results/videos')
shutil.copy2(D/'source-equivalence.json',P/'04_results/source_equivalence.json')
fixed['assembly_environment']={'python':platform.python_version(),'versions':{x:version(x) for x in ['numpy','scipy','numba','mujoco','PyYAML','matplotlib','imageio-ffmpeg']}}
fixed['artifact_scope']='Fixed initial body pose, full model and neural data; not free walking.'
fixed['reused_fixed_asset_sha256']=expected['sha256']
fixed['videos']=['videos/'+p.name for p in sorted((P/'04_results/videos').glob('*.mp4'))]
(P/'04_results/verification.json').write_text(json.dumps(fixed,indent=2)+'\n')
ph=P/'03_phenomena/phenomena.json';phenomena=json.loads(ph.read_text())
phenomena['packaged_demo_condition']='Externally fixed initial body position and orientation; native legs, gravity and foot-ground contact.'
phenomena['fully_reproduced_laboratory_experiments']=[]
for x in phenomena['can_complete_in_stated_scope']:
 if x['id']=='DN_to_muscle_forward_simulation':x.update(status='verified_supported_body_forward_simulation',evidence='../04_results/verification.json')
ph.write_text(json.dumps(phenomena,indent=2,ensure_ascii=False)+'\n')
audit=R.parent/'rhythm-pathway-audit-20261115'
for name in ['report.json','signals.png']:
 shutil.copy2(audit/name,P/'03_phenomena'/('rhythm_audit_'+name))
for name in ['run_demo.sh','run_demo.bat']:
 p=P/name;p.write_text(p.read_text().replace('run.py demo','run.py demo --fixed-body'))
p=P/'README.md';text=p.read_text().replace('python 02_code/run.py demo --experiment DN_drive\n','python 02_code/run.py demo --experiment DN_drive --fixed-body\n')
p.write_text('本完整包可独立运行，无需之前的8MB结果包。默认启动脚本生成固定身体版本：躯干固定于初始位置与姿态，腿部自由，地面碰撞、摩擦和接触力保留。去掉`--fixed-body`可运行自由身体实验。\n\n'+text)
for p in P.rglob('__pycache__'):shutil.rmtree(p)
revision=os.environ.get('GITHUB_SHA') or subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()
manifest={'schema':'unified_fly_full_fixed_delivery_v1','code_revision':revision,'model_sha256':fixed['model_sha256'],'source_fixed_asset_url':expected['source_url'],'source_fixed_asset_sha256':expected['sha256'],'contents':[{'path':str(p.relative_to(P)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(P.rglob('*')) if p.is_file() and p.name!='MANIFEST.json']}
(P/'MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
out=R/'dist';out.mkdir(exist_ok=True)
archive=out/'UnifiedFlyModel_Full_20261115.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in sorted(P.rglob('*')):
  if p.is_file():z.write(p,str(p.relative_to(P.parent)))
meta={'file':archive.name,'bytes':archive.stat().st_size,'sha256':sha(archive),'code_revision':revision,'model_sha256':fixed['model_sha256'],'contents':'one complete model.yaml with geometry/meshes/parameters; full runnable code; phenomena JSON; neural and muscle/body states; three fixed-body videos; provenance and per-file checksums','condition':'fixed initial body pose with native leg and ground contact dynamics','source_fixed_asset_sha256':expected['sha256']}
(out/'UnifiedFlyModel_Full_20261115.manifest.json').write_text(json.dumps(meta,indent=2)+'\n')
print(json.dumps(meta,indent=2))
