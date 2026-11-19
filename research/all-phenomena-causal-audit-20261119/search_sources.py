"""Re-query public literature metadata; save successes and failures with exact provenance."""
from pathlib import Path
import urllib.request,urllib.parse,json,hashlib,datetime
R=Path(__file__).resolve().parent;D=R/'sources';D.mkdir(exist_ok=True);out=[]
for term in ['Drosophila MF14 LUL152','Drosophila LUL130 connectome','Drosophila moonwalker ascending MAN connectome','Drosophila CxHP8 connectome hair plate','Drosophila DopaMeander','Drosophila presynaptic inhibition hook claw chief 9A']:
 u='https://www.ebi.ac.uk/europepmc/webservices/rest/search?format=json&pageSize=8&query='+urllib.parse.quote(term);name='epmc-'+hashlib.sha256(term.encode()).hexdigest()[:10]+'.json';row={'query':term,'url':u,'provider':'Europe PMC','retrieval_UTC':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 try:
  raw=urllib.request.urlopen(u,timeout=25).read();(D/name).write_bytes(raw);x=json.loads(raw);row.update(file=name,sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),hits=[{k:v.get(k) for k in ['title','doi','pmcid','id']} for v in x['resultList']['result']])
 except Exception as e:row['error']=str(e)
 out.append(row)
(R/'search_manifest.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print([(x['query'],len(x.get('hits',[])),x.get('error')) for x in out])
