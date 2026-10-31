"""Real HTTP integration checks, including independent CSV/statistical comparisons."""
from pathlib import Path
import json,urllib.request,urllib.error,csv,math,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'quant'))
from engine import statistics
ROOT=Path(__file__).resolve().parents[1]
from settings import read_settings
CFG=read_settings()
BASE={s:CFG[s.upper()+'_URL'] for s in ['market','portfolio','analysis']}
def post(service,name,body):
 r=urllib.request.Request(f'{BASE[service]}/api/{service}/{name}',data=json.dumps(body).encode(),headers={'Content-Type':'application/json'})
 with urllib.request.urlopen(r,timeout=180) as response:return json.load(response)
def bad(service,name,body):
 try:post(service,name,body)
 except urllib.error.HTTPError as e:assert e.code==400;return
 raise AssertionError('Invalid input accepted')
market=post('market','liststocks',{});assert len(market['stocks'])==32 and len(market['quotes'])==32
with (Path(CFG['DATA_DIR'])/'daily.csv').open() as f:expected=[x for x in csv.DictReader(f) if x['symbol']=='AAPL']
stock=post('market','getstock',dict(symbol='AAPL',start='2022-03-07',end='2026-10-23'))
assert len(stock['bars'])==len(expected)==1164
for a,b in zip(stock['bars'],expected):
 assert a['date']==b['date'] and a['volume']==int(b['volume']) and abs(a['close']-float(b['close']))<1e-8
prices=[float(x['close']) for x in expected];reference=statistics([b/a-1 for a,b in zip(prices,prices[1:])])
for key in ['totalReturn','annualReturn','volatility','sharpe','maxDrawdown','skewness','excessKurtosis']:assert abs(reference[key]-stock['metrics'][key])<1e-9,key
assert len(stock['annual'])==5 and stock['annual'][0]['partial'] and stock['annual'][-1]['partial']
bad('market','getstock',dict(symbol='UNKNOWN',start='2022-03-07',end='2026-10-23'))
bad('market','getstock',dict(symbol='AAPL',start='2026-01-01',end='2022-01-01'))
p=dict(symbols=['AAPL','AMZN','GOOG','BAC','GLD'],start='2022-03-07',end='2026-10-23',maxWeight=.4,riskAversion=3,skewPreference=1,kurtosisAversion=1,lookback=126,rebalance=63,costBps=10,model='mvsk')
a=post('analysis','runanalysis',dict(parameters=p));assert len(a['models'])==5
for model in a['models']:
 assert model['converged'] and abs(sum(model['weights'])-1)<1e-6 and min(model['weights'])>=-1e-7 and max(model['weights'])<=.400001
b=post('analysis','runbacktest',dict(parameters=p));assert len(b['results'])==4
for result in b['results']:
 assert result['curve'][0]['value']==1 and len(result['curve'])>500
 assert abs(result['curve'][-1]['value']-1-result['metrics']['totalReturn'])<1e-9
 for t in result['trades']:assert t['signalEnd']<t['executionDate']<t['returnDate']
bad('analysis','runanalysis',dict(parameters=dict(p,maxWeight=.1)))
bad('analysis','runanalysis',dict(parameters=dict(p,symbols=['AAPL','AAPL'])))
bad('analysis','runbacktest',dict(parameters=dict(p,start='2026-09-01')))
bad('portfolio','savereport',dict(title='invalid',kind='analysis',parameters={},result={}))
watch=post('portfolio','listwatchlist',{})['symbols']
try:
 assert 'AAPL' in post('portfolio','setwatchlist',dict(symbol='AAPL',selected=True))['symbols']
finally:post('portfolio','setwatchlist',dict(symbol='AAPL',selected='AAPL' in watch))
saved=post('portfolio','savereport',dict(title='API verification - temporary',kind='analysis',parameters=p,result=a))['id']
try:
 report=next(r for r in post('portfolio','listreports',{})['reports'] if r['id']==saved);assert report['parameters']==p and report['result']==a
finally:post('portfolio','deletereport',dict(id=saved))
print('PASS: real database rows and metrics, five optimizers, four rolling backtests, invalid inputs, watchlist, report persistence/delete.')
