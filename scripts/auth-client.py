"""CLI authentication uses explicitly supplied credentials, never a shipped default account."""
import http.cookiejar,json,os,urllib.request

def authenticated(base):
 jar=http.cookiejar.CookieJar();opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
 username=os.environ.get('APERTURE_USERNAME');password=os.environ.get('APERTURE_PASSWORD')
 if not username or not password:raise RuntimeError('Set APERTURE_USERNAME and APERTURE_PASSWORD to an existing account for API verification')
 req=urllib.request.Request(base+'/api/accounts/loginuser',data=json.dumps(dict(username=username,password=password)).encode(),headers={'Content-Type':'application/json'})
 with opener.open(req) as response:assert response.status==200
 return opener
