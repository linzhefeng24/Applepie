"""Add the EXACT training reference to the previously generated73-update replay.

The recovered reference includes full original root/head/leg poses and matches
all2001x66 training angle samples. Prescribed reference poses are displayed
kinematically; they are not a newly simulated muscle-driven result. All actual
physics panels reuse existing saved states or exact original nativeAB replay.
"""
from pathlib import Path
import argparse,hashlib,importlib.util,io,json,os,subprocess,zipfile
os.environ.setdefault('MUJOCO_GL','egl')
import numpy as np
import mujoco
from PIL import Image,ImageDraw
import imageio_ffmpeg
R=Path(__file__).resolve().parent;ROOT=R.parents[1]
p=argparse.ArgumentParser();p.add_argument('--replay',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
source_manifest=json.loads((R/'preview-73-manifest.json').read_text());source_item=next(x for x in source_manifest['assets'] if x['name']=='Joint_Epoch73_Replay.zip');assert hashlib.sha256(a.replay.read_bytes()).hexdigest()==source_item['sha256'] and a.replay.stat().st_size==source_item['bytes']
provenance=json.loads((R/'reference/provenance.json').read_text());frame_file=R/'reference/target-video-frames.npz';assert hashlib.sha256(frame_file.read_bytes()).hexdigest()==provenance['frame_asset']['sha256']
body_zip=ROOT/'research/assets/flymimic-legacy-AB-twofile.zip';assert hashlib.sha256(body_zip.read_bytes()).hexdigest()==provenance['canonical_model_archive_sha256']
directory=a.out/'native';directory.mkdir(exist_ok=True)
with zipfile.ZipFile(body_zip) as z:
 for name in ['parameters.yaml','simulation.py']:(directory/name).write_bytes(z.read(name))
spec=importlib.util.spec_from_file_location('reference_preview_native',directory/'simulation.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);native=mod.Simulation(directory/'parameters.yaml');m=native.model;initial_root=native.data.qpos[:3].copy()
with zipfile.ZipFile(a.replay) as z:
 report=json.loads(z.read('evaluation.json'));epoch=report['completed_main_updates'];assert epoch==73
 banks={}
 for name in ['Manual',f'Epoch{epoch}']:
  with np.load(io.BytesIO(z.read(name+'.npz')),allow_pickle=False) as data:banks[name]={k:data[k] for k in data.files}
with np.load(frame_file,allow_pickle=False) as z:frames={k:z[k] for k in z.files}
assert frames['qpos'].shape==(80,m.nq) and frames['qvel'].shape==(80,m.nv)
ids=np.asarray(native.config['reference']['joint_qpos_indices']);assert np.array_equal(ids,frames['joint_qpos_indices'])
training_frames=banks[f'Epoch{epoch}']['target_joint_angles'][49::50];difference=float(abs(training_frames-frames['qpos'][:,ids]).max());assert difference<1e-12
for bank in banks.values():assert np.isfinite(bank['full_state']).all() and np.isfinite(bank['physical_u']).all()
ref_states=[];d=mujoco.MjData(m)
for i,t in enumerate(frames['time_s']):
 d.time=t;d.qpos[:]=frames['qpos'][i];d.qvel[:]=frames['qvel'][i];d.act[:]=0
 state=np.empty(mujoco.mj_stateSize(m,mujoco.mjtState.mjSTATE_FULLPHYSICS));mujoco.mj_getState(m,d,state,mujoco.mjtState.mjSTATE_FULLPHYSICS);ref_states.append(state)
reference=native.replay_ab('A');panels={'Reference_kinematic':np.asarray(ref_states),'DirectAB_A':reference['full_state'][24::25],**{name:bank['full_state'][49::50] for name,bank in banks.items()}}
labels=['Reference_kinematic','DirectAB_A','Manual',f'Epoch{epoch}'];solo=a.out/'Training_Reference.mp4';comparison=a.out/f'Joint_Epoch{epoch}_WithReference.mp4';writers=[imageio_ffmpeg.write_frames(str(solo),(640,512),fps=20,codec='libx264',quality=7),imageio_ffmpeg.write_frames(str(comparison),(1280,1024),fps=20,codec='libx264',quality=7)]
for writer in writers:writer.send(None)
last=None
try:
 for k,t in enumerate(frames['time_s']):
  canvas=Image.new('RGB',(1280,1024),'white');draw=ImageDraw.Draw(canvas)
  for i,label in enumerate(labels):
   x=(i%2)*640;y=(i//2)*512;image=Image.fromarray(native._image(panels[label][k])).convert('RGB').resize((640,480));canvas.paste(image,(x,y+32));draw.text((x+10,y+3),f'{label} | t={t:.3f}s | 10x slow',fill='black')
   note='Prescribed original poses; root motion NOT in training loss' if i==0 else 'Muscle-driven native dynamics; free body and floor contact'
   draw.text((x+10,y+17),note,fill='black')
  writers[0].send(np.asarray(canvas.crop((0,0,640,512))));writers[1].send(np.asarray(canvas));last=canvas
finally:
 for writer in writers:writer.close()
if last:last.save(a.out/'reference-comparison-preview.jpg')
result={**report,'render_code_revision':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'reference_added':True,'prior_replay_source':source_item,'reference_provenance':provenance,'reference_target_frame_max_abs_error':difference,'reference_root_displacement_mm':((frames['qpos'][-1,:3]-frames['initial_qpos'][:3])*native.config['units']['native_length_to_mm']).tolist(),'reference_initial_root_diff_from_native':(frames['initial_qpos'][:3]-initial_root).tolist(),'reference_rendering':'Original full qpos/qvel prescribed, no integration and no inferred muscle activation; act=0 only for geometry rendering','training_loss_scope':'Only66 leg joint angles; displayed reference root motion is not part of the current objective','comparison_order':'top-left reference kinematics; top-right direct nativeAB; bottom-left manual neural bank; bottom-right73-update neural bank','neural_or_training_rerun':False,'video':'Same80 physical times0.005..0.400s;4s video at20fps,10x slow of half-speed reference time'}
(a.out/'evaluation.json').write_text(json.dumps(result,indent=2)+'\n');np.savez_compressed(a.out/'reference-frames.npz',**frames)
bundle=a.out/f'Joint_Epoch{epoch}_WithReference.zip'
with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED) as z:
 for file in a.out.iterdir():
  if file.is_file() and file!=bundle:z.write(file,file.name)
 z.write(Path(__file__),'code/add_reference_video.py')
print(json.dumps(result,indent=2))
