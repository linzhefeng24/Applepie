"""Try public scientific data endpoints from the GitHub runner's normal network.
Only published-hash verified files enter the draft archive. Failures are retained
without recording cookies, credentials or signed storage redirect URLs.
"""
from pathlib import Path
import hashlib,json,os,subprocess,tempfile,urllib.request,urllib.error
R=Path(__file__).parent;TAG='public-feco-inputs-20261115'
def gh(*args):return subprocess.check_output(['gh',*args],text=True)
def sha(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 return h.hexdigest()
def main():
 repo=os.environ['GITHUB_REPOSITORY'];rev=os.environ['GITHUB_SHA'];manifest=json.load(open(R/'inputs.json'));releases=json.loads(gh('api',f'repos/{repo}/releases?per_page=100'));release=next((x for x in releases if x['tag_name']==TAG),None)
 if release is None:
  gh('release','create',TAG,'--repo',repo,'--draft','--target',rev,'--title','Verified public FeCO inputs and access diagnostics','--notes','Public dataset sources and verified files only. Failure manifests distinguish unavailable downloads from recovered input.');release=next(x for x in json.loads(gh('api',f'repos/{repo}/releases?per_page=100')) if x['tag_name']==TAG)
 records=[]
 with tempfile.TemporaryDirectory() as directory:
  for item in manifest['inputs']:
   record={**item,'attempts':[],'status':'not_recovered'};path=Path(directory)/item['name'];assets=json.loads(gh('api',f'repos/{repo}/releases/{release["id"]}'))['assets'];existing=next((x for x in assets if x['name']==item['name']),None)
   if existing and existing.get('digest')=='sha256:'+item['sha256'] and existing['size']==item['bytes']:record.update(status='verified_release_asset',asset_id=existing['id'])
   else:
    for url in item['urls']:
     try:
      request=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 (public scientific dataset reproducibility)'})
      with urllib.request.urlopen(request,timeout=25) as source,path.open('wb') as target:
       for chunk in iter(lambda:source.read(4*1024*1024),b''):target.write(chunk)
      size=path.stat().st_size;digest=sha(path);record['attempts'].append({'public_url':url,'bytes':size,'sha256':digest})
      if size!=item['bytes'] or digest!=item['sha256']:continue
      if existing:raise RuntimeError('Conflicting existing archive asset, never overwrite')
      gh('release','upload',TAG,str(path),'--repo',repo);assets=json.loads(gh('api',f'repos/{repo}/releases/{release["id"]}'))['assets'];asset=next(x for x in assets if x['name']==item['name']);assert asset['digest']=='sha256:'+item['sha256'];record.update(status='verified_release_asset',asset_id=asset['id'],asset_url=asset['browser_download_url']);break
     except urllib.error.HTTPError as error:record['attempts'].append({'public_url':url,'http_status':error.code})
     except (TimeoutError,urllib.error.URLError) as error:record['attempts'].append({'public_url':url,'error_type':type(error).__name__})
   path.unlink(missing_ok=True);records.append(record);print(item['name'],record['status'],flush=True)
  output={'dataset_doi':manifest['dataset_doi'],'dataset_version_id':manifest['dataset_version_id'],'workflow_code_revision':rev,'release_id':release['id'],'records':records,'interpretation':'Only verified_release_asset means recovered. Failed public downloads are not declared restored.'};path=Path(directory)/('recovery-'+rev+'.json');path.write_text(json.dumps(output,indent=2)+'\n');gh('release','upload',TAG,str(path),'--repo',repo)
if __name__=='__main__':main()
