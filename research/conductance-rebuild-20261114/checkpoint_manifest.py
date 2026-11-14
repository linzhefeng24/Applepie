"""Hash versioned and nonignored experiment artifacts, excluding this manifest."""
from pathlib import Path
import hashlib,json,subprocess
R=Path(__file__).resolve().parent
paths=subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard','-z','--',str(R)],cwd=R).decode().split('\0')
root=Path(subprocess.check_output(['git','rev-parse','--show-toplevel'],cwd=R).decode().strip());records=[]
for name in sorted(set(paths)):
 p=root/name
 if not name or p.name=='artifact-manifest.json' or not p.is_file():continue
 b=p.read_bytes();records.append({'path':str(p.relative_to(R)),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
(R/'artifact-manifest.json').write_text(json.dumps({'scope':'Tracked and nonignored experiment files; excludes itself and ignored caches','artifacts':records},indent=2)+'\n')
