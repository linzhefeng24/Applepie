"""Archive only hash-pinned public inputs to a draft GitHub Release.
Uses the runner's ephemeral repository token via gh; no credentials are saved.
Existing assets are verified and never replaced. This runs no downloaded code.
"""
import hashlib,json,os,subprocess,tempfile,urllib.request
from pathlib import Path
from urllib.parse import urlparse
ROOT=Path(__file__).parent
TAG='public-neural-inputs-20261115'
def gh(*args):
 return subprocess.check_output(['gh',*args],text=True)
def sha(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for chunk in iter(lambda:f.read(4*1024*1024),b''):h.update(chunk)
 return h.hexdigest()
def main():
 manifest=json.loads((ROOT/'inputs.json').read_text());repo=os.environ['GITHUB_REPOSITORY'];rev=os.environ['GITHUB_SHA']
 release=subprocess.run(['gh','release','view',TAG,'--repo',repo],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 if release.returncode:gh('release','create',TAG,'--repo',repo,'--draft','--target',rev,'--title','Pinned public neural research inputs','--notes','Raw public source inputs; SHA-256 and scientific code revision are recorded in the asset manifest. Draft archive only.')
 verified=[]
 with tempfile.TemporaryDirectory() as directory:
  for item in manifest['inputs']:
   u=urlparse(item['source_url'])
   if u.scheme!='https' or u.hostname not in {'storage.googleapis.com','static-content.springer.com'}:raise ValueError('Unexpected source host')
   if Path(item['name']).name!=item['name']:raise ValueError('Unsafe asset name')
   path=Path(directory)/item['name'];assets=json.loads(gh('api',f'repos/{repo}/releases/tags/{TAG}'))['assets'];existing=next((a for a in assets if a['name']==item['name']),None)
   if not existing:
    with urllib.request.urlopen(item['source_url'],timeout=180) as src,path.open('wb') as dst:
     for chunk in iter(lambda:src.read(4*1024*1024),b''):dst.write(chunk)
    if path.stat().st_size!=item['bytes'] or sha(path)!=item['sha256']:raise ValueError('Public download identity mismatch: '+item['name'])
    gh('release','upload',TAG,str(path),'--repo',repo)
    assets=json.loads(gh('api',f'repos/{repo}/releases/tags/{TAG}'))['assets'];existing=next(a for a in assets if a['name']==item['name'])
   if existing['size']!=item['bytes']:raise ValueError('Existing asset size mismatch')
   if existing.get('digest')!='sha256:'+item['sha256']:
    gh('release','download',TAG,'--repo',repo,'--pattern',item['name'],'--dir',directory,'--clobber')
    if sha(path)!=item['sha256']:raise ValueError('Existing asset hash mismatch')
   verified.append({**item,'asset_id':existing['id'],'release_tag':TAG,'release_asset_url':existing['browser_download_url'],'release_api_url':existing['url'],'verified_sha256':item['sha256']});print('Verified',item['name'],flush=True)
   path.unlink(missing_ok=True)
  output={'status':'verified by fresh GitHub asset metadata or downloaded asset hash','archive_workflow_revision':rev,'neural_code_revision':manifest['neural_code_revision'],'inputs':verified};path=Path(directory)/('verified-inputs-'+rev+'.json');path.write_text(json.dumps(output,indent=2)+'\n');gh('release','upload',TAG,str(path),'--repo',repo)
if __name__=='__main__':main()
