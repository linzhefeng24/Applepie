"""Build one runnable selected network + all raw condition outputs; no private transcript."""
from pathlib import Path
import hashlib,json,subprocess,zipfile
R=Path(__file__).resolve().parent;ROOT=R.parents[1];P=ROOT/'research/manual-full-rerun-20261119/cache/extracted/Manual_FreeBody';D=R/'cache/delivery';D.mkdir(parents=True,exist_ok=True);bundle=D/'Selected_Core_Extension.zip'
files={'01_model/model.yaml':R/'cache/selected_manual_model.yaml','02_code/run_selected_neural.py':R/'run_selected_neural.py','README_zh.md':R/'README.md'}
for f in (P/'02_code/flymodel').glob('*.py'):files['02_code/flymodel/'+f.name]=f
for f in R.iterdir():
 if f.suffix in {'.json','.tsv','.py','.npz'} and f.name not in {'artifact-transport.json','manifest.json','delivery-status.json'}:files['03_evidence/'+f.name]=f
for f in (R/'results').iterdir():
 if f.suffix in {'.json','.npz'}:files['04_results/'+f.name]=f
files['04_results/core-and-muscle-traces.png']=R/'core-and-muscle-traces.png'
assert len(list((R/'results').glob('*.npz')))==17
with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for name,f in sorted(files.items()):z.write(f,name)
 z.writestr('CONTENTS_SHA256.json',json.dumps({k:{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for k,p in sorted(files.items())},indent=2))
with zipfile.ZipFile(bundle) as z:assert z.testzip() is None
assets=[bundle,R/'core-and-muscle-traces.png',R/'phenomena_status.json'];base='https://github.com/linzhefeng24/Applepie/releases/download/manual-core-extension-20261119/'
manifest={'status':'local_bundle_verified_pending_publication','source_revision':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'delivery_assets':[{'name':f.name,'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'url':base+f.name} for f in assets],'original_manual_package':{'url':'https://github.com/linzhefeng24/Applepie/releases/download/manual-r2-freebody-20261119/Manual_R2_FreeBody_Complete.zip','bytes':93825131,'sha256':'e7b47bb6804f2f7f121b5569fa8b45e287d3a0d827e93195bd9f54a76e5a8cb8'},'scope':'one selected network model, code, 17 raw conditions; no newly rendered body video'}
(R/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
with zipfile.ZipFile(D/'Core_Extension_Transport.zip','w',zipfile.ZIP_STORED) as z:
 for f in assets:z.write(f,f.name)
print(json.dumps(manifest,indent=2))
