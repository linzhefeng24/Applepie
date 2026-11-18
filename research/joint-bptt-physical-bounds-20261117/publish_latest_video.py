"""Public intermediate-video assets and fresh-download-verified provenance."""
from pathlib import Path
import base64,hashlib,json,os,subprocess,sys,time
out=Path(sys.argv[1]);report=json.loads((out/'evaluation.json').read_text());epoch=report['completed_main_updates'];repo=os.environ['GITHUB_REPOSITORY'];variant='-reference' if report.get('reference_added') else '';tag=f'joint-physical-latest-20261118-e{epoch:04d}'+variant
def gh(*args,check=True):return subprocess.run(['gh',*args],check=check,capture_output=True,text=True)
assets=[p for p in out.iterdir() if p.suffix in ['.mp4','.zip','.jpg','.json']];manifest={'completed_main_updates':epoch,'selected_bank':report['selected_bank'],'render_code_revision':report['render_code_revision'],'source_checkpoint_sha256':report['source_checkpoint']['sha256'],'assets':[{'name':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size,'url':f'https://github.com/{repo}/releases/download/{tag}/{p.name}'} for p in assets]}
mp=out/'manifest.json';mp.write_text(json.dumps(manifest,indent=2)+'\n');assets.append(mp)
gh('release','create',tag,'--repo',repo,'--draft','--target',report['render_code_revision'],'--title',f'Joint BPTT update{epoch}: native AB video preview','--notes','Actual intermediate checkpoint, not completion of300 updates. Latest raw bank, not the best bank on original free-body AB dynamics; reference/direct-A/manual/latest comparison. Complete0.4s at10x slow motion.')
gh('release','upload',tag,*map(str,assets),'--repo',repo)
verify=out/'verify';verify.mkdir(exist_ok=True)
for item in manifest['assets']:
 gh('release','download',tag,'--repo',repo,'--pattern',item['name'],'--dir',str(verify),'--clobber');assert hashlib.sha256((verify/item['name']).read_bytes()).hexdigest()==item['sha256']
gh('release','edit',tag,'--repo',repo,'--draft=false')
for local,name in [(mp,f'latest-preview-{epoch}{variant}-manifest.json'),(out/'evaluation.json',f'latest-preview-{epoch}{variant}-evaluation.json')]:
 path='research/joint-bptt-physical-bounds-20261117/'+name
 for attempt in range(8):
  old=gh('api','-H','Cache-Control: no-cache',f'repos/{repo}/contents/{path}?ref=main&nonce={time.time_ns()}',check=False);payload={'message':f'Save native video preview at actual update{epoch}','branch':'main','content':base64.b64encode(local.read_bytes()).decode()}
  if old.returncode==0:payload['sha']=json.loads(old.stdout)['sha']
  elif '404' not in old.stderr:raise RuntimeError(old.stderr)
  request=out/'commit-payload.json';request.write_text(json.dumps(payload));answer=gh('api','--method','PUT',f'repos/{repo}/contents/{path}','--input',str(request),check=False)
  if answer.returncode==0:break
  if attempt==7:raise RuntimeError(answer.stderr)
  time.sleep(min(2**attempt,8))
 fresh=json.loads(gh('api','-H','Cache-Control: no-cache',f'repos/{repo}/contents/{path}?ref=main&nonce={time.time_ns()}').stdout);assert base64.b64decode(fresh['content'])==local.read_bytes()
print(json.dumps(manifest,indent=2))
