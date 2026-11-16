"""Publish tested server bundle with fresh download verification and committed manifest."""
from pathlib import Path
import base64,hashlib,json,os,subprocess,sys,time
R=Path(__file__).resolve().parent;out=Path(sys.argv[1]);repo=os.environ['GITHUB_REPOSITORY'];cfg=json.loads((R/'server/package-config.json').read_text());tag=cfg['github_release_tag'];source=os.environ['GITHUB_SHA']
def gh(*args,check=True):return subprocess.run(['gh',*args],text=True,capture_output=True,check=check)
manifest=out/'server-package-manifest.json';data=json.loads(manifest.read_text());bundle=out/data['name'];assert hashlib.sha256(bundle.read_bytes()).hexdigest()==data['sha256']
existing=gh('release','view',tag,'--repo',repo,check=False)
if existing.returncode:
 if 'not found' not in existing.stderr.lower():raise RuntimeError(existing.stderr)
 gh('release','create',tag,'--repo',repo,'--draft','--target',source,'--title','Self-contained server joint BPTT code, model and optimizer','--notes','Offline CPU benchmark and independent300-update continuation. Complete model, manual anchor, optimizer snapshot, source hashes and Chinese instructions. Does not stop or overwrite the GitHub training run.')
gh('release','upload',tag,str(bundle),str(manifest),'--repo',repo)
verify=out/'verify';verify.mkdir(exist_ok=True);gh('release','download',tag,'--repo',repo,'--pattern',bundle.name,'--dir',str(verify),'--clobber');assert hashlib.sha256((verify/bundle.name).read_bytes()).hexdigest()==data['sha256']
gh('release','edit',tag,'--repo',repo,'--draft=false')
path='research/joint-bptt-300-20261116/server-package-manifest.json';encoded=base64.b64encode(manifest.read_bytes()).decode()
for attempt in range(8):
 old=gh('api','-H','Cache-Control: no-cache',f'repos/{repo}/contents/{path}?ref=main&nonce={time.time_ns()}',check=False);payload={'message':'Save complete tested server bundle manifest','branch':'main','content':encoded}
 if old.returncode==0:payload['sha']=json.loads(old.stdout)['sha']
 elif '404' not in old.stderr:raise RuntimeError(old.stderr)
 p=out/'manifest-commit.json';p.write_text(json.dumps(payload));answer=gh('api','--method','PUT',f'repos/{repo}/contents/{path}','--input',str(p),check=False)
 if answer.returncode==0:break
 if attempt==7:raise RuntimeError(answer.stderr)
 time.sleep(min(2**attempt,8))
fresh=json.loads(gh('api','-H','Cache-Control: no-cache',f'repos/{repo}/contents/{path}?ref=main&nonce={time.time_ns()}').stdout);assert base64.b64decode(fresh['content'])==manifest.read_bytes();print('Fresh asset download and remote manifest verified:',data['source_url'])
