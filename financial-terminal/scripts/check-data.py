from pathlib import Path
import hashlib,json,csv
from settings import read_settings
DATA=Path(read_settings()['DATA_DIR']);p=json.loads((DATA/'provenance.json').read_text());stocks=json.loads((DATA/'stocks.json').read_text())
assert hashlib.file_digest((DATA/'daily.csv').open('rb'),'sha256').hexdigest()==p['dailyCsvSha256'], 'Daily data hash mismatch'
with (DATA/'daily.csv').open() as f:rows=list(csv.DictReader(f))
assert len(rows)==p['rows'] and len(stocks)==p['symbols']
assert len({(x['symbol'],x['date']) for x in rows})==len(rows)
assert {s['symbol'] for s in stocks}=={x['symbol'] for x in rows}
for s in stocks:
 xs=[x for x in rows if x['symbol']==s['symbol']];assert len(xs)==s['sessions'];assert xs[0]['date']==s['firstDate'] and xs[-1]['date']==s['lastDate']
for x in rows:
 o,h,l,c=map(float,[x['open'],x['high'],x['low'],x['close']]);assert 0<l<=min(o,c)<=max(o,c)<=h;assert int(x['volume'])>=0
print(f"Verified {len(stocks)} symbols / {len(rows)} daily rows, OHLC invariants and provenance hash.")
