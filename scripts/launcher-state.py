"""Launch cache: paths and source/dependency hashes, never credentials or .env values."""
from pathlib import Path
import hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
STATE=ROOT/'.run/launcher-state.json'
def digest(paths):
 h=hashlib.sha256()
 for p in sorted(set(paths)):
  if p.is_file():h.update(str(p.relative_to(ROOT)).encode());h.update(p.read_bytes())
 return h.hexdigest()
def current():
 dependencies=[ROOT/n for n in ['frontend/package.json','frontend/package-lock.json','quant/requirements.txt','backend/build.sbt','backend/project/build.properties','backend/project/plugins.sbt']]
 sources=[]
 for folder in ['backend/src','frontend/src','quant','config']:
  sources.extend(p for p in (ROOT/folder).rglob('*') if '__pycache__' not in p.parts and p.suffix in {'.scala','.ts','.tsx','.css','.py','.json'})
 sources.extend(ROOT/n for n in ['frontend/config.ts','frontend/vite.config.ts','frontend/index.html'])
 return dict(root=str(ROOT),dependencies=digest(dependencies),sources=digest(sources))
def runtime_exists():
 files=['.venv/bin/python','.run/classpath','frontend/node_modules/.package-lock.json','frontend/dist/index.html']
 if not all((ROOT/n).exists() for n in files):return False
 runtime=subprocess.run([sys.executable,str(ROOT/'scripts/backend-runtime.py'),'check'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode
 if runtime==2:return False
 if runtime!=0 and not all((ROOT/n).exists() for n in ['.tools/sbt-launch.jar','.tools/repositories']):return False
 # Preserve the venv path; resolving its executable symlink would lose its installed packages.
 result=subprocess.run([str(ROOT/'.venv/bin/python'),'-c','import sys;assert (3,12)<=sys.version_info[:2]<(3,14);import numpy,scipy,pandas,pyarrow,psycopg'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 return result.returncode==0
if __name__=='__main__':
 mode=sys.argv[1];now=current()
 if mode=='save':STATE.parent.mkdir(exist_ok=True);STATE.write_text(json.dumps(now,indent=2));raise SystemExit(0)
 try:old=json.loads(STATE.read_text())
 except (OSError,ValueError):raise SystemExit(1)
 if mode=='check':raise SystemExit(0 if old.get('root')==now['root'] and old.get('dependencies')==now['dependencies'] and runtime_exists() else 1)
 if mode=='build-check':raise SystemExit(0 if old.get('sources')==now['sources'] else 1)
 raise SystemExit(2)
