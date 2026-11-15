"""Public bibliographic searches; no credentials or browser validation bypass."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import urllib.parse,urllib.request,json,hashlib,datetime
R=Path(__file__).parent;O=R/'sources';O.mkdir(exist_ok=True)
QUERIES={
 'sensory_motor':'Drosophila proprioception sensory motor connectome',
 'load_feedback':'Drosophila campaniform sensilla load walking',
 'braking':'Drosophila walking braking stance BRK',
 'MF_identity':'Drosophila LUL130 LUL152 MF14',
 'phase_gate':'Drosophila DNg13 phase walking',
 'hunger_stop':'Drosophila starvation sugar feeding walking stopping',
 'adult_sensory':'Drosophila 13Bb 10Ba club claw hook'
}
def get(job):
 key,source,url=job;row={'query_id':key,'query':QUERIES[key],'source':source,'url':url,'retrieved_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'ApplepieResearch/1.0 public-literature-review'}),timeout=45) as f:raw=f.read();row.update(status=f.status,content_type=f.headers.get('Content-Type'))
  obj=json.loads(raw);p=O/(key+'-'+source+'.json');p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n');row.update(file=str(p.relative_to(R)),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size)
 except Exception as e:row.update(error=type(e).__name__+': '+str(e))
 return row
jobs=[]
for key,q in QUERIES.items():
 jobs.append((key,'epmc','https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urllib.parse.urlencode({'query':q,'format':'json','pageSize':12,'resultType':'core'})))
 jobs.append((key,'crossref','https://api.crossref.org/works?'+urllib.parse.urlencode({'query':q,'rows':8,'select':'DOI,title,published,URL,type'})))
 jobs.append((key,'openalex','https://api.openalex.org/works?'+urllib.parse.urlencode({'search':q,'per-page':8})))
with ThreadPoolExecutor(max_workers=5) as ex:rows=list(ex.map(get,jobs))
(R/'search-manifest.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
for r in rows:print(r['query_id'],r['source'],r.get('status'),r.get('error',''))
