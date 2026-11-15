"""Publish final full validation and one standalone candidate after1000 updates."""
from pathlib import Path
import base64,hashlib,json,os,shutil,subprocess,sys,zipfile
R=Path(__file__).resolve().parent;ROOT=R.parents[1];O=R/'cache/longrun';report=json.loads((O/'chunk-report.json').read_text())
if report['completed_updates']<1000:print('Not finished1000; no final model claimed');sys.exit(0)
repo=os.environ['GITHUB_REPOSITORY'];tag='regularized-bptt-1000-20261115'
def gh(*a):return subprocess.check_output(['gh',*a],text=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
v=R/'full-validation/longrun-best';bundle=R/'cache/final-bundle';bundle.mkdir(exist_ok=True)
validation=json.loads((v/'report.json').read_text()) if (v/'report.json').exists() else {'status':'missing_full_validation'}
rawzip=R/'cache/bptt-1000-full-validation.zip'
with zipfile.ZipFile(rawzip,'w',zipfile.ZIP_DEFLATED) as z:
 for p in v.rglob('*'):
  if p.is_file():z.write(p,str(p.relative_to(v)))
assets=[rawzip]
patch=v/'parameter-patch.json'
if patch.exists():
 runtime=ROOT/'research/single-model-delivery-20261115/runtime'
 for p in runtime.iterdir():
  target=bundle/p.name
  if p.is_dir():shutil.copytree(p,target,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
  else:shutil.copy2(p,target)
 (bundle/'01_model').mkdir(exist_ok=True)
 subprocess.run([sys.executable,str(R/'materialize_candidate.py'),'--base',str(ROOT/json.loads((R/'config.json').read_text())['baseline_model']),'--patch',str(patch),'--output',str(bundle/'01_model/model.yaml')],check=True)
 (bundle/'03_training').mkdir(exist_ok=True)
 for name in ['chunk-report.json','history.json','run-config.json','forward-check.json','best-parameters.npz']:
  shutil.copy2(O/name,bundle/'03_training'/name)
 shutil.copy2(v/'report.json',bundle/'03_training/full-network-validation.json')
 if (v/'muscle-u.npz').exists():shutil.copy2(v/'muscle-u.npz',bundle/'03_training/full-network-u.npz')
 (bundle/'README.md').write_text('这是完成至少1000次Adam参数更新后的正则化代理梯度BPTT候选。01_model/model.yaml是唯一运行模型，02_code读取它。安装requirements.txt后执行python 02_code/run.py neural --experiment DN_drive；固定身体可执行demo --fixed-body。\n\n训练为260细胞局部回放边界，23组共207变量；并非完整3988细胞的反向传播。完成轮数见03_training/chunk-report.json；原始完整网络验证见full-network-validation.json。改进幅度、未通过或未检验现象必须按报告解释，不能将训练完成等同于左右交替/全部实验复现。此包未附新视频。\n')
 archive=R/'cache/Regularized_BPTT_1000_Candidate.zip'
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for p in bundle.rglob('*'):
   if p.is_file():z.write(p,'Regularized_BPTT_1000_Candidate/'+str(p.relative_to(bundle)))
 assets.append(archive)
meta={'completed_updates':report['completed_updates'],'best_training_step':report['best_training_step'],'source_revision':report['source_revision'],'full_validation_status':validation.get('status'),'assets':[{'file':p.name,'bytes':p.stat().st_size,'sha256':sha(p)} for p in assets],'scope':'Local boundary-replayed surrogate BPTT then original full-network hard-spike validation; not a guarantee of laboratory phenomena or anti-phase output.'}
f=R/'cache/regularized-bptt-1000-final.manifest.json';f.write_text(json.dumps(meta,indent=2)+'\n')
gh('release','upload',tag,*map(str,[*assets,f]),'--repo',repo,'--clobber')
# Fresh reads of uploaded asset metadata and a task-owned progress commit.
remote=json.loads(gh('release','view',tag,'--repo',repo,'--json','assets'))
for a in meta['assets']:
 a['url']=next(x['url'] for x in remote['assets'] if x['name']==a['file'])
path='research/surrogate-bptt-20261115/longrun/progress.json'
old=json.loads(gh('api',f'repos/{repo}/contents/{path}?ref=main'));progress=json.loads(base64.b64decode(old['content']));progress['final_results']=meta
payload={'message':'Save final1000-update validation and candidate asset identities','branch':'main','sha':old['sha'],'content':base64.b64encode((json.dumps(progress,indent=2)+'\n').encode()).decode()};p=R/'cache/final-progress.json';p.write_text(json.dumps(payload));gh('api','--method','PUT',f'repos/{repo}/contents/{path}','--input',str(p))
fresh=json.loads(gh('api',f'repos/{repo}/contents/{path}?ref=main'));assert json.loads(base64.b64decode(fresh['content']))['completed_updates']>=1000
print(json.dumps(meta,indent=2))
