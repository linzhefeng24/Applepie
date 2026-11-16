"""Upload verified additive ZIP; commit its immutable hash/size/code manifest."""
from pathlib import Path
import base64,hashlib,json,os,subprocess,sys,time
out=Path(sys.argv[1]);manifest=out/'lowmem-addon-manifest.json';meta=json.loads(manifest.read_text());repo=os.environ['GITHUB_REPOSITORY'];tag='server-joint-bptt-20261116'
def gh(*args,check=True):return subprocess.run(['gh',*args],check=check,capture_output=True,text=True)
asset=out/meta['name'];gh('release','upload',tag,str(asset),str(manifest),'--repo',repo)
verify=out/'verify';verify.mkdir(exist_ok=True);gh('release','download',tag,'--repo',repo,'--pattern',asset.name,'--dir',str(verify),'--clobber');assert hashlib.sha256((verify/asset.name).read_bytes()).hexdigest()==meta['sha256']
destination='research/joint-bptt-300-20261116/lowmem-addon-manifest.json'
for attempt in range(8):
 old=gh('api','-H','Cache-Control: no-cache',f'repos/{repo}/contents/{destination}?ref=main&nonce={time.time_ns()}',check=False);payload={'message':'Save validated low-memory execution add-on manifest','branch':'main','content':base64.b64encode(manifest.read_bytes()).decode()}
 if old.returncode==0:payload['sha']=json.loads(old.stdout)['sha']
 elif '404' not in old.stderr:raise RuntimeError(old.stderr)
 request=out/'request.json';request.write_text(json.dumps(payload));answer=gh('api','--method','PUT',f'repos/{repo}/contents/{destination}','--input',str(request),check=False)
 if answer.returncode==0:break
 if attempt==7:raise RuntimeError(answer.stderr)
 time.sleep(min(2**attempt,8))
fresh=json.loads(gh('api','-H','Cache-Control: no-cache',f'repos/{repo}/contents/{destination}?ref=main&nonce={time.time_ns()}').stdout);assert base64.b64decode(fresh['content'])==manifest.read_bytes();print('Fresh asset and repository manifest verified',meta['source_url'])
