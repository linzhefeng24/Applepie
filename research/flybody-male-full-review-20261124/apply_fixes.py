"""Apply reporting/launcher fixes only to the exact reviewed model; preserve backups."""
from pathlib import Path
import argparse,hashlib,json,shutil
R=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
p=argparse.ArgumentParser();p.add_argument('package',type=Path,help='Extracted flybody_male_full root');a=p.parse_args();root=a.package.resolve();spec=json.loads((R/'patch_manifest.json').read_text());assert sha(root/'01_model/model.yaml')==spec['expected_model_sha256'],'Different model: patch not applied';assert sha(root/'01_model/body_parameters.yaml')==spec['expected_body_sha256'],'Different body model: patch not applied';manifest=root/'FILE_MANIFEST.json';records=json.loads(manifest.read_text());backup=root/'review_backup_20261124'
for q in spec['fixes']:
 assert sha(root/q['file']) in [q['original_sha256'],q['fixed_sha256']],q['file']+' changed since review'
for q in spec['fixes']:
 target=root/q['file'];current=sha(target);assert current in [q['original_sha256'],q['fixed_sha256']],q['file']+' changed since review'
 if current==q['original_sha256']:
  dst=backup/q['file'];dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(target,dst);shutil.copy2(R/'fixes'/q['file'],target)
 assert sha(target)==q['fixed_sha256'];records[q['file']]={'sha256':sha(target),'bytes':target.stat().st_size}
manifest.write_text(json.dumps(records,indent=2)+'\n');print('Applied code/reporting fixes. Neural and body parameter files unchanged; backups:',backup)
