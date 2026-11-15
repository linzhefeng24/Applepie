"""Hash local evidence and derived artifacts; large raw arrays use Release refs."""
from pathlib import Path
import hashlib,json,subprocess
R=Path(__file__).parent;rows=[]
for p in sorted(R.rglob('*')):
 if not p.is_file() or '__pycache__' in p.parts or p.name=='artifact-manifest.json':continue
 rows.append({'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
d={'status':'new literature retrieval, source identity and independently rerun/inspected artifacts','parent_revision':subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),'large_raw_data':'full-trace-release.json; remote-local-equivalence.json verifies identical NPZ bytes','randomness':'simulations deterministic; no random draws','files':rows};(R/'artifact-manifest.json').write_text(json.dumps(d,indent=2)+'\n')
