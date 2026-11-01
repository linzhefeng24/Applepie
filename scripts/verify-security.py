"""Live authentication, authorization and owner-isolation checks against an isolated test deployment.
Requires APERTURE_USERNAME/PASSWORD for an existing admin; creates only uniquely named test users.
"""
import http.cookiejar,importlib.util,json,os,secrets,urllib.request,urllib.error
from settings import read_settings,ROOT
cfg=read_settings();base=cfg['FRONTEND_URL']
class Client:
 def __init__(self):self.jar=http.cookiejar.CookieJar();self.op=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.jar))
 def post(self,path,body=None,expected=200,headers=None):
  request=urllib.request.Request(base+path,data=json.dumps({} if body is None else body).encode(),headers={'Content-Type':'application/json',**(headers or {})})
  try:
   with self.op.open(request,timeout=90) as r:status=r.status;result=json.load(r)
  except urllib.error.HTTPError as e:status=e.code;result=json.load(e)
  assert status==expected,(path,status,result)
  return result
admin=Client();admin.post('/api/accounts/loginuser',dict(username=os.environ['APERTURE_USERNAME'],password=os.environ['APERTURE_PASSWORD']))
anonymous=Client();anonymous.post('/api/catalog/listsecurities',expected=401)
clients=[]
for _ in range(2):
 c=Client();username='sec_'+secrets.token_hex(6);password=secrets.token_urlsafe(16)
 response=c.post('/api/accounts/registeruser',dict(username=username,password=password,displayName='Security verification'))
 assert 'sessionToken' not in response;u=response['user'];assert u['role']=='analyst'
 assert any(cookie.name=='aperture_session' and cookie.has_nonstandard_attr('HttpOnly') and cookie.get_nonstandard_attr('SameSite')=='Strict' for cookie in c.jar)
 clients.append((c,u,username,password))
a,ua,na,pa=clients[0];b,ub,nb,pb=clients[1]
a.post('/api/accounts/loginuser',dict(username=na,password='wrongpassword'),expected=401)
a.post('/api/authorization/listusers',expected=403)
a.post('/api/watchlist/setwatchlist',dict(symbol='AAPL',selected=True))
assert a.post('/api/watchlist/listwatchlist')['symbols']==['AAPL'];assert not b.post('/api/watchlist/listwatchlist')['symbols']
a.post('/api/watchlist/listwatchlist',dict(userId=ub['id']),expected=400)
a.post('/api/watchlist/setwatchlist',dict(symbol='GOOG',selected=True),expected=403,headers={'Origin':'https://foreign.invalid'})
params=dict(symbols=['AAPL','GOOG'],start='2023-01-01',end='2026-10-23',maxWeight=.8,riskAversion=3,skewPreference=1,kurtosisAversion=1,lookback=126,rebalance=63,costBps=5,model='mvsk')
report=a.post('/api/reports/savereport',dict(title='Owner isolation',kind='analysis',parameters=params,result={'symbols':['AAPL','GOOG'],'start':params['start'],'end':params['end'],'models':[]}))
report_id=report['report']['id'] if 'report' in report else report.get('id')
if not report_id:report_id=a.post('/api/reports/listreports')['reports'][0]['id']
assert not b.post('/api/reports/listreports')['reports'];b.post('/api/reports/deletereport',dict(id=report_id));assert a.post('/api/reports/listreports')['reports'][0]['id']==report_id
a.post('/api/reports/deletereport',dict(id=report_id))
admin.post('/api/authorization/setaccess',dict(targetUserId=ua['id'],newRole='viewer',enabled=True))
a.post('/api/watchlist/setwatchlist',dict(symbol='GOOG',selected=True),expected=403)
a.post('/api/optimization/runanalysis',dict(parameters=params),expected=403)
a.post('/api/backtest/runbacktest',dict(parameters=params),expected=403)
assert a.post('/api/catalog/listsecurities')['stocks']
admin.post('/api/authorization/setaccess',dict(targetUserId=ua['id'],newRole='analyst',enabled=True))
# Password changes invalidate pre-existing sessions via credential version, even before revoke completes.
second=Client();second.post('/api/accounts/loginuser',dict(username=na,password=pa))
a.post('/api/accounts/changepassword',dict(currentPassword=pa,newPassword=pa+'x'))
second.post('/api/accounts/getcurrentuser',expected=401)
a.post('/api/accounts/loginuser',dict(username=na,password=pa),expected=401)
a.post('/api/accounts/loginuser',dict(username=na,password=pa+'x'))
sessions=a.post('/api/sessions/getsessions')['sessions'];current=next(s for s in sessions if s['current'])
a.post('/api/sessions/revokesession',dict(sessionId=current['id']));a.post('/api/catalog/listsecurities',expected=401)
b.post('/api/sessions/logoutuser');b.post('/api/catalog/listsecurities',expected=401)
me=admin.post('/api/accounts/getcurrentuser')['user'];admin.post('/api/authorization/setaccess',dict(targetUserId=me['id'],newRole='viewer',enabled=True),expected=400)
# Validate internal authentication and caller allowlists without disclosing raw credentials.
spec=importlib.util.spec_from_file_location('services_env',ROOT/'scripts/service-environment.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
for caller,target,path,body in [('quotes','accounts','findusers',{}),('optimization','quant_backtest','backtest',{})]:
 env=m.environment(caller);targetenv=m.environment(target);url='http://127.0.0.1:'+targetenv['HTTP_PORT']+('/internal/'+target+'/'+path if target=='accounts' else '/'+path)
 req=urllib.request.Request(url,data=json.dumps(body).encode(),headers={'Content-Type':'application/json','X-Service-Name':caller,'X-Internal-Token':env['INTERNAL_SERVICE_TOKEN']})
 try:urllib.request.urlopen(req);raise AssertionError('Cross-service privilege bypass')
 except urllib.error.HTTPError as e:assert e.code==403
# Each app role is non-superuser and cannot authenticate to another cluster.
import psycopg
owned=[s for s in m.REGISTRY if s['database']]
for s in owned:
 env=m.environment(s['name']);other=m.environment(next(x['name'] for x in owned if x['name']!=s['name']))
 with psycopg.connect(host=env['DB_HOST'],port=env['DB_PORT'],dbname=env['DB_NAME'],user=env['DB_USER'],password=env['DB_PASSWORD']) as c:assert not c.execute('SELECT rolsuper FROM pg_roles WHERE rolname=current_user').fetchone()[0]
 try:psycopg.connect(host=other['DB_HOST'],port=other['DB_PORT'],dbname=other['DB_NAME'],user=env['DB_USER'],password=env['DB_PASSWORD'],connect_timeout=2);raise AssertionError('Cross-cluster credentials accepted')
 except psycopg.OperationalError:pass
for s in m.REGISTRY:
 if not s['database']:assert not any(k.startswith('DB_') for k in json.loads((ROOT/'.run/service-env'/f"{s['name']}.json").read_text()))
print('PASS: login, HttpOnly cookie, roles, private watchlists/reports, origin checks, password/session invalidation, last-admin protection, internal caller allowlists, 8 database instances and credential isolation.')
