"""Explicitly copy old anonymous research into one chosen existing account; never deletes source data."""
import argparse,json,os,uuid
import psycopg
from psycopg.types.json import Jsonb
from settings import ROOT
parser=argparse.ArgumentParser();parser.add_argument('--owner',required=True,help='Existing account UUID that explicitly receives the old anonymous data');args=parser.parse_args();owner=str(uuid.UUID(args.owner))
def connect(name):
 e=json.loads((ROOT/'.run/service-env'/f'{name}.json').read_text());return psycopg.connect(host=e['DB_HOST'],port=e['DB_PORT'],dbname=e['DB_NAME'],user=e['DB_USER'],password=e['DB_PASSWORD'])
with connect('accounts') as c:
 if not c.execute('SELECT 1 FROM accounts.users WHERE id=%s',(owner,)).fetchone():raise SystemExit('Target account does not exist')
# Supply a libpq DSN in the environment; it is never printed or stored in source.
with psycopg.connect(os.environ['APERTURE_LEGACY_DSN']) as legacy:
 watch=legacy.execute('SELECT symbol,created_at FROM portfolio.watchlist').fetchall()
 reports=legacy.execute('SELECT id,title,kind,parameters,result,created_at FROM portfolio.report').fetchall()
with connect('watchlist') as c:
 for symbol,created in watch:c.execute('INSERT INTO watchlist.watchlist(user_id,symbol,created_at) VALUES (%s,%s,%s) ON CONFLICT DO NOTHING',(owner,symbol,created))
with connect('reports') as c:
 for id,title,kind,parameters,result,created in reports:c.execute('INSERT INTO reports.report(id,user_id,title,kind,parameters,result,created_at) VALUES (%s,%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING',(id,owner,title,kind,Jsonb(parameters),Jsonb(result),created))
print(f'Copied {len(watch)} watchlist entries and {len(reports)} reports to the selected account; original data untouched. Re-running is idempotent.')
