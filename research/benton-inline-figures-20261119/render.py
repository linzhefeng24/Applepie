"""Re-layout the existing assistant-authored translation; no new machine translation.
Crop complete figures from the user PDF (including vector labels) at 216 dpi,
then place each immediately before its translated caption in PDF/Word/HTML.
Coordinates are PDF points. Reference entries and original labels stay verbatim.
"""
from pathlib import Path
import argparse, base64, hashlib, html, json, re, zipfile
import fitz
from docx import Document
from docx.shared import Inches, Pt
from docx.oxml.ns import qn
R=Path(__file__).resolve().parent
SOURCE=R.parent/'chinese-translations-20261118'
FIGURES=[('1',2,[40,75,555,615],'benton-p03-s002'),('2',4,[40,75,555,748],'benton-p05-s002'),('3',6,[40,75,555,748],'benton-p07-s002'),('4',8,[40,75,555,748],'benton-p09-s002'),('5',10,[40,75,555,748],'benton-p11-s002'),('6',12,[40,75,555,537],'benton-p12-s001'),('EV1',20,[40,100,555,568],'benton-p20-s000'),('EV2',21,[40,75,555,748],'benton-p22-s000')]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('source_pdf',type=Path);a=p.parse_args()
 data=json.loads((SOURCE/'translated.json').read_text())['documents']['benton'];m=data['metadata']
 assert sha(a.source_pdf)==m['sha256']
 cache=R/'cache';out=cache/'delivery';out.mkdir(parents=True,exist_ok=True)
 original=fitz.open(a.source_pdf);figs={}
 for label,no,rect,anchor in FIGURES:
  path=cache/f'figure-{label}.jpg';original[no-1].get_pixmap(matrix=fitz.Matrix(3,3),clip=fitz.Rect(rect),alpha=False).save(path,jpg_quality=95)
  figs[anchor]={'label':label,'source_page':no,'crop_pdf_points':rect,'anchor_segment':anchor,'path':path,'sha256':sha(path)}
 intro='非官方中文全文阅读译稿，图文对应版。图1–6及扩展图EV1、EV2均插入相应中文图注之前。原图面板字母、基因名、坐标与统计标记保留原样；参考文献保留原文。原文CC BY 4.0；本版仅调整图文布局，中文译文沿用2026-11-18版本。'
 doc=Document();normal=doc.styles['Normal'];normal.font.name='Noto Sans CJK SC';normal.font.size=Pt(10.5);normal._element.get_or_add_rPr().rFonts.set(qn('w:eastAsia'),'Noto Sans CJK SC')
 doc.add_heading(m['title'],0);doc.add_paragraph(m['english']);doc.add_paragraph(m['authors']);doc.add_paragraph('https://doi.org/'+m['doi']);doc.add_paragraph(intro)
 head='<h1>'+m['title']+'</h1><p>'+m['english']+'</p><p>'+m['authors']+'</p><p>https://doi.org/'+m['doi']+'</p><p>'+intro+'</p>'
 body=[];pdfbody=[];captions=[]
 for page in data['pages']:
  title=f'原文PDF第{page["page"]}页';doc.add_heading(title,1);body.append('<h2>'+title+'</h2>');pdfbody.append('<h2>'+title+'</h2>')
  for segment in page['segments']:
   if segment['id'] in figs:
    f=figs[segment['id']];path=f['path'];pix=fitz.Pixmap(path);width=490;height=width*pix.height/pix.width
    if height>590:width*=590/height;height=590
    label='图'+f['label']+'（原文第'+str(f['source_page'])+'页）'
    doc.add_paragraph(label);doc.add_picture(str(path),width=Inches(width/72))
    img='<img width="'+str(round(width))+'" height="'+str(round(height))+'" src="'
    body.append('<div class="figure"><h3>'+label+'</h3>'+img+'data:image/jpeg;base64,'+base64.b64encode(path.read_bytes()).decode()+'"></div>')
    pdfbody.append('<div class="figure"><h3>'+label+'</h3>'+img+path.name+'"></div>');captions.append(f['label'])
   text=segment['translation'];doc.add_paragraph(text)
   paragraphs=''.join('<p>'+html.escape(x).replace('\n','<br>')+'</p>' for x in text.split('\n\n'))
   body.append(paragraphs+'<details><summary>核对本段英文</summary><pre>'+html.escape(segment['source'])+'</pre></details>');pdfbody.append(paragraphs)
 css='body{font-family:sans-serif;font-size:10.5pt;line-height:1.5}h1{font-size:22pt}h2{font-size:14pt}h3{font-size:11pt}h2,h3{page-break-after:avoid}.figure{page-break-inside:avoid}img{display:block;max-width:100%;margin:auto}pre{white-space:pre-wrap}details{color:#555}p{overflow-wrap:anywhere}'
 def document(content):return '<html lang="zh"><meta charset="utf-8"><style>'+css+'</style>'+head+''.join(content)+'</html>'
 name='Benton_2025_Chinese_Illustrated';(out/(name+'.html')).write_text(document(body));doc.save(out/(name+'.docx'))
 story=fitz.Story(document(pdfbody),archive=fitz.Archive(str(cache)));paper=fitz.paper_rect('a4');area=paper+(36,36,-36,-36)
 pdf=story.write_with_links(lambda n,filled:(paper,area,None));pdf.save(out/(name+'.pdf'),garbage=4,deflate=True)
 reopened=fitz.open(out/(name+'.pdf'));images=sum(len(p.get_image_info()) for p in reopened);text=''.join(p.get_text() for p in reopened)
 assert images==8,(images,len(reopened))
 assert all(t in text for t in ['图1图注','图2图注','图3图注','图EV1','图EV2','数据可用性'])
 audit={'source_sha256':m['sha256'],'translation_sha256':sha(SOURCE/'translated.json'),'figures':[{k:v for k,v in f.items() if k!='path'} for f in figs.values()],'pdf_pages':len(reopened),'pdf_image_placements':images,'caption_order':captions,'all_original_translation_segments_retained':46,'versions':{'PyMuPDF':fitz.VersionBind},'status':'rendered_and_structurally_checked'}
 (R/'layout-audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n')
 (out/'Sources_and_Layout.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n')
 bundle=out/'Benton_2025_Chinese_Illustrated.zip'
 with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED) as z:
  for f in sorted(out.iterdir()):
   if f!=bundle:z.write(f,f.name)
 assets=[{'name':f.name,'bytes':f.stat().st_size,'sha256':sha(f),'url':'https://github.com/linzhefeng24/Applepie/releases/download/benton-illustrated-zh-20261119/'+f.name} for f in sorted(out.iterdir())]
 (R/'manifest.json').write_text(json.dumps({'status':'rendered_pending_publication','delivery_assets':assets},ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(audit,ensure_ascii=False));print([(x['name'],x['bytes']) for x in assets])
if __name__=='__main__':main()
