"""Durable GitHub checkpoint storage, progress commits and next-chunk dispatch."""
from pathlib import Path
import base64,hashlib,json,os,subprocess,sys,zipfile
R=Path(__file__).resolve().parent;OUT=R/'cache/longrun';OUT.mkdir(parents=True,exist_ok=True)
REPO=os.environ['GITHUB_REPOSITORY'];SOURCE=os.environ['TRAIN_SOURCE_REF'];TAG='regularized-bptt-1000-20261115';PROGRESS='research/surrogate-bptt-20261115/longrun/progress.json'
def gh(*args,check=True):return subprocess.run(['gh',*args],check=check,text=True,capture_output=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def release():
 r=gh('release','view',TAG,'--repo',REPO,'--json','assets',check=False)
 if r.returncode:
  if 'release not found' not in r.stderr.lower():raise RuntimeError(r.stderr)
  return None
 return json.loads(r.stdout)
mode=sys.argv[1]
if mode=='restore':
 d=release()
 if d and any(x['name']=='latest.json' for x in d['assets']):
  tmp=R/'cache/resume';tmp.mkdir(exist_ok=True)
  gh('release','download',TAG,'--repo',REPO,'--pattern','latest.json','--dir',str(tmp),'--clobber')
  meta=json.loads((tmp/'latest.json').read_text());assert meta['source_revision']==SOURCE
  gh('release','download',TAG,'--repo',REPO,'--pattern',meta['checkpoint_asset'],'--dir',str(tmp),'--clobber')
  p=tmp/meta['checkpoint_asset'];assert p.stat().st_size==meta['bytes'] and sha(p)==meta['sha256']
  with zipfile.ZipFile(p) as z:
   assert z.testzip() is None
   for n in z.namelist():assert not Path(n).is_absolute() and '..' not in Path(n).parts
   z.extractall(OUT)
  print('Restored exact optimizer state at',meta['completed_updates'],flush=True)
 else:print('No prior durable checkpoint; starting new1000-update run',flush=True)
elif mode=='publish':
 report=json.loads((OUT/'chunk-report.json').read_text());count=int(report['completed_updates']);assert report['source_revision']==SOURCE
 archive=R/'cache'/f'bptt-checkpoint-{count:04d}.zip'
 names=['latest-optimizer.npz','best-parameters.npz','history.json','chunk-report.json','run-config.json','forward-check.json','best-local-fit.npz']
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
  for n in names:z.write(OUT/n,n)
 if not release():gh('release','create',TAG,'--repo',REPO,'--draft','--target',SOURCE,'--title','Regularized HH surrogate-BPTT: minimum1000 updates','--notes','Durable optimizer checkpoints. Completed updates are counted explicitly; no early stopping before1000. Local training and full-network validation are distinct.')
 immutable=archive.with_name(archive.stem+'-'+sha(archive)[:12]+'.zip');archive.rename(immutable);archive=immutable
 if not any(x['name']==archive.name for x in release()['assets']):gh('release','upload',TAG,str(archive),'--repo',REPO)
 meta={'completed_updates':count,'minimum_updates':report['minimum_updates'],'complete':report['complete'],'best_training_step':report['best_training_step'],'checkpoint_asset':archive.name,'bytes':archive.stat().st_size,'sha256':sha(archive),'source_revision':SOURCE,'model_sha256':report['baseline_model_sha256'],'best_training_objective':report['best_training_objective'],'best_holdout_mse':report['best_holdout_mse'],'best_max_relative_shift':report['best_max_relative_shift'],'run_url':f"https://github.com/{REPO}/actions/runs/{os.environ['GITHUB_RUN_ID']}",'checkpoint_tag':TAG,'definition':report['epoch_definition']}
 (R/'cache/latest.json').write_text(json.dumps(meta,indent=2)+'\n');gh('release','upload',TAG,str(R/'cache/latest.json'),'--repo',REPO,'--clobber')
 # Commit only this task-owned progress file using the current remote file SHA.
 for attempt in range(3):
  old=gh('api',f'repos/{REPO}/contents/{PROGRESS}?ref=main',check=False);payload={'message':f'Record regularized BPTT progress {count}/1000','branch':'main','content':base64.b64encode((json.dumps(meta,indent=2)+'\n').encode()).decode()}
  if old.returncode==0:payload['sha']=json.loads(old.stdout)['sha']
  elif '404' not in old.stderr:raise RuntimeError(old.stderr)
  f=R/'cache/progress-payload.json';f.write_text(json.dumps(payload))
  result=gh('api','--method','PUT',f'repos/{REPO}/contents/{PROGRESS}','--input',str(f),check=False)
  if result.returncode==0:break
  if attempt==2:raise RuntimeError(result.stderr)
 check=json.loads(gh('api',f'repos/{REPO}/contents/{PROGRESS}?ref=main').stdout)
 fresh=json.loads(base64.b64decode(check['content']));assert fresh['sha256']==meta['sha256'] and fresh['completed_updates']==count
 print('Fresh remote checkpoint confirmed',json.dumps(meta),flush=True)
elif mode=='dispatch':
 report=json.loads((OUT/'chunk-report.json').read_text())
 if report['completed_updates']<max(1000,report['minimum_updates']):
  gh('workflow','run','train-bptt-1000.yml','--repo',REPO,'--ref','main','-f','source_ref='+SOURCE,'-f','chunk_updates=50')
  print('Dispatched continuation; no early stopping',flush=True)
 else:print('Minimum1000 updates really completed; no continuation needed',flush=True)
else:raise ValueError(mode)
