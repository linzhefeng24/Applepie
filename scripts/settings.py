"""Configuration precedence: exported environment > local .env > committed defaults.
Paths are resolved against this file's project root, not the caller's working directory.
No expansion or execution of .env contents. Never log the returned mapping.
"""
from pathlib import Path
import hashlib,json,os,re,shlex,shutil,subprocess,tempfile
ROOT=Path(__file__).resolve().parents[1]
def read_settings(root=ROOT,environ=None):
    root=Path(root).resolve();values=json.loads((root/'config/defaults.json').read_text())
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
            values[key]=' '.join(parts)
    values.update(dict(os.environ if environ is None else environ))
    for key in ['DATA_DIR','PG_DATA_DIR']:
        values[key]=str((root/values[key]).resolve())
    if not values.get('PG_BIN'):
        bundled=next((root/'.tools/pg').rglob('pg_ctl'),None) if (root/'.tools/pg').exists() else None
        installed=shutil.which('pg_ctl',path=values.get('PATH'))
        values['PG_BIN']=str(bundled.parent) if bundled else str(Path(installed).parent) if installed else ''
    elif values['PG_BIN']:values['PG_BIN']=str((root/values['PG_BIN']).resolve())
    if not values.get('PG_SHARE'):
        bki=next((root/'.tools/pg').rglob('postgres.bki'),None) if (root/'.tools/pg').exists() else None
        if bki:values['PG_SHARE']=str(bki.parent)
        elif values['PG_BIN']:
            pgconfig=Path(values['PG_BIN'])/'pg_config'
            if pgconfig.exists():values['PG_SHARE']=subprocess.check_output([str(pgconfig),'--sharedir'],text=True).strip()
    elif values['PG_SHARE']:values['PG_SHARE']=str((root/values['PG_SHARE']).resolve())
    values['PG_SOCKET_DIR']=str((root/values['PG_SOCKET_DIR']).resolve()) if values.get('PG_SOCKET_DIR') else str(Path(tempfile.gettempdir())/('aperture-pg-'+hashlib.sha256(str(root).encode()).hexdigest()[:12]))
    for service in ['MARKET','PORTFOLIO','ANALYSIS','QUANT']:
        values.setdefault(service+'_URL',f"http://{values['SERVICE_HOST']}:{values[service+'_PORT']}")
    values.setdefault('FRONTEND_URL',f"http://{values['FRONTEND_HOST']}:{values['FRONTEND_PORT']}")
    values['PYTHON_BIN']=str((root/values.get('PYTHON_BIN','.venv/bin/python')).absolute())
    return values
if __name__=='__main__':
    import sys
    cfg=read_settings()
    # Emit only application keys, not unrelated inherited credentials or process environment.
    keys=set(json.loads((ROOT/'config/defaults.json').read_text()))|{'DB_PASSWORD','MARKET_URL','PORTFOLIO_URL','ANALYSIS_URL','QUANT_URL','FRONTEND_URL','PYTHON_BIN'}
    if sys.argv[1:] == ['--shell']:
        print('\n'.join('export '+k+'='+shlex.quote(cfg[k]) for k in sorted(keys) if k in cfg))
    else:raise SystemExit('Use --shell only inside eval; do not print settings containing credentials.')
