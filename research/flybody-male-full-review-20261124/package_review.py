"""Small review/fix bundle; preserve original model as an existing public Release asset."""
from pathlib import Path
import hashlib,json,zipfile,subprocess
R=Path(__file__).resolve().parent;ROOT=R.parents[1];P=R/'cache/extracted/flybody_male_full';D=R/'cache/delivery';D.mkdir(parents=True,exist_ok=True);asset=D/'Flybody_Review_And_Fixes.zip';files={}
for p in R.iterdir():
 if p.suffix in ['.py','.json','.md'] and p.name not in ['artifact-transport.json','delivery-status.json','manifest.json']:files[p.name]=p
for p in (R/'fixes').rglob('*'):
 if p.is_file() and '__pycache__' not in p.parts:files[str(p.relative_to(R))]=p
for name in ['neural_rerun_delta.npz','background_only.npz','sensory_plus_background.npz']:files['data/'+name]=R/'cache'/name
for name in ['body_state.npz','full_physical_rollout.npz']:files['data/'+name]=P/'04_results/data'/name
for p in (P/'04_results/videos').glob('*.mp4'):files['videos/'+p.name]=p
files['videos/review_frame.png']=R/'cache/review_frame.png'
content={k:{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for k,p in files.items()}
with zipfile.ZipFile(asset,'w') as z:
 for k,p in sorted(files.items()):z.write(p,k,compress_type=zipfile.ZIP_STORED if p.suffix in ['.npz','.mp4','.png'] else zipfile.ZIP_DEFLATED)
 z.writestr('CONTENTS_SHA256.json',json.dumps(content,indent=2),compress_type=zipfile.ZIP_DEFLATED)
with zipfile.ZipFile(asset) as z:assert z.testzip() is None
assets=[asset,P/'04_results/videos/03_synchronized.mp4',R/'cache/review_frame.png'];base='https://github.com/linzhefeng24/Applepie/releases/download/flybody-review-20261124/';manifest={'status':'local_bundle_verified_pending_publication','source_revision':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'original_user_model':json.loads((R/'input_manifest.json').read_text()),'delivery_assets':[{'name':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size,'url':base+p.name} for p in assets],'scope':'Scoped independent validation, reporting-only patches and regenerated labeled videos. Canonical neural/body parameters unchanged. Original reference plus exact XOR delta restores the independently rerun state.'};(R/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
with zipfile.ZipFile(D/'Flybody_Review_Transport.zip','w',zipfile.ZIP_STORED) as z:
 for p in assets:z.write(p,p.name)
print(json.dumps(manifest,indent=2))
