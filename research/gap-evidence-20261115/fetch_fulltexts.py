"""Fetch open-access Europe PMC full text and extract searchable paragraphs."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import urllib.request,json,hashlib,xml.etree.ElementTree as ET
R=Path(__file__).parent;O=R/'sources';IDS=['PMC12056673','PMC13384506','PMC12778575','PMC11446846','PMC8665017','PMC11348827','PMC12279373','PMC13009157','PMC12975126']
def get(i):
 u=f'https://www.ebi.ac.uk/europepmc/webservices/rest/{i}/fullTextXML';d={'pmcid':i,'url':u}
 try:
  raw=urllib.request.urlopen(u,timeout=45).read();root=ET.fromstring(raw);p=O/(i+'.xml');p.write_bytes(raw);d.update(sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),file=str(p.relative_to(R)))
  ps=[' '.join(x.itertext()) for x in root.iter() if x.tag in ['article-title','p','table-wrap','caption']];(O/(i+'.txt')).write_text('\n'.join(ps)+'\n');d['title']=' '.join(root.find('.//article-title').itertext())
 except Exception as e:d['error']=str(e)
 return d
with ThreadPoolExecutor(max_workers=4) as ex:rows=list(ex.map(get,IDS))
(R/'fulltext-manifest.json').write_text(json.dumps(rows,indent=2)+'\n')
for x in rows:print(x['pmcid'],x.get('title'),x.get('error'))
