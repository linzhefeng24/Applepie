"""Assemble source-indexed translations written in the current assistant session."""
from pathlib import Path
import argparse,json,hashlib
R=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--document',choices=['benton','dorkenwald','all'],default='all');a=p.parse_args();data=json.loads((R/'segments.json').read_text());mapping={}
for path in sorted((R/'drafts').glob('*.json')):
 for key,text in json.loads(path.read_text()).items():assert key not in mapping,key;mapping[key]=text
if a.document!='all':data['documents']={a.document:data['documents'][a.document]}
missing=[];total=0
for d in data['documents'].values():
 for page in d['pages']:
  for s in page['segments']:
   total+=1
   if s['mode']=='original_reference':s.update(translation=s['source'],status='reference_preserved')
   elif s['id'] in mapping:s.update(translation=mapping[s['id']],status='assistant_translated')
   else:missing.append(s['id'])
assert not missing,'Still missing: '+str(missing)
data.update(translation_status='complete',failed_segments=[],engine='Translated directly by the assistant within the conversation; reference bibliographic entries and figure identifiers preserved; failed local model trials not used',source_segments=total,manual_draft_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (R/'drafts').glob('*.json')})
(R/'translated.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');print('Complete selected documents',list(data['documents']),total,'segments')
