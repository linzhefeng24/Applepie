"""Independent local clusters and narrowly scoped process environments. Never print secrets."""
from pathlib import Path
import hashlib,json,os,secrets,subprocess,sys,tempfile
from settings import ROOT,read_settings,windows_drive_project
REGISTRY=json.loads((ROOT/'config/services.json').read_text())
def private_json(path,value):
 path.parent.mkdir(parents=True,exist_ok=True)
 fd,temporary=tempfile.mkstemp(dir=path.parent,prefix='.'+path.name+'-')
 try:
  with os.fdopen(fd,'w') as f:json.dump(value,f);f.flush();os.fsync(f.fileno())
  os.chmod(temporary,0o600);os.replace(temporary,path)
 finally:Path(temporary).unlink(missing_ok=True)

def configuration():
 cfg=read_settings();base=Path(cfg.get('SERVICE_STATE_DIR',str(Path(cfg['PG_DATA_DIR']).parent/'services')))
 if not base.is_absolute():base=ROOT/base
 base.mkdir(parents=True,exist_ok=True);os.chmod(base,0o700)
 private=base/'credentials.json'
 if private.exists():credentials=json.loads(private.read_text())
 else:credentials={}
 for service in REGISTRY:
  name=service['name'];credentials.setdefault(name,dict(token=secrets.token_urlsafe(32),password=secrets.token_urlsafe(32),adminPassword=secrets.token_urlsafe(32)))
 private_json(private,credentials)
 return cfg,base,credentials

def prepare(start=True):
 cfg,base,credentials=configuration()
 hashes={n:hashlib.sha256(v['token'].encode()).hexdigest() for n,v in credentials.items()}
 urls={s['name'].upper()+'_URL':cfg.get(s['name'].upper()+'_URL',f"http://{cfg['SERVICE_HOST']}:{cfg.get(s['name'].upper()+'_PORT',s['port'])}") for s in REGISTRY}
 for s in REGISTRY:
  name=s['name'];key=name.upper();secret=credentials[name]
  env={k:str(v) for k,v in cfg.items() if k in ['DATA_DIR','FRONTEND_PORT','DEV_PORT','SERVICE_HOST','ALLOWED_ORIGINS','COOKIE_SECURE']}
  env.update(urls);env.update(SERVICE=name,HTTP_PORT=str(cfg.get(key+'_PORT',s['port'])),DATABASE_REQUIRED=str(s['database']).lower(),INTERNAL_SERVICE_TOKEN=secret['token'],TRUSTED_SERVICE_HASHES=json.dumps(hashes))
  if s['database']:
   port=str(cfg.get(key+'_DB_PORT',s['dbPort']));db='aperture_'+name;user='app_'+name
   env.update(DB_HOST=cfg.get(key+'_DB_HOST','127.0.0.1'),DB_PORT=port,DB_NAME=cfg.get(key+'_DB_NAME',db),DB_USER=cfg.get(key+'_DB_USER',user),DB_PASSWORD=cfg.get(key+'_DB_PASSWORD',secret['password']))
   if cfg.get('MANAGE_POSTGRES','true')=='true' and start:
    import psycopg
    from psycopg import sql
    cluster=base/name;socket=Path(tempfile.gettempdir())/('aperture-'+hashlib.sha256(str(base).encode()).hexdigest()[:10]+'-'+name)
    socket.mkdir(mode=0o700,exist_ok=True);pg=Path(cfg['PG_BIN'])
    if not (cluster/'PG_VERSION').exists():
     fd,pw=tempfile.mkstemp(dir=base,prefix='.init-')
     try:
      with os.fdopen(fd,'w') as f:f.write(secret['adminPassword'])
      cmd=[str(pg/'initdb'),'-D',str(cluster),'--username=aperture_admin','--pwfile='+pw,'--auth-local=scram-sha-256','--auth-host=scram-sha-256','--no-locale','--encoding=UTF8']
      if cfg.get('PG_SHARE'):cmd+=['-L',cfg['PG_SHARE']]
      subprocess.run(cmd,check=True,stdout=subprocess.DEVNULL)
     finally:Path(pw).unlink(missing_ok=True)
    if subprocess.run([str(pg/'pg_ctl'),'-D',str(cluster),'status'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode:
     subprocess.run([str(pg/'pg_ctl'),'-D',str(cluster),'-l',str(ROOT/'.run'/f'postgres-{name}.log'),'-o',f"-h 127.0.0.1 -p {port} -k '{socket}' -c shared_buffers=16MB -c max_connections=24",'start'],check=True,stdout=subprocess.DEVNULL)
    with psycopg.connect(host='127.0.0.1',port=port,dbname='postgres',user='aperture_admin',password=secret['adminPassword'],autocommit=True) as c:
     if not c.execute('SELECT 1 FROM pg_roles WHERE rolname=%s',(user,)).fetchone():c.execute(sql.SQL('CREATE ROLE {} LOGIN PASSWORD {}').format(sql.Identifier(user),sql.Literal(secret['password'])))
     if not c.execute('SELECT 1 FROM pg_database WHERE datname=%s',(db,)).fetchone():c.execute(sql.SQL('CREATE DATABASE {} OWNER {}').format(sql.Identifier(db),sql.Identifier(user)))
     c.execute(sql.SQL('REVOKE ALL ON DATABASE {} FROM PUBLIC').format(sql.Identifier(db)))
    # Verify exactly this service's restricted credentials, not the bootstrap administrator.
    with psycopg.connect(host=env['DB_HOST'],port=port,dbname=env['DB_NAME'],user=env['DB_USER'],password=env['DB_PASSWORD']) as c:
     assert c.execute('SELECT NOT rolsuper FROM pg_roles WHERE rolname=current_user').fetchone()==(True,)
   print(f"Database ready: {name} ({env['DB_HOST']}:{port})",flush=True)
  private_json(ROOT/'.run/service-env'/f'{name}.json',env)
 return cfg

def environment(name):
 # Remove all inherited database/internal credentials before adding only this process's own settings.
 env={k:v for k,v in os.environ.items() if not (k.startswith(('DB_','PG_')) or k in {'PGPASSWORD','PGPASSFILE','PGSERVICEFILE','PGSERVICE','PGHOST','PGHOSTADDR','PGPORT','PGDATABASE','PGUSER','DATABASE_URL'} or '_DB_' in k or k in ['INTERNAL_SERVICE_TOKEN','TRUSTED_SERVICE_HASHES'])}
 env.update(json.loads((ROOT/'.run/service-env'/f'{name}.json').read_text()));return env
if __name__=='__main__':
 if sys.argv[1:] == ['stop']:
  cfg,base,_=configuration()
  for s in REGISTRY:
   cluster=base/s['name']
   if s['database'] and (cluster/'PG_VERSION').exists():subprocess.run([str(Path(cfg['PG_BIN'])/'pg_ctl'),'-D',str(cluster),'stop','-m','fast'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 else:prepare()
