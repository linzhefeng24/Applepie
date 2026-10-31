"""Create credentials only for this project's managed PostgreSQL instance."""
from pathlib import Path
import secrets,shlex,psycopg
from psycopg import sql
from settings import read_settings,ROOT
cfg=read_settings();assert cfg['MANAGE_POSTGRES']=='true'
password=secrets.token_hex(24)
with psycopg.connect(host=cfg['PG_SOCKET_DIR'],port=int(cfg['DB_PORT']),user=cfg['DB_USER'],dbname='postgres',autocommit=True) as c:
 c.execute(sql.SQL('ALTER ROLE {} PASSWORD {}').format(sql.Identifier(cfg['DB_USER']),sql.Literal(password)))
 if not c.execute('SELECT 1 FROM pg_database WHERE datname=%s',(cfg['DB_NAME'],)).fetchone():c.execute(sql.SQL('CREATE DATABASE {}').format(sql.Identifier(cfg['DB_NAME'])))
p=ROOT/'.env';existing=p.read_text() if p.exists() else ''
# Keep user settings and append the generated password only. Last assignment wins.
p.write_text(existing.rstrip()+'\nDB_PASSWORD='+shlex.quote(password)+'\n');p.chmod(0o600)
print('Generated a local PostgreSQL password in ignored .env.')
