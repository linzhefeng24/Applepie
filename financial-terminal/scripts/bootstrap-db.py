"""Create credentials only for this project's managed PostgreSQL instance."""
from pathlib import Path
import secrets,shlex,psycopg
from psycopg import sql
from settings import read_settings,ROOT
cfg=read_settings();assert cfg['MANAGE_POSTGRES']=='true'
password=cfg.get('DB_PASSWORD') or secrets.token_hex(24)
with psycopg.connect(host=cfg['PG_SOCKET_DIR'],port=int(cfg['DB_PORT']),user=cfg['DB_USER'],dbname='postgres',autocommit=True) as c:
 c.execute(sql.SQL('ALTER ROLE {} PASSWORD {}').format(sql.Identifier(cfg['DB_USER']),sql.Literal(password)))
 if not c.execute('SELECT 1 FROM pg_database WHERE datname=%s',(cfg['DB_NAME'],)).fetchone():c.execute(sql.SQL('CREATE DATABASE {}').format(sql.Identifier(cfg['DB_NAME'])))
p=ROOT/'.env';existing=p.read_text() if p.exists() else ''
# Keep user settings and append the generated password only. Last assignment wins.
additions=[]
if not cfg.get('DB_PASSWORD'):additions.append('DB_PASSWORD='+shlex.quote(password))
# Preserve an automatically selected Linux state location when a WSL project moves.
try:Path(cfg['PG_DATA_DIR']).relative_to(ROOT)
except ValueError:
 if not any(line.startswith('PG_DATA_DIR=') for line in existing.splitlines()):additions.append('PG_DATA_DIR='+shlex.quote(cfg['PG_DATA_DIR']))
if additions:p.write_text(existing.rstrip()+'\n'+'\n'.join(additions)+'\n');p.chmod(0o600)
print('Local PostgreSQL credentials initialized; private settings remain in ignored .env.')
