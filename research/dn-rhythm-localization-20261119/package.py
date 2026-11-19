from pathlib import Path
import hashlib,json,zipfile,shutil
R=Path(__file__).resolve().parent;D=R/'cache/delivery';D.mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
s=json.loads((R/'summary.json').read_text());assert s['case_count']==22
raw=list((R/'cache').glob('*.npz'));assert len(raw)==22
for case in s['cases']:
 p=R/'cache'/case['trace']['name'];assert sha(p)==case['trace']['sha256'] and p.stat().st_size==case['trace']['bytes']
bundle=D/'DN_Rhythm_Localization_Data.zip'
with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED) as z:
 for p in raw:z.write(p,p.name)
 for p in R.iterdir():
  if p.is_file() and p.suffix in ['.json','.py','.md','.png'] and p.name not in ['manifest.json','artifact-transport.json','delivery-status.json']:z.write(p,p.name)
with zipfile.ZipFile(bundle) as z:assert z.testzip() is None
for name in ['localization.png','summary.json']:shutil.copyfile(R/name,D/name)
assets=[{'name':p.name,'sha256':sha(p),'bytes':p.stat().st_size,'url':'https://github.com/linzhefeng24/Applepie/releases/download/dn-rhythm-localization-20261119/'+p.name} for p in sorted(D.iterdir())]
(R/'manifest.json').write_text(json.dumps({'status':'prepared_for_release','delivery_assets':assets,'scope':'22 full-network diagnostic interventions plus6small circuits; no parameter optimization'},indent=2)+'\n');print([(x['name'],x['bytes']) for x in assets])
