"""Configuration precedence: exported environment > local .env > committed defaults.
Paths are resolved against this file's project root, not the caller's working directory.
No expansion or execution of .env contents. Never log the returned mapping.
"""
from pathlib import Path
import hashlib,json,os,re,shlex,shutil,subprocess,tempfile
ROOT=Path(__file__).resolve().parents[1]
def windows_drive_project(root,environ):
    parts=Path(root).parts
    return bool(environ.get('WSL_DISTRO_NAME')) and len(parts)>3 and parts[1]=='mnt' and bool(re.fullmatch('[a-zA-Z]',parts[2]))
def read_settings(root=ROOT,environ=None):
    root=Path(root).resolve();values=json.loads((root/'config/defaults.json').read_text())
    file_keys=set()
    path=root/'.env'
    if path.exists():
        for line in path.read_text().splitlines():
            line=line.strip()
            if not line or line.startswith('#'):continue
            if line.startswith('export '):line=line[7:]
            if '=' not in line:raise ValueError('Invalid .env line: expected KEY=value')
            key,value=line.split('=',1)
            if not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*',key):raise ValueError('Invalid .env key')
            parts=shlex.split(value,comments=True)
            values[key]=' '.join(parts);file_keys.add(key)
    environment=dict(os.environ if environ is None else environ)
    values.update(environment)
    # Preserve old explicit port overrides when upgrading from the three-service layout.
    for new,old in [('WATCHLIST','PORTFOLIO'),('OPTIMIZATION','ANALYSIS'),('CATALOG','MARKET'),('DAILY','HISTORY'),('QUANT_OPTIMIZER','QUANT')]:
        for suffix in ['_PORT','_URL']:
            if new+suffix not in file_keys and new+suffix not in environment and (old+suffix in file_keys or old+suffix in environment):
                values[new+suffix]=values[old+suffix]
    # PostgreSQL cannot use default Windows-drive permissions. Keep WSL database state on Linux.
    explicit_pg_data='PG_DATA_DIR' in file_keys or 'PG_DATA_DIR' in environment
    if not explicit_pg_data and windows_drive_project(root,environment):
        state=Path(environment.get('XDG_STATE_HOME',str(Path.home()/'.local/state')))
        values['PG_DATA_DIR']=str(state/'aperture'/hashlib.sha256(str(root).encode()).hexdigest()[:12]/'postgres')
    for key in ['DATA_DIR','PG_DATA_DIR']:
        values[key]=str((root/values[key]).resolve())
    if not values.get('PG_BIN'):
        bundled=next((root/'.tools/pg').rglob('pg_ctl'),None) if (root/'.tools/pg').exists() else None
        installed=shutil.which('pg_ctl',path=values.get('PATH'))
        system_bins=sorted(Path('/usr/lib/postgresql').glob('*/bin/pg_ctl'),key=lambda p:tuple(int(n) for n in re.findall(r'\d+',str(p))))
        values['PG_BIN']=str(bundled.parent) if bundled else str(Path(installed).parent) if installed else str(system_bins[-1].parent) if system_bins else ''
    elif values['PG_BIN']:values['PG_BIN']=str((root/values['PG_BIN']).resolve())
    if not values.get('PG_SHARE'):
        bki=next((root/'.tools/pg').rglob('postgres.bki'),None) if (root/'.tools/pg').exists() else None
        if bki:values['PG_SHARE']=str(bki.parent)
        elif values['PG_BIN']:
            pgconfig=Path(values['PG_BIN'])/'pg_config'
            if pgconfig.exists():values['PG_SHARE']=subprocess.check_output([str(pgconfig),'--sharedir'],text=True).strip()
    elif values['PG_SHARE']:values['PG_SHARE']=str((root/values['PG_SHARE']).resolve())
    values['PG_SOCKET_DIR']=str((root/values['PG_SOCKET_DIR']).resolve()) if values.get('PG_SOCKET_DIR') else str(Path(tempfile.gettempdir())/('aperture-pg-'+hashlib.sha256(str(root).encode()).hexdigest()[:12]))
    service_names=['MARKET','HISTORY','STATISTICS','WATCHLIST','REPORTS','OPTIMIZATION','BACKTEST','QUANT']
    registry=root/'config/services.json'
    if registry.exists():service_names += [s['name'].upper() for s in json.loads(registry.read_text())]
    for service in service_names:
        values.setdefault(service+'_URL',f"http://{values['SERVICE_HOST']}:{values[service+'_PORT']}")
    values.setdefault('FRONTEND_URL',f"http://{values['FRONTEND_HOST']}:{values['FRONTEND_PORT']}")
    venv=values.get('APERTURE_VENV_DIR')
    if not venv:
        if windows_drive_project(root,environment):
            requirements=root/'quant/requirements.txt'
            dep_hash=hashlib.sha256(requirements.read_bytes() if requirements.exists() else b'').hexdigest()[:16]
            cache=Path(environment.get('XDG_CACHE_HOME',str(Path.home()/'.cache')))
            venv=str(cache/'aperture'/'venvs'/dep_hash/'venv')
        else:venv='.venv'
    values['APERTURE_VENV_DIR']=str((root/venv).absolute())
    values['PYTHON_BIN']=str((root/values.get('PYTHON_BIN',str(Path(values['APERTURE_VENV_DIR'])/'bin/python'))).absolute())
    return values
if __name__=='__main__':
    import sys
    cfg=read_settings()
    # Emit only application keys, not unrelated inherited credentials or process environment.
    keys=set(json.loads((ROOT/'config/defaults.json').read_text()))|{'DB_PASSWORD','MARKET_URL','HISTORY_URL','STATISTICS_URL','WATCHLIST_URL','REPORTS_URL','OPTIMIZATION_URL','BACKTEST_URL','QUANT_URL','FRONTEND_URL','PYTHON_BIN'}
    if sys.argv[1:] == ['--shell']:
        print('\n'.join('export '+k+'='+shlex.quote(cfg[k]) for k in sorted(keys) if k in cfg))
    else:raise SystemExit('Use --shell only inside eval; do not print settings containing credentials.')
