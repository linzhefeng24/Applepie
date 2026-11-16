"""Offline, isolated server benchmark/continuation; never updates GitHub state."""
from pathlib import Path
import argparse,datetime,hashlib,json,os,shutil,subprocess,sys,time,uuid,zipfile
ROOT=Path(__file__).resolve().parent
REL=Path('research/joint-bptt-300-20261116')
def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
 return h.hexdigest()
def read(p):return json.loads(p.read_text())
def write(p,v):p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
def verify():
 manifest=read(ROOT/'PACKAGE_MANIFEST.json')
 for item in manifest['files']:
  p=ROOT/item['path'];assert p.stat().st_size==item['bytes'] and digest(p)==item['sha256'],'Changed/missing package input: '+str(p)
 print('Verified',len(manifest['files']),'files; manual model and checkpoint hashes match.',flush=True)
 return manifest
def info():
 import importlib.metadata as md
 import jax
 cpu=Path('/proc/cpuinfo').read_text() if Path('/proc/cpuinfo').exists() else ''
 memory=Path('/proc/meminfo').read_text() if Path('/proc/meminfo').exists() else ''
 result={'python':sys.version,'cpu_model':next((line.split(':',1)[1].strip() for line in cpu.splitlines() if line.startswith('model name')),'unknown'),'logical_cpus':os.cpu_count(),'memory_total':next((line for line in memory.splitlines() if line.startswith('MemTotal:')),'unknown'),'jax_devices':[str(x) for x in jax.devices()],'versions':{n:md.version(n) for n in ['numpy','jax','jaxlib','mujoco','mujoco-mjx']},'execution':'CPU; GPU availability is reported separately and does not enable GPU execution'}
 if shutil.which('nvidia-smi'):
  gpu=subprocess.run(['nvidia-smi','--query-gpu=name,memory.total,driver_version','--format=csv,noheader'],capture_output=True,text=True)
  result['gpu_inventory']=gpu.stdout.strip() if gpu.returncode==0 else 'nvidia-smi failed'
 print(json.dumps(result,indent=2,ensure_ascii=False),flush=True);return result
def new_run(mode,manifest):
 work=ROOT/'runs'/(datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+mode+'-'+uuid.uuid4().hex[:6]);work.mkdir(parents=True)
 shutil.copytree(ROOT/'research',work/'research',ignore=shutil.ignore_patterns('cache','__pycache__','*.pyc'))
 out=work/REL/'cache/train';out.mkdir(parents=True)
 with zipfile.ZipFile(ROOT/'checkpoint/optimizer.zip') as archive:
  for name in archive.namelist():
   assert Path(name).name==name,'Unexpected nested checkpoint input'
   if name in ['config.json','manual-anchor.json','neural-config.json','validation-report.json']:continue
   if Path(name).suffix in ['.npz','.json']:(out/name).write_bytes(archive.read(name))
 write(work/'server-run.json',{'mode':mode,'manifest_sha256':digest(ROOT/'PACKAGE_MANIFEST.json'),'training_source_revision':manifest['training_source_revision'],'seed_checkpoint_sha256':manifest['checkpoint']['sha256'],'official_github_counts_are_not_changed':True})
 return work
def export(work):
 destination=ROOT/'exports';destination.mkdir(exist_ok=True);p=destination/(work.name+'.zip')
 files=[x for x in work.iterdir() if x.is_file() and x.suffix in ['.json','.log']]
 files +=[x for x in (work/REL/'cache/train').iterdir() if x.is_file() and x.suffix in ['.npz','.json']]
 with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED) as z:
  for x in files:z.write(x,x.relative_to(work))
  z.write(ROOT/'PACKAGE_MANIFEST.json','PACKAGE_MANIFEST.json')
 print('Export:',p,'SHA256:',digest(p),flush=True);return p
def execute(mode,resume=None,updates=None):
 manifest=verify()
 if resume:
  work=Path(resume).resolve();assert work.is_relative_to(ROOT/'runs'),'Resume directory must be under this package runs/'
  assert read(work/'server-run.json')['manifest_sha256']==digest(ROOT/'PACKAGE_MANIFEST.json'),'Different bundle; do not mix checkpoints'
 else:work=new_run(mode,manifest)
 out=work/REL/'cache/train';old=read(out/'history.json');before=len(old)
 write(work/'environment.json',info());print('Run directory:',work,flush=True)
 count=0 if mode=='check' else (updates if updates is not None else 2 if mode=='benchmark' else 315)
 assert count>=0
 env=os.environ.copy();env['TRAIN_SOURCE_REF']=manifest['training_source_revision'];env['SYNC_EVERY_SAVE']='0';env['JAX_PLATFORMS']='cpu'
 command=[sys.executable,str(work/REL/'train_chunk.py'),'--updates',str(count)]
 start=time.monotonic()
 with (work/'console.log').open('a') as log:
  log.write('\nCommand: '+json.dumps(command)+'\n');log.flush()
  process=subprocess.Popen(command,cwd=work,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
  try:
   for line in process.stdout:print(line,end='',flush=True);log.write(line);log.flush()
   code=process.wait()
  except KeyboardInterrupt:
   process.terminate();process.wait();code=130
 history=read(out/'history.json');new=history[before:];summary={'mode':mode,'exit_code':code,'wall_seconds':time.monotonic()-start,'actual_updates_in_this_invocation':len(new),'latest':read(out/'chunk-report.json'),'per_update_seconds':[row['seconds'] for row in new],'github_reference_steady_update_seconds':502,'benchmark_note':'First sample includes fresh compilation. Use second sample for steady-speed comparison; pilot final evaluation and saving are included in wall time, not per-update seconds.','official_github_checkpoint_modified':False}
 if len(new)>=2:summary['last_update_speedup_vs_github_502s']=502/new[-1]['seconds']
 write(work/'server-result.json',summary);export(work)
 print('Saved result:',work/'server-result.json',flush=True)
 if code:raise SystemExit(code)
parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='command',required=True)
for command in ['verify','info']:sub.add_parser(command)
for command in ['check','benchmark','train']:
 p=sub.add_parser(command);p.add_argument('--resume');p.add_argument('--updates',type=int)
for command in ['status','export']:
 p=sub.add_parser(command);p.add_argument('--run',required=True)
args=parser.parse_args()
if args.command=='verify':verify()
elif args.command=='info':info()
elif args.command in ['check','benchmark','train']:execute(args.command,args.resume,args.updates)
else:
 work=Path(args.run).resolve();assert work.is_relative_to(ROOT/'runs')
 if args.command=='status':print(json.dumps(read(work/REL/'cache/train/chunk-report.json'),indent=2,ensure_ascii=False))
 else:export(work)
