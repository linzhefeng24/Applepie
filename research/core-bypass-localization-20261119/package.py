"""Archive all 29 exact-step/state traces and reproducible interventions.
Input selected model is referenced by immutable published asset, not duplicated.
"""
from pathlib import Path
import hashlib,json,subprocess,zipfile
R=Path(__file__).resolve().parent;ROOT=R.parents[1];D=R/'cache/delivery';D.mkdir(parents=True,exist_ok=True);asset=D/'Core_Bypass_Diagnostics.zip';files={}
for p in R.iterdir():
 if p.suffix in {'.py','.json','.png','.md'} and p.name not in {'artifact-transport.json','manifest.json','delivery-status.json'}:files['research/core-bypass-localization-20261119/'+p.name]=p
for p in (R/'results').iterdir():
 if p.suffix in {'.json','.npz'}:files['research/core-bypass-localization-20261119/results/'+p.name]=p
assert len(list((R/'results').glob('*.npz')))==29
content={k:{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size} for k,p in sorted(files.items())}
with zipfile.ZipFile(asset,'w') as z:
 for k,p in sorted(files.items()):z.write(p,k,compress_type=zipfile.ZIP_STORED if p.suffix=='.npz' else zipfile.ZIP_DEFLATED,compresslevel=6)
 z.writestr('CONTENTS_SHA256.json',json.dumps(content,indent=2),compress_type=zipfile.ZIP_DEFLATED)
with zipfile.ZipFile(asset) as z:assert z.testzip() is None
assets=[asset,R/'local-core-rhythm.png',R/'phenomena_status.json'];base='https://github.com/linzhefeng24/Applepie/releases/download/core-bypass-localization-20261119/';prior=json.loads((ROOT/'research/manual-extension-review-20261119/manifest.json').read_text());model_asset=next(x for x in prior['delivery_assets'] if x['name']=='Selected_Core_Extension.zip');manifest={'status':'local_verified_pending_publication','source_revision':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'input_model_sha256':'38b07321a54694dc875aebfaa82c930cd752bd0d25f2940ef7087fa45a44e4fa','input_model_asset':model_asset,'delivery_assets':[{'name':p.name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'url':base+p.name} for p in assets],'scope':'29 independent diagnostic conditions, original full-resolution states and exact event logs; previous canonical model unchanged; local model slow rhythm is not full-network behavior reproduction.'};(R/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
with zipfile.ZipFile(D/'Core_Bypass_Transport.zip','w',zipfile.ZIP_STORED) as z:
 for p in assets:z.write(p,p.name)
print(json.dumps(manifest,indent=2))
