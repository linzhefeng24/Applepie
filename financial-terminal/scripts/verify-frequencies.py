"""Independent OHLCV comparisons against bundled real minutes and daily CSV."""
from pathlib import Path
import sys,json,urllib.request,urllib.error
import pandas as pd
from settings import read_settings
cfg=read_settings();base=cfg['FRONTEND_URL'];data=Path(cfg['DATA_DIR'])
import importlib.util
spec=importlib.util.spec_from_file_location('auth_client',Path(__file__).with_name('auth-client.py'));auth=importlib.util.module_from_spec(spec);spec.loader.exec_module(auth)
opener=auth.authenticated(base)
def post(name,body):
 req=urllib.request.Request(base+'/api/resampling/'+name,data=json.dumps(body).encode(),headers={'Content-Type':'application/json'})
 with opener.open(req) as response:return json.load(response)
def bars(start,end,frequency):return post('getbars',dict(symbol='AAPL',start=start,end=end,frequency=frequency))
meta=post('listfrequencies',dict(symbol='AAPL'));assert {f['code'] for f in meta['frequencies'] if f['available']}=={'1y','1mo','1d','5min','2min','1min'}
minute=pd.read_csv(data/'minutes/AAPL.csv.gz',parse_dates=['time']);day=minute.time.max().strftime('%Y-%m-%d');selected=minute[minute.time.dt.strftime('%Y-%m-%d')==day].set_index('time')
def compare(actual,expected):
 assert len(actual)==len(expected),(len(actual),len(expected))
 for result,(stamp,row) in zip(actual,expected.iterrows()):
  assert result['date']==stamp.strftime('%Y-%m-%d %H:%M:%S')
  for key in ['open','high','low','close']:assert abs(result[key]-row[key])<1e-9,(key,result,row)
  assert result['volume']==row.volume and result['minutes']==row.minutes
for frequency,size in [('1min',1),('2min',2),('5min',5)]:
 expected=selected.resample(f'{size}min',origin='start_day').agg(open=('open','first'),high=('high','max'),low=('low','min'),close=('close','last'),volume=('volume','sum'),minutes=('close','size')).dropna(subset=['open'])
 response=bars(day,day,frequency);compare(response['bars'],expected)
 assert response['incompleteBars']==int((expected.minutes<size).sum())
 print('PASS',frequency,len(expected),'real source buckets')
daily=pd.read_csv(data/'daily.csv',parse_dates=['date']);daily=daily[daily.symbol=='AAPL'].set_index('date')
for frequency,rule in [('1mo','MS'),('1y','YS')]:
 expected=daily.resample(rule).agg(open=('open','first'),high=('high','max'),low=('low','min'),close=('close','last'),volume=('volume','sum'),minutes=('minutes','sum'))
 actual=bars('2022-03-07',day,frequency)['bars'];assert len(actual)==len(expected)
 for result,(stamp,row) in zip(actual,expected.iterrows()):
  assert result['date']==stamp.strftime('%Y-%m-%d')
  for key in ['open','high','low','close','volume','minutes']:assert abs(result[key]-row[key])<1e-7,(frequency,key)
 print('PASS',frequency,len(actual),'calendar OHLCV buckets')
for body in [dict(symbol='AAPL',start=minute.time.min().strftime('%Y-%m-%d'),end=day,frequency='1min'),dict(symbol='AAPL',start=day,end=day,frequency='10sec')]:
 try:post('getbars',body)
 except urllib.error.HTTPError as error:assert error.code==400
 else:raise AssertionError('oversized or unsupported frequency accepted')
# A short-lived fixture demonstrates year bars are unavailable without sufficient calendar history.
import psycopg
env=json.loads((Path(__file__).resolve().parents[1]/'.run/service-env/daily.json').read_text())
with psycopg.connect(host=env['DB_HOST'],port=env['DB_PORT'],dbname=env['DB_NAME'],user=env['DB_USER'],password=env['DB_PASSWORD'],autocommit=True) as connection:
 try:
  connection.execute("INSERT INTO market.daily_bar VALUES ('SHORTTEST','2026-10-01',1,1,1,1,0,1)")
  short=post('listfrequencies',dict(symbol='SHORTTEST'))
  assert not next(f for f in short['frequencies'] if f['code']=='1y')['available']
 finally:connection.execute("DELETE FROM market.daily_bar WHERE symbol='SHORTTEST'")
print('PASS: source timestamps, no fabricated minutes, OHLCV conservation, query limit and short-history year availability.')
