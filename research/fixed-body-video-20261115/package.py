"""Archive real fixed-body results; no free-body movie is substituted."""
from pathlib import Path
import hashlib,json,os,subprocess,zipfile
import imageio_ffmpeg
R=Path(__file__).resolve().parent
out=R/'results'
videos=sorted((out/'videos').glob('*.mp4'))
assert len(videos)==3
for p in videos:
 subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-v','error','-i',str(p),'-f','null','-'],check=True)
report=json.loads((out/'report.json').read_text())
assert report['position_max_drift_native']==0 and report['quaternion_max_drift']==0
assert report['ground_normal_force_max_native']>0
archive=out/'FixedBody_20261115.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
 for p in [out/'report.json',out/'body_state.npz',*sorted((out/'videos').glob('*')),R/'README.md',R/'render_fixed.py']:
  z.write(p,str(p.relative_to(out)) if out in p.parents else 'source/'+p.name)
 for p in (R.parent/'single-model-delivery-20261115/runtime/02_code').rglob('*.py'):
  z.write(p,'updated_02_code/'+str(p.relative_to(R.parent/'single-model-delivery-20261115/runtime/02_code')))
manifest={'file':archive.name,'bytes':archive.stat().st_size,'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),
 'code_revision':os.environ.get('GITHUB_SHA') or subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),
 'model_sha256':report['model_sha256'],'neural_input_sha256':report['neural_input_sha256'],
 'condition':report['condition'],'contains':['3 videos','state data','verification report','updated runtime code'],
 'not_included':'unchanged base model.yaml and neural_state.npz; use the original single-model package'}
(out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps(manifest,indent=2))
