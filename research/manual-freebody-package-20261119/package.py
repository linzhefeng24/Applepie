"""Package the complete manual model and new free-body videos; verify actual ZIP.
The outer flat transport archive is only for the existing SHA256 Release publisher.
"""
from pathlib import Path
import hashlib,json,zipfile,shutil,subprocess
R=Path(__file__).resolve().parent;P=R/'cache/Manual_FreeBody';D=R/'cache/delivery';D.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
report=json.loads((P/'04_results/report.json').read_text());assert not report['fixed_root'] and report['hand_parameters_included']
paths=[p for p in P.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc' and p.name!='FILE_MANIFEST.json']
checks={str(p.relative_to(P)):{'sha256':sha(p),'bytes':p.stat().st_size} for p in paths}
(P/'FILE_MANIFEST.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2)+'\n')
bundle=D/'Manual_R2_FreeBody_Complete.zip'
with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED) as z:
 for p in paths+[P/'FILE_MANIFEST.json']:z.write(p,'Manual_FreeBody/'+str(p.relative_to(P)))
with zipfile.ZipFile(bundle) as z:
 assert z.testzip() is None
 for n,info in checks.items():assert hashlib.sha256(z.read('Manual_FreeBody/'+n)).hexdigest()==info['sha256']
 assert hashlib.sha256(z.read('Manual_FreeBody/01_model/model.yaml')).hexdigest()==report['manual_model_sha256']
 assert 'Manual_FreeBody/04_results/data/manual-resolved-parameters.npz' in z.namelist()
assert not any('BPTT' in n or 'optimizer' in n or 'checkpoint' in n for n in checks)
for src,name in [('01_body_muscles.mp4','Manual_R2_FreeBody.mp4'),('02_neural_chain_3d.mp4','Manual_R2_Neural_Chain.mp4'),('03_synchronized.mp4','Manual_R2_Synchronized.mp4')]:
 p=P/'04_results/videos'/src;meta=json.loads(subprocess.check_output(['ffprobe','-v','quiet','-count_frames','-select_streams','v:0','-show_entries','stream=nb_read_frames,width,height,duration','-of','json',str(p)],text=True));assert int(meta['streams'][0]['nb_read_frames'])==80;shutil.copyfile(p,D/name)
shutil.copyfile(P/'04_results/report.json',D/'verification.json')
assets=[{'name':p.name,'bytes':p.stat().st_size,'sha256':sha(p),'url':'https://github.com/linzhefeng24/Applepie/releases/download/manual-r2-freebody-20261119/'+p.name} for p in sorted(D.iterdir()) if p.name!='Manual_FreeBody_Delivery_Transport.zip']
with zipfile.ZipFile(D/'Manual_FreeBody_Delivery_Transport.zip','w',zipfile.ZIP_STORED) as z:
 for p in assets:z.write(D/p['name'],p['name'])
audit={'status':'local standalone archive hash checked; all three videos decoded80frames','file_count':len(checks)+1,'manual_model_in_zip':True,'manual_cells_in_zip':True,'root_free':True,'no_BPTT_checkpoint_in_zip':True,'manual_model_sha256':report['manual_model_sha256'],'assets':assets}
(R/'package-verification.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n');(R/'manifest.json').write_text(json.dumps({'status':'prepared_for_public_release','delivery_assets':assets},indent=2)+'\n');print([(x['name'],x['bytes']) for x in assets])
