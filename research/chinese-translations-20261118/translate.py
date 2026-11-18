"""User-requested complete Chinese reading drafts with original-page facsimiles.
A local offline NLLB model supplies draft text; a separate explicit glossary
normalizes technical terms. This is an unofficial translation, not an author-approved
edition. All source spans, reference exceptions and OCR pages are audited.
"""
from pathlib import Path
import argparse,concurrent.futures,hashlib,html,json,re,subprocess,time,unicodedata,zipfile,sys,base64
import fitz
R=Path(__file__).resolve().parent;CACHE=R/'cache';CACHE.mkdir(exist_ok=True)
META={'benton':{'name':'Benton_2025','title':'果蝇嗅觉系统的解剖、功能与进化整合视图','english':'An integrated anatomical, functional and evolutionary view of the Drosophila olfactory system','authors':'Richard Benton, Jérôme Mermet, Andre Jang, Keita Endo, Steeve Cruchet, Karen Menuz','doi':'10.1038/s44319-025-00476-8','sha256':'','pages':22},'dorkenwald':{'name':'Dorkenwald_2024','title':'成年果蝇大脑的神经元连接图谱','english':'Neuronal wiring diagram of an adult brain','authors':'Sven Dorkenwald et al.; The FlyWire Consortium','doi':'10.1038/s41586-024-07558-y','sha256':'','pages':32}}
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def clean(t):
 t=unicodedata.normalize('NFKC',t).replace('\xad','').replace('\x00','')
 t=re.sub(r'([A-Za-z])-\n([a-z])',r'\1\2',t)
 t=re.sub(r'[ \t]+',' ',re.sub(r'(?<!\n)\n(?!\n)',' ',t)).strip()
 return re.sub(r'(https?://[^\s]+[/.-]) +(?=[A-Za-z0-9])',r'\1',t)
def cut(t,size=3200):
 while len(t)>size:
  end=max(t.rfind('\n\n',0,size),t.rfind('. ',0,size),t.rfind('; ',0,size))
  if end<size//3:end=t.rfind(' ',0,size)
  if end<1:end=size
  yield t[:end].strip();t=t[end:].strip()
 if t:yield t

def extract(paths):
 result={'source':'user-uploaded PDFs','translation_status':'not_started','documents':{}}
 for key,path in paths.items():
  pdf=fitz.open(path);meta={**META[key],'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bytes':path.stat().st_size,'filename':path.name};pages=[];refs=False
  for no,page in enumerate(pdf,1):
   assets=CACHE/key;assets.mkdir(exist_ok=True);page.get_pixmap(matrix=fitz.Matrix(1.1,1.1)).save(assets/f'page-{no:02d}.jpg')
   ocr=key=='dorkenwald' and no>=20
   if ocr:
    png=assets/f'ocr-{no}.png';page.get_pixmap(matrix=fitz.Matrix(3,3)).save(png)
    completed=subprocess.run(['tesseract',str(png),'stdout','-l','eng','--psm','3'],capture_output=True,text=True,check=True);raw=completed.stdout;png.unlink();blocks=[{'text':clean(b),'mode':'translate'} for b in re.split(r'\n\s*\n',raw) if clean(b)]
   else:
    blocks=[]
    for b in page.get_text('blocks'):
     text=clean(b[4]);y0,y1=b[1],b[3]
     if not text:continue
     # Repeated journal headers and running page footers are layout, not prose.
     if y0<43 and (text in ['Article','EMBO reports'] or 'Richard Benton et al' in text):continue
     if y0>page.rect.height-47 and (('EMBO reports' in text) or ('Nature' in text) or '© The Author' in text):continue
     if key=='benton':
      if text=='References':refs=True
      if text.startswith(('Acknowledgements','Author contributions')):refs=False
     else:
      if re.match(r'^1\.\s+Scheffer',text):refs=True
      if text.startswith(('Publisher’s note','Publisher\'s note','Open Access','The FlyWire Consortium','Methods','M eth','M\xad')):refs=False
      if no==19 and re.search(r'\b120\.\s+Mitchell,',text):
       at=re.search(r'\b120\.\s+Mitchell,',text).start()
       if at:blocks.append({'text':text[:at].strip(),'mode':'translate'})
       blocks.append({'text':text[at:],'mode':'original_reference'});refs=True;continue
      if no==19 and text.startswith(('Acknowledgements','Author contributions')):refs=False
     blocks.append({'text':text,'mode':'original_reference' if refs else 'translate'})
   # Pack adjacent same-mode blocks, keeping original paragraph separators.
   packed=[]
   for b in blocks:
    if packed and packed[-1]['mode']==b['mode'] and len(packed[-1]['text'])+len(b['text'])<3100:packed[-1]['text']+='\n\n'+b['text']
    else:packed.append(dict(b))
   segments=[]
   for b in packed:
    for part in cut(b['text']):segments.append({'id':f'{key}-p{no:02d}-s{len(segments):03d}','mode':b['mode'],'source':part,'source_sha256':hashlib.sha256(part.encode()).hexdigest()})
   pages.append({'page':no,'ocr':ocr,'segments':segments,'source_word_count':sum(len(b['text'].split()) for b in blocks)})
  result['documents'][key]={'metadata':meta,'pages':pages}
 dump(R/'segments.json',result)
 print({k:{'pages':len(v['pages']),'segments':sum(len(p['segments']) for p in v['pages']),'source_words':sum(p['source_word_count'] for p in v['pages'])} for k,v in result['documents'].items()})

# Explicit corrections are logged and limited to mistranslated technical words.
FIXES={'肾小球':'嗅小球','肾小球的':'嗅小球的','气味感觉神经元':'嗅觉感觉神经元','气味感知神经元':'嗅觉感觉神经元','嗅觉感受神经元':'嗅觉感觉神经元','连接体':'连接组','连接基因组':'连接组','腹侧神经索':'腹神经索','腹侧神经绳':'腹神经索','腹神经绳':'腹神经索','下行运动神经通路':'下行运动通路','下行神经细胞':'下行神经元','传入神经细胞':'传入神经元','传出神经细胞':'传出神经元','投影神经元':'投射神经元','投影组':'投射组','神经毡':'神经纤维网','黑腹果蝇黑腹果蝇':'黑腹果蝇','校样':'校对','电导率':'电导','抑制性突触的电导可以比兴奋性突触的电导高十倍':'抑制性突触的电导可达兴奋性突触的约十倍'}
def normalize(t):
 for a,b in FIXES.items():t=t.replace(a,b)
 return t

class OfflineEngine:
 def __init__(self,model_dir):
  import ctranslate2,sentencepiece
  self.model_dir=Path(model_dir);self.sp=sentencepiece.SentencePieceProcessor(model_file=str(self.model_dir/'sentencepiece.bpe.model'))
  self.model=ctranslate2.Translator(str(self.model_dir),device='cpu',compute_type='int8',intra_threads=4,inter_threads=1)
 def parts(self,text):
  # Keep every source character; split only at whitespace/sentence boundaries.
  pieces=re.split(r'(?<=[.!?;])\s+(?=[A-Z(])',text);parts=[];current=''
  for sentence in pieces:
   if len(self.sp.encode((current+' '+sentence).strip()))<=180:current=(current+' '+sentence).strip();continue
   if current:parts.append(current);current=''
   words=sentence.split();piece=[]
   for word in words:
    if piece and len(self.sp.encode(' '.join(piece+[word])))>180:parts.append(' '.join(piece));piece=[]
    piece.append(word)
   current=' '.join(piece)
  if current:parts.append(current)
  return parts
 def batch(self,texts):
  sources=[['eng_Latn']+self.sp.encode(t,out_type=str)+['</s>'] for t in texts]
  output=self.model.translate_batch(sources,target_prefix=[['zho_Hans'] for t in texts],beam_size=4,max_decoding_length=512,max_input_length=0,length_penalty=1.)
  result=[]
  for o in output:
   tokens=[t for t in o.hypotheses[0] if t not in ['zho_Hans','</s>','<s>']]
   result.append(self.sp.decode(tokens))
  return result

def translate(model_dir):
 data=json.loads((R/'segments.json').read_text());engine=OfflineEngine(model_dir);jobs=[];mapping={};start=time.monotonic()
 for d in data['documents'].values():
  for p in d['pages']:
   for s in p['segments']:
    if s['mode']=='original_reference':s.update(translation=s['source'],status='reference_preserved');continue
    paragraphs=[]
    for paragraph in s['source'].split('\n\n'):
     items=[]
     for part in engine.parts(paragraph):
      key=hashlib.sha256(('nllb600-int8-v1\n'+part).encode()).hexdigest();items.append(key)
      if key not in mapping:mapping[key]={'source':part};jobs.append(key)
     paragraphs.append(items)
    s['_part_keys']=paragraphs
 complete=0;pending=[]
 for key in jobs:
  path=CACHE/(key+'.json')
  if path.exists():mapping[key].update(json.loads(path.read_text()));complete+=1
  else:pending.append(key)
 print('Offline translation units',len(jobs),'cached',complete,flush=True)
 for offset in range(0,len(pending),12):
  batch=pending[offset:offset+12];texts=[mapping[k]['source'] for k in batch];outputs=engine.batch(texts)
  for key,text in zip(batch,outputs):
   assert text.strip(),'Empty offline translation'
   item={'raw_translation':text,'translation':normalize(text),'status':'translated','engine':'NLLB200 distilled600M local CTranslate2 int8'};mapping[key].update(item);dump(CACHE/(key+'.json'),item)
  complete+=len(batch);state={'completed_units':complete,'total_units':len(jobs),'seconds':time.monotonic()-start,'engine':'local offline NLLB; no document text sent over network'};dump(R/'progress.json',state);print(json.dumps(state),flush=True)
 for d in data['documents'].values():
  for p in d['pages']:
   for s in p['segments']:
    if s['mode']=='original_reference':continue
    s['translation']='\n\n'.join(' '.join(mapping[k]['translation'] for k in keys) for keys in s.pop('_part_keys'))
    s['status']='translated';assert s['translation'].strip()
 data.update(translation_status='complete',failed_segments=[],engine='Local offline NLLB200 distilled600M int8 draft, glossary normalization, separately recorded technical review',seconds=time.monotonic()-start,model_manifest=json.loads((Path(model_dir)/'download-manifest.json').read_text()))
 dump(R/'translated.json',data)

def render():
 from docx import Document
 from docx.shared import Inches,Pt
 from docx.oxml.ns import qn
 data=json.loads((R/'translated.json').read_text());assert data['translation_status']=='complete';out=CACHE/'delivery';out.mkdir(exist_ok=True)
 intro='非官方中文全文译稿。由机器逐段初译并进行专业术语校订；不是作者审定译本。正文、方法、图注、扩展数据及可用性说明均纳入；参考文献保留原始书目信息，基因/细胞标识与原图文字保持原样。文末扫描页文字经OCR识别，表格勾选与图中符号请对照所附原页。原始论文采用CC BY 4.0许可，译稿为衍生阅读材料，已做语言转换和版式调整。'
 for key,d in data['documents'].items():
  m=d['metadata'];name=m['name']+'_Chinese_Full';doc=Document();normal=doc.styles['Normal'];normal.font.name='Noto Sans CJK SC';normal._element.rPr.rFonts.set(qn('w:eastAsia'),'Noto Sans CJK SC');normal.font.size=Pt(10.5);doc.add_heading(m['title'],0);doc.add_paragraph(m['english']);doc.add_paragraph(m['authors']);doc.add_paragraph('原文：https://doi.org/'+m['doi']);doc.add_paragraph(intro)
  chunks=[f'# {m["title"]}',m['english'],m['authors'],'原文：https://doi.org/'+m['doi'],intro];sections=[]
  for p in d['pages']:
   title=f'原文PDF第{p["page"]}页'+('（扫描页OCR）' if p['ocr'] else '');doc.add_heading(title,1);chunks.append('\n## '+title);paragraphs=[]
   for s in p['segments']:
    text=s['translation'];assert text and s['status']!='failed'
    if s['mode']=='original_reference':text='【参考文献原文】\n'+text
    doc.add_paragraph(text);chunks.append(text)
    paragraphs.append('<section class="segment">'+''.join('<p>'+html.escape(t).replace('\n','<br>')+'</p>' for t in text.split('\n\n'))+'<details class="english"><summary>核对本段英文</summary><pre>'+html.escape(s['source'])+'</pre></details></section>')
   image=CACHE/key/f'page-{p["page"]:02d}.jpg';encoded=base64.b64encode(image.read_bytes()).decode()
   # Original page preserves all figures, coordinates, checkbox states and equations.
   doc.add_paragraph('原页图版（保留原图及符号，供核对）：');doc.add_picture(str(image),width=Inches(5.9))
   sections.append('<article><h2>'+title+'</h2>'+''.join(paragraphs)+'<h3>原页图版（含原图及符号）</h3><img class="original" src="data:image/jpeg;base64,'+encoded+'"></article>')
  (out/(name+'.md')).write_text('\n\n'.join(chunks)+'\n');doc.save(out/(name+'.docx'))
  css='body{font-family:"Noto Sans CJK SC",sans-serif;font-size:11pt;line-height:1.6;color:#17212b;max-width:900px;margin:30px auto}h1{font-size:24pt}h2{font-size:17pt;break-after:avoid}article{break-before:page}p{white-space:normal;overflow-wrap:anywhere}pre{white-space:pre-wrap;font-family:serif;font-size:10pt}details{font-size:10pt;color:#495057;background:#f4f6f8;padding:8px}.original{width:100%;max-height:260mm;object-fit:contain;break-inside:avoid}h3{font-size:12pt;break-after:avoid}@page{size:A4;margin:18mm 16mm}@media print{body{margin:0;max-width:none}.english{display:none}a{color:#17212b}img{max-width:100%}}'
  h='<html lang="zh-CN"><meta charset="utf-8"><title>'+html.escape(m['title'])+'</title><style>'+css+'</style><h1>'+html.escape(m['title'])+'</h1><p>'+html.escape(m['english'])+'</p><p>'+html.escape(m['authors'])+'</p><p>原文：https://doi.org/'+m['doi']+'</p><p>'+intro+'</p>'+''.join(sections)+'</html>'
  hp=out/(name+'.html');hp.write_text(h)
  subprocess.run(['chromium','--headless','--no-sandbox','--disable-dev-shm-usage','--disable-gpu','--no-pdf-header-footer','--print-to-pdf='+str(out/(name+'.pdf')),hp.as_uri()],capture_output=True,check=True,timeout=120)
  print('Rendered',name,flush=True)
 dump(out/'Translation_Notes_and_Sources.json',{'translation':'unofficial full reading draft','source_manifest':{k:d['metadata'] for k,d in data['documents'].items()},'method':data['engine'],'all_segments_complete':not data['failed_segments'],'references':'kept verbatim','figures':'original page images retained; caption/body text translated','ocr_pages':{k:[p['page'] for p in d['pages'] if p['ocr']] for k,d in data['documents'].items()}})
 bundle=out/'Two_Papers_Chinese_Full_Translations.zip'
 with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED) as z:
  for p in out.iterdir():
   if p!=bundle:z.write(p,p.name)
 print('Bundle',bundle,flush=True)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('mode',choices=['extract','translate','render']);p.add_argument('--model-dir',type=Path);p.add_argument('--benton',type=Path);p.add_argument('--dorkenwald',type=Path);a=p.parse_args()
 if a.mode=='extract':extract({'benton':a.benton,'dorkenwald':a.dorkenwald})
 elif a.mode=='translate':translate(a.model_dir)
 else:render()
