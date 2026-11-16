"""Create a small additive code ZIP only after full numerical/memory validation."""
from pathlib import Path
import argparse,hashlib,json,subprocess,zipfile
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();validation=json.loads((HERE/'validation.json').read_text())
assert validation['numerical_parity_passed'] and validation['physical_steps']==4000 and validation['neural_ms']==1400
assert validation['memory']['conservative_parent_plus_largest_worker_peak_kib']<6.5*1024*1024,'Do not advertise a7.5GiB mode before the6.5GiB process upper bound is met'
assert json.loads((HERE/'entry-check.json').read_text())['passed']
a.out.mkdir(parents=True,exist_ok=True);asset=a.out/'Applepie_LowMemory_Addon.zip';files=[]
for f in sorted(HERE.iterdir()):
 if f.is_file() and f.suffix in ['.py','.json','.npz','.md']:files.append((f,'lowmem/'+f.name))
files.append((HERE/'run_lowmem.sh','run_lowmem.sh'))
source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();contents=[{'path':name,'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f,name in files]
with zipfile.ZipFile(asset,'w',zipfile.ZIP_DEFLATED) as z:
 for f,name in files:
  assert name.startswith('lowmem/') or name=='run_lowmem.sh'
  z.write(f,name)
 z.writestr('LOW_MEMORY_MANIFEST.json',json.dumps({'code_revision':source,'files':contents,'original_model_files_overwritten':False,'validation':validation},indent=2)+'\n')
manifest={'name':asset.name,'sha256':hashlib.sha256(asset.read_bytes()).hexdigest(),'bytes':asset.stat().st_size,'code_revision':source,'source_url':'https://github.com/linzhefeng24/Applepie/releases/download/server-joint-bptt-20261116/'+asset.name,'validation':validation}
(a.out/'lowmem-addon-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(manifest,indent=2))
