"""Continuous immutable GitHub checkpoints, fresh progress reads,300 continuation.
Only task-owned progress.json is updated; no force push or credentials in files.
"""
from pathlib import Path
import base64,hashlib,json,os,subprocess,sys,zipfile,time
R=Path(__file__).resolve().parent;OUT=R/'cache/train';OUT.mkdir(parents=True,exist_ok=True)
REPO=os.environ['GITHUB_REPOSITORY'];SOURCE=os.environ['TRAIN_SOURCE_REF'];TAG='joint-physical-bounds-20261117';PROGRESS='research/joint-bptt-physical-bounds-20261117/progress.json'
def gh(*args,check=True):return subprocess.run(['gh',*args],check=check,text=True,capture_output=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def release():
 r=gh('release','view',TAG,'--repo',REPO,'--json','assets',check=False)
 if r.returncode:
  if 'not found' not in r.stderr.lower():raise RuntimeError(r.stderr)
  return None
 return json.loads(r.stdout)
def write(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
def progress_read():
 # Read a fresh blob SHA after conflicts; never reuse a cached main response.
 return gh('api','-H','Cache-Control: no-cache',f'repos/{REPO}/contents/{PROGRESS}?ref=main&sync_nonce={time.time_ns()}',check=False)
mode=sys.argv[1]
if mode=='restore':
 data=release();tmp=R/'cache/resume';tmp.mkdir(parents=True,exist_ok=True)
 if data and any(x['name']=='latest.json' for x in data['assets']):
  gh('release','download',TAG,'--repo',REPO,'--pattern','latest.json','--dir',str(tmp),'--clobber');meta=json.loads((tmp/'latest.json').read_text());assert meta['source_revision']==SOURCE,'Do not mix training source revisions'
  gh('release','download',TAG,'--repo',REPO,'--pattern',meta['checkpoint_asset'],'--dir',str(tmp),'--clobber');p=tmp/meta['checkpoint_asset'];assert sha(p)==meta['sha256'] and p.stat().st_size==meta['bytes']
  with zipfile.ZipFile(p) as z:
   assert z.testzip() is None
   for n in z.namelist():assert not Path(n).is_absolute() and '..' not in Path(n).parts
   z.extractall(OUT)
  print('Restored actual main updates',meta['completed_updates'],'phase',meta['phase'],flush=True)
 else:print('New run: best parent87 weights; manual regularizer center; new main0/300',flush=True)
elif mode=='publish':
 report=json.loads((OUT/'chunk-report.json').read_text());assert report['source_revision']==SOURCE
 reserved={'config.json','manual-anchor.json','neural-config.json','validation-report.json','initialization.json','parameter-rules.json'}
 names=[p for p in OUT.iterdir() if p.is_file() and p.suffix in ('.npz','.json') and p.name not in reserved]
 names+=[R/name for name in sorted(reserved)]
 archive=R/'cache/transfer.zip'
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
  for p in names:
   raw=p.read_bytes()
   assert b'lzf'+b'123456' not in raw and (b'-----BEGIN '+b'PRIVATE KEY') not in raw
   z.writestr(p.name,raw)
 count=int(report['completed_updates']);phase=report['phase'];asset=f"joint-{phase}-e{count:04d}-p{report['pilot_index']}-{report['phase_updates']}-{sha(archive)[:12]}.zip";target=archive.with_name(asset);archive.replace(target);archive=target
 data=release()
 if not data:
  gh('release','create',TAG,'--repo',REPO,'--draft','--target',SOURCE,'--title','Physical-range BPTT300 from best parent87','--notes','Actual joint-loss optimizer updates, not old muscle-u training. Exact native AB forward, white-box contact/muscle derivatives; anchored to pre-BPTT manually tuned bank. Source/parameters/counts are immutable and validated.');data=release()
 if not any(a['name']==asset for a in data['assets']):gh('release','upload',TAG,str(archive),'--repo',REPO)
 verify=R/'cache/remote-verify';verify.mkdir(exist_ok=True);gh('release','download',TAG,'--repo',REPO,'--pattern',asset,'--dir',str(verify),'--clobber');assert sha(verify/asset)==sha(archive);(verify/asset).unlink()
 meta={'completed_updates':count,'required_updates':300,'complete':count>=300,'phase':phase,'pilot_index':report['pilot_index'],'phase_updates':report['phase_updates'],'selected_coefficient':report['selected_coefficient'],'parameter_anchor':'pre-BPTT manually tuned bank','manual_model_sha256':report['manual_anchor_model_sha256'],'source_revision':SOURCE,'checkpoint_asset':asset,'sha256':sha(archive),'bytes':archive.stat().st_size,'checkpoint_tag':TAG,'checkpoint_url':f'https://github.com/{REPO}/releases/download/{TAG}/{asset}','draft_asset':True,'fresh_asset_download_verified':True,'run_url':f"https://github.com/{REPO}/actions/runs/{os.environ.get('GITHUB_RUN_ID','local')}",'last':report['last'],'epoch_definition':report['epoch_definition']}
 latest=R/'cache/latest.json';write(latest,meta);gh('release','upload',TAG,str(latest),'--repo',REPO,'--clobber')
 for attempt in range(8):
  old=progress_read();payload={'message':f'Save native joint BPTT {phase} main{count}/300','branch':'main','content':base64.b64encode(latest.read_bytes()).decode()}
  if old.returncode==0:
   existing=json.loads(old.stdout)
   if base64.b64decode(existing['content'])==latest.read_bytes():break
   payload['sha']=existing['sha']
  elif '404' not in old.stderr:raise RuntimeError(old.stderr)
  request=R/'cache/progress-payload.json';write(request,payload);answer=gh('api','--method','PUT',f'repos/{REPO}/contents/{PROGRESS}','--input',str(request),check=False)
  if answer.returncode==0:break
  if attempt==7:raise RuntimeError(answer.stderr)
  time.sleep(min(2**attempt,8))
 # A successful Contents PUT can precede a consistent read from every replica.
 # Retry the actual hash/count check; do not weaken or skip remote validation.
 for verify_attempt in range(8):
  fresh_result=progress_read();fresh=None
  if fresh_result.returncode==0:
   response=json.loads(fresh_result.stdout);fresh=json.loads(base64.b64decode(response['content']))
   if fresh.get('sha256')==meta['sha256'] and fresh.get('completed_updates')==count:break
  if verify_attempt==7:
   raise RuntimeError('Remote progress did not converge to uploaded checkpoint: expected_count='+str(count)+', observed_count='+str(None if fresh is None else fresh.get('completed_updates')))
  time.sleep(min(2**verify_attempt,8))
 print('Fresh remote checkpoint confirmed',json.dumps(meta),flush=True)
elif mode=='dispatch':
 report=json.loads((OUT/'chunk-report.json').read_text())
 if int(report['completed_updates'])<300:
  gh('workflow','run','train-joint-physical-bounds.yml','--repo',REPO,'--ref','main','-f','source_ref='+SOURCE,'-f','chunk_updates='+os.environ.get('NEXT_CHUNK_UPDATES','10'));print('Dispatched continuation toward300 actual main updates',flush=True)
 else:print('300 main updates actually completed',flush=True)
else:raise ValueError(mode)
