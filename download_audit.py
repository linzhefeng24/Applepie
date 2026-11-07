from pathlib import Path
import argparse,hashlib,json,time,urllib.request
BASE='https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/'
parser=argparse.ArgumentParser();parser.add_argument('--only',choices=['code','data','all'],default='all');args=parser.parse_args()
R=Path(__file__).resolve().parent;chunks=R/'.audit_chunks';chunks.mkdir(exist_ok=True)
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
with urllib.request.urlopen(BASE+'audit_download_manifest.json',timeout=60) as f:raw=f.read()
assert hashlib.sha256(raw).hexdigest()=='04c9e67683bbb6cc4251fd3fdaba6a90c45fe9a7f03e7234b465d4a97c8e53a6', 'Manifest checksum mismatch'
plan=json.loads(raw)
for asset in plan['assets']:
 if args.only not in ['all',asset['key']]:continue
 target=R/asset['name']
 if target.exists():
  if sha(target)==asset['sha256']:print('Already verified',target.name);continue
  raise SystemExit('Existing output differs; rename it first: '+target.name)
 for part in asset['chunks']:
  p=chunks/Path(part['path']).name
  if p.exists() and p.stat().st_size==part['bytes'] and sha(p)==part['sha256']:continue
  print('Downloading',p.name,flush=True)
  for attempt in range(5):
   try:
    with urllib.request.urlopen(BASE+part['path'],timeout=180) as src,p.open('wb') as dst:
     while b:=src.read(8*1024*1024):dst.write(b)
    assert p.stat().st_size==part['bytes'] and sha(p)==part['sha256']
    break
   except Exception:
    if attempt==4:raise
    time.sleep(3*(attempt+1))
 temporary=target.with_name(target.name+'.merging')
 with temporary.open('wb') as dst:
  for part in asset['chunks']:
   with (chunks/Path(part['path']).name).open('rb') as src:
    while b:=src.read(8*1024*1024):dst.write(b)
 assert temporary.stat().st_size==asset['bytes'] and sha(temporary)==asset['sha256']
 temporary.rename(target);print('Merged and verified',target.name,flush=True)
