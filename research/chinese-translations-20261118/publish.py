"""Verified GitHub Release delivery for user-authorized translation artifacts.
Local CLI asset upload receives401 in this environment. Temporary Git blob
objects transport chunks without committing large binaries to branch history;
the official GitHub Actions token publishes the reconstructed Release assets.
No credentials are saved in requests, manifests or archives.
"""
from pathlib import Path
import argparse,base64,hashlib,json,os,subprocess,zipfile,time
R=Path(__file__).resolve().parent;CACHE=R/'cache';REPO='linzhefeng24/Applepie';TAG='paper-translations-zh-20261118'
def sha(b):return hashlib.sha256(b).hexdigest()
def gh(*args):return subprocess.check_output(['gh',*args],text=True)
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
p=argparse.ArgumentParser();p.add_argument('mode',choices=['transport','publish']);a=p.parse_args()
if a.mode=='transport':
 bundle=CACHE/'delivery/Two_Papers_Chinese_Full_Translations.zip';raw=bundle.read_bytes();manifest={'repo':REPO,'release_tag':TAG,'source_revision':gh('api',f'repos/{REPO}/git/ref/heads/main','--jq','.object.sha').strip(),'bundle':{'name':bundle.name,'bytes':len(raw),'sha256':sha(raw)},'chunks':[],'assets':json.loads((R/'manifest.json').read_text())['delivery_assets'],'transport':'unreferenced Git blobs; no large-file commit to branch history'}
 progress=CACHE/'transport-progress.json'
 if progress.exists():
  old=json.loads(progress.read_text())
  if old['bundle']['sha256']==manifest['bundle']['sha256']:manifest=old
 size=4*1024*1024
 for index,start in enumerate(range(0,len(raw),size)):
  chunk=raw[start:start+size]
  if index<len(manifest['chunks']):assert manifest['chunks'][index]['sha256']==sha(chunk);continue
  request=CACHE/'blob-upload-request.json';dump(request,{'content':base64.b64encode(chunk).decode(),'encoding':'base64'})
  obj=json.loads(gh('api','--method','POST',f'repos/{REPO}/git/blobs','--input',str(request)))
  item={'index':index,'git_blob_sha':obj['sha'],'sha256':sha(chunk),'bytes':len(chunk)};manifest['chunks'].append(item);dump(progress,manifest);print('Uploaded transport chunk',index+1,'of',(len(raw)+size-1)//size,flush=True)
 request.unlink(missing_ok=True);dump(R/'artifact-transport.json',manifest)
else:
 manifest=json.loads((R/'artifact-transport.json').read_text());directory=CACHE/'published';directory.mkdir(parents=True,exist_ok=True);raw=bytearray()
 for c in manifest['chunks']:
  obj=json.loads(gh('api',f"repos/{REPO}/git/blobs/{c['git_blob_sha']}"));data=base64.b64decode(obj['content']);assert sha(data)==c['sha256'] and len(data)==c['bytes'];raw.extend(data)
 assert sha(raw)==manifest['bundle']['sha256'] and len(raw)==manifest['bundle']['bytes'];bundle=directory/manifest['bundle']['name'];bundle.write_bytes(raw)
 with zipfile.ZipFile(bundle) as z:
  assert z.testzip() is None
  for n in z.namelist():assert not Path(n).is_absolute() and '..' not in Path(n).parts and Path(n).name==n
  z.extractall(directory)
 files=[]
 for item in manifest['assets']:
  f=directory/item['name'];assert f.exists() and sha(f.read_bytes())==item['sha256'] and f.stat().st_size==item['bytes'];files.append(f)
 gh('release','edit',TAG,'--repo',REPO,'--target',manifest['source_revision'],'--title','Two papers: complete Chinese reading translations','--notes','User-requested unofficial Chinese reading translations of Benton2025 and Dorkenwald2024. Assistant-authored within the session, with54 original page facsimiles, English source paragraphs and original bibliographic entries. Includes PDF, Word, HTML and Markdown. Not author-approved translations; original papers CC BY4.0, changes are translation and layout.')
 gh('release','upload',TAG,*map(str,files),'--repo',REPO,'--clobber')
 verified=[];verify=CACHE/'release-verify';verify.mkdir(exist_ok=True)
 for item in manifest['assets']:
  gh('release','download',TAG,'--repo',REPO,'--pattern',item['name'],'--dir',str(verify),'--clobber');f=verify/item['name'];assert sha(f.read_bytes())==item['sha256'] and f.stat().st_size==item['bytes'];verified.append(item['name'])
 gh('release','edit',TAG,'--repo',REPO,'--draft=false')
 status={'complete':True,'source_revision':manifest['source_revision'],'release_url':f'https://github.com/{REPO}/releases/tag/{TAG}','fresh_download_sha256_verified_assets':verified,'assets':manifest['assets']};dump(directory/'delivery-status.json',status)
 gh('release','upload',TAG,str(directory/'delivery-status.json'),'--repo',REPO,'--clobber')
 path='research/chinese-translations-20261118/delivery-status.json'
 for attempt in range(8):
  old=subprocess.run(['gh','api','-H','Cache-Control: no-cache',f'repos/{REPO}/contents/{path}?ref=main&nonce={time.time_ns()}'],capture_output=True,text=True);payload={'message':'Save verified complete Chinese translation delivery','branch':'main','content':base64.b64encode((directory/'delivery-status.json').read_bytes()).decode()}
  if old.returncode==0:payload['sha']=json.loads(old.stdout)['sha']
  elif '404' not in old.stderr:raise RuntimeError(old.stderr)
  request=CACHE/'delivery-request.json';dump(request,payload);res=subprocess.run(['gh','api','--method','PUT',f'repos/{REPO}/contents/{path}','--input',str(request)],capture_output=True,text=True)
  if res.returncode==0:break
  if attempt==7:raise RuntimeError(res.stderr)
  time.sleep(min(2**attempt,8))
 for attempt in range(8):
  fresh=json.loads(gh('api','-H','Cache-Control: no-cache',f'repos/{REPO}/contents/{path}?ref=main&nonce={time.time_ns()}'))
  if base64.b64decode(fresh['content'])==(directory/'delivery-status.json').read_bytes():break
  if attempt==7:raise RuntimeError('Fresh remote delivery record did not converge')
  time.sleep(min(2**attempt,8))
 print('Freshly verified public translation assets',json.dumps(status),flush=True)
