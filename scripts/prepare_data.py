"""Verified Release minutes -> a reproducible 32-symbol, daily OHLCV teaching subset."""
from pathlib import Path
import argparse, hashlib, io, json, zipfile
import numpy as np
import pandas as pd
ROOT = Path(__file__).resolve().parents[1]
from settings import read_settings
from clean_minutes import clean_minutes
DATA = Path(read_settings()["DATA_DIR"])
SHA = '3228a7935ab3b8fffa857c44cddf2795f6b37e76e965ab2787d364afd435a693'
SYMBOLS = {
 'AAPL':('Apple','科技'), 'AMZN':('Amazon','消费'), 'GOOG':('Alphabet','科技'),
 'AMD':('AMD','半导体'), 'ADBE':('Adobe','软件'), 'AVGO':('Broadcom','半导体'),
 'ASML':('ASML','半导体'), 'AMAT':('Applied Materials','半导体'),
 'BAC':('Bank of America','金融'), 'C':('Citigroup','金融'), 'GS':('Goldman Sachs','金融'),
 'AXP':('American Express','金融'), 'BLK':('BlackRock','金融'), 'BRK-B':('Berkshire Hathaway B','金融'),
 'ABBV':('AbbVie','医疗'), 'ABT':('Abbott','医疗'), 'AMGN':('Amgen','医疗'), 'GILD':('Gilead','医疗'),
 'CVX':('Chevron','能源'), 'COP':('ConocoPhillips','能源'), 'BP':('BP ADR','能源'),
 'COST':('Costco','消费'), 'HD':('Home Depot','消费'), 'DIS':('Disney','消费'),
 'CAT':('Caterpillar','工业'), 'GE':('GE Aerospace','工业'), 'BA':('Boeing','工业'),
 'F':('Ford','汽车'), 'GM':('General Motors','汽车'), 'CRM':('Salesforce','软件'),
 'CSCO':('Cisco','科技'), 'GLD':('SPDR Gold Shares','黄金ETF')}
def prepare(archive: Path):
 assert hashlib.file_digest(archive.open('rb'),'sha256').hexdigest() == SHA, 'Release SHA256 mismatch'
 frames, stocks, audits = [], [], []
 with zipfile.ZipFile(archive) as z:
  for symbol,(name,sector) in SYMBOLS.items():
   member=f'part1/{symbol}_clean_1min.parquet'
   d=pd.read_parquet(io.BytesIO(z.read(member)))
   raw=len(d);sources=sorted(d.source.dropna().unique().tolist())
   d,duplicates,rejected=clean_minutes(d)
   # Source timestamps are naive; retain their recorded session date, do not invent UTC conversion.
   d['date']=d.datetime.dt.strftime('%Y-%m-%d')
   daily=d.groupby('date',sort=True).agg(open=('Open','first'),high=('High','max'),low=('Low','min'),close=('Close','last'),volume=('Volume','sum'),minutes=('Close','size')).reset_index()
   daily.insert(0,'symbol',symbol);frames.append(daily)
   jumps=int((daily.close.pct_change().abs()>.25).sum())
   stocks.append(dict(symbol=symbol,name=name,sector=sector,currency='USD',firstDate=daily.date.iloc[0],lastDate=daily.date.iloc[-1],sessions=len(daily),source=','.join(sources)))
   audits.append(dict(symbol=symbol,rawMinutes=raw,duplicates=duplicates,rejectedMinutes=rejected,sources=sources,dailyRows=len(daily),sessionsUnder300Minutes=int((daily.minutes<300).sum()),dailyMovesOver25Pct=jumps))
   print(symbol,raw,'->',len(daily),flush=True)
 out=DATA;out.mkdir(parents=True,exist_ok=True);pd.concat(frames).to_csv(out/'daily.csv',index=False,float_format='%.8f')
 (out/'stocks.json').write_text(json.dumps(stocks,ensure_ascii=False,indent=2))
 report=dict(release='https://github.com/linzhefeng24/Applepie/releases/tag/data_v1',asset='part1.zip',sha256=SHA,selection='32 named US-listed equities/ADR and gold ETF from part1 only; part2/part3 not imported',frequency='daily from all valid recorded minutes, not exchange consolidated official daily bars',timezone='naive source timestamps; session date retained; timezone not verified',adjustment='unknown; no corporate-action or dividend data supplied; price returns, not total returns',volume='sum of source minute volume; source includes IEX, not whole-market volume',financials='not supplied: revenue, ROE, PE, PB, dividends unavailable',aggregation='stable chronological sort; duplicate timestamps keep last; discard nonfinite/nonpositive/inconsistent OHLC or negative volume; first open/max high/min low/last close/sum volume',survivorship='curated teaching subset; not suitable for claims about unbiased whole-market strategy performance',symbols=len(stocks),rows=sum(x['dailyRows'] for x in audits),audits=audits)
 report['dailyCsvSha256']=hashlib.file_digest((out/'daily.csv').open('rb'),'sha256').hexdigest()
 (out/'provenance.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--archive',type=Path,default=DATA/'raw/part1.zip');prepare(parser.parse_args().archive)
