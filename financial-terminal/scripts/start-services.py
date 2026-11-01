"""Start separately deployable processes; record ownership before returning."""
from pathlib import Path
import importlib.util,json,os,socket,subprocess,time,urllib.request
from settings import ROOT,read_settings
spec=importlib.util.spec_from_file_location('processes',ROOT/'scripts/processes.py');processes=importlib.util.module_from_spec(spec);spec.loader.exec_module(processes)
cfg=read_settings();registry=json.loads((ROOT/'config/services.json').read_text())
def ready(url,deadline):
 while True:
  try:
   with urllib.request.urlopen(url,timeout=2) as response:assert response.status==200
   return
  except Exception:
   if time.monotonic()>deadline:raise RuntimeError('Service did not become ready: '+url+'; inspect .run logs')
   time.sleep(.5)
def launch(name,cmd):
 if processes.owned(name):return
 with (ROOT/f'.run/{name}.log').open('ab') as log:
  child=subprocess.Popen(cmd,cwd=ROOT,start_new_session=True,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT)
 (ROOT/f'.run/{name}.pid').write_text(str(child.pid))
 for attempt in range(30):
  try:
   found=processes.identity(child.pid)
   if found:(ROOT/f'.run/{name}.started').write_text(found[0]);return
  except OSError:pass
  time.sleep(.05)
 raise RuntimeError('Process could not start: '+name)
for offset in range(0,len(registry),4):
 batch=registry[offset:offset+4]
 for s in batch:
  port=int(cfg.get(s['name'].upper()+'_PORT',s['port']))
  if not processes.owned(s['name']):
   with socket.socket() as sock:
    try:sock.bind((cfg['SERVICE_HOST'],port))
    except OSError:raise RuntimeError(f"Port {port} is occupied; stop the previous APERTURE instance or configure {s['name'].upper()}_PORT")
  launch(s['name'],[cfg['PYTHON_BIN'],'scripts/run-service.py',s['name']])
 for s in batch:
  url=cfg.get(s['name'].upper()+'_URL',f"http://{cfg['SERVICE_HOST']}:{cfg.get(s['name'].upper()+'_PORT',s['port'])}")
  ready(url+'/health',time.monotonic()+180);print('Ready: '+s['name'],flush=True)
if (ROOT/'frontend/dist/index.html').exists():
 launch('frontend',['npm','--prefix','frontend','run','preview']);ready(cfg['FRONTEND_URL'],time.monotonic()+30)
print('APERTURE ready: '+cfg['FRONTEND_URL'])
