"""Opt-in destructive-to-processes development check: restart this project's services/database."""
from pathlib import Path
import json,subprocess,urllib.request
ROOT=Path(__file__).resolve().parents[1]
def post(s,port,name,body):
 req=urllib.request.Request(f'http://127.0.0.1:{port}/api/{s}/{name}',data=json.dumps(body).encode(),headers={'Content-Type':'application/json'})
 with urllib.request.urlopen(req,timeout=180) as r:return json.load(r)
p=dict(symbols=['AAPL','AMZN','GOOG','BAC','GLD'],start='2022-03-07',end='2026-10-23',maxWeight=.4,riskAversion=3,skewPreference=1,kurtosisAversion=1,lookback=126,rebalance=63,costBps=10,model='mvsk')
a=post('analysis',8103,'runanalysis',dict(parameters=p))
saved=post('portfolio',8102,'savereport',dict(title='Restart verification - temporary',kind='analysis',parameters=p,result=a))['id']
try:
 subprocess.run(['bash','scripts/stop-services.sh','--database'],cwd=ROOT,check=True)
 subprocess.run(['bash','scripts/start-services.sh'],cwd=ROOT,check=True)
 reports=post('portfolio',8102,'listreports',{})['reports'];report=next(r for r in reports if r['id']==saved)
 assert report['result']==a and report['parameters']==p
 market=post('market',8101,'liststocks',{});assert market['provenance']['rows']==37247 and len(market['stocks'])==32
 print('PASS: full application + PostgreSQL restart preserved research report and refreshed real market data.')
finally:
 post('portfolio',8102,'deletereport',dict(id=saved))
