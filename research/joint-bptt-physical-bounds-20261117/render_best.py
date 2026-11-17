"""Render an immutable intermediate checkpoint on exact native free-body AB.
No300-update claim and no training state writes. The minimum joint-MSE parameter bank produces the labelled best footage.
"""
from pathlib import Path
import argparse,hashlib,json,os,sys,zipfile,io,subprocess,time
os.environ.setdefault('MUJOCO_GL','egl')
import numpy as np
import jax
jax.config.update('jax_enable_x64',True)
import mujoco
from PIL import Image,ImageDraw
import imageio_ffmpeg
from training_context import JointContext
from reference_panel import load as load_reference_panel
R=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--snapshot',type=Path,required=True);p.add_argument('--archive',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();meta=json.loads(a.snapshot.read_text());assert hashlib.sha256(a.archive.read_bytes()).hexdigest()==meta['sha256'] and a.archive.stat().st_size==meta['bytes'];a.out.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(a.archive) as z:
 with np.load(io.BytesIO(z.read('best-parameters.npz')),allow_pickle=False) as bank:
  raw=bank['raw'];epoch=int(bank['completed_updates']);expected_mse=float(bank['score'])
 identity=json.loads(z.read('run-identity.json'))
assert epoch<=meta['completed_updates'];ctx=JointContext();pbody=ctx.physics;body=ctx.native_physics;native=pbody.native
assert identity['manual_anchor_model_sha256']==ctx.cfg['anchor_model_sha256']
for name,key in [('config.json','config_sha256'),('neural-config.json','neural_config_sha256'),('validation-report.json','physics_validation_sha256')]:assert hashlib.sha256((R/name).read_bytes()).hexdigest()==identity[key],name
forward=jax.jit(ctx.neural_u);labels=['Reference_kinematic','DirectAB_A','Manual',f'BestUpdate{epoch}'];panels={};metrics={};dt=pbody.dt
panels['Reference_kinematic'],reference_details=load_reference_panel(native,pbody.target)
for label,factors in [('Manual',ctx.reference),(f'BestUpdate{epoch}',raw)]:
 start=time.monotonic();u=forward(factors);u.block_until_ready();control=np.asarray(u[pbody.clock_indices][:,ctx.order]);state=tuple(np.asarray(x) for x in pbody.initial);poses=[];states=[]
 for k,row in enumerate(control):
  result=body.native_step_numpy(state,k,row);state=result[:4];poses.append(state[0])
  full=np.empty(mujoco.mj_stateSize(body.m,mujoco.mjtState.mjSTATE_FULLPHYSICS));mujoco.mj_getState(body.m,body.data,full,mujoco.mjtState.mjSTATE_FULLPHYSICS);states.append(full)
 poses=np.asarray(poses);states=np.asarray(states);error=poses[:,np.asarray(pbody.joint_ids)]-np.asarray(pbody.target)
 w=mujoco.MjData(body.m);bid=mujoco.mj_name2id(body.m,mujoco.mjtObj.mjOBJ_BODY,'walker/thorax');up=[]
 for pose in poses[::10]:w.qpos[:]=pose;mujoco.mj_kinematics(body.m,w);up.append(float(w.xmat[bid].reshape(3,3)[2,2]))
 metrics[label]={'actual_parameter_update':0 if label=='Manual' else epoch,'joint_mse_rad2':float(np.mean(error**2)),'joint_rmse_deg':float(np.sqrt(np.mean(error**2))*180/np.pi),'root_displacement_mm':((poses[-1,:3]-np.asarray(pbody.initial[0])[:3])*native.config['units']['native_length_to_mm']).tolist(),'min_body_up_z_sampled_1ms':min(up),'max_parameter_fractional_change_from_manual':float(np.max(abs(ctx.fractional_shift(factors)))),'all_states_finite':bool(np.isfinite(states).all()),'seconds':time.monotonic()-start}
 np.savez_compressed(a.out/(label+'.npz'),raw=np.asarray(factors),physical_u=control,neural_u=np.asarray(u),full_state=states,qpos=poses,target_joint_angles=np.asarray(pbody.target),joint_qpos_indices=np.asarray(pbody.joint_ids),dt_s=dt)
 panels[label]=states[49::50];print(label,json.dumps(metrics[label]),flush=True)
assert np.isclose(metrics[f'BestUpdate{epoch}']['joint_mse_rad2'],expected_mse,rtol=1e-8,atol=1e-10), 'Best replay mismatch'
reference=native.replay_ab('A');panels['DirectAB_A']=reference['full_state'][24::25];metrics['DirectAB_A']=reference['metrics']
single=a.out/f'Joint_BestUpdate{epoch}.mp4';comparison=a.out/f'Joint_BestUpdate{epoch}_Comparison.mp4';writers=[imageio_ffmpeg.write_frames(str(single),(640,512),fps=20,codec='libx264',quality=7),imageio_ffmpeg.write_frames(str(comparison),(1280,1024),fps=20,codec='libx264',quality=7)]
for writer in writers:writer.send(None)
last=None
try:
 for k in range(min(len(panels[label]) for label in labels)):
  canvas=Image.new('RGB',(1280,1024),'white');draw=ImageDraw.Draw(canvas)
  for i,label in enumerate(labels):
   x=(i%2)*640;y=(i//2)*512;frame=Image.fromarray(native._image(panels[label][k])).convert('RGB').resize((640,480));canvas.paste(frame,(x,y+32));draw.text((x+10,y+3),f'{label} | t={(k+1)*.005:.3f}s | 10x slow',fill='black')
   if i==0:draw.text((x+10,y+17),'Prescribed reference; original root motion NOT in loss',fill='black')
  writers[0].send(np.asarray(canvas.crop((640,512,1280,1024))));writers[1].send(np.asarray(canvas));last=canvas
finally:
 for writer in writers:writer.close()
if last:last.save(a.out/'comparison-preview.jpg')
revision=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();report={'completed_main_updates':epoch,'selected_bank':'minimum evaluated joint MSE; best-parameters.npz; not latest raw','source_checkpoint':meta,'training_source_revision':identity['source_revision'],'render_code_revision':revision,'manual_anchor_model_sha256':ctx.cfg['anchor_model_sha256'],'body_archive_sha256':ctx.cfg['body_archive_sha256'],'metrics':metrics,'physical_duration_s':.4,'physical_dt_s':dt,'physical_steps':4000,'neural_ms':1400,'body':'free body with original floor/contact/NoSlip/fluid and all11 original auxiliary schedules; no extra forces or state resets','video':'80 frames at20fps;10x slow motion of the complete0.4s rollout','validation_scope':'New hard neural forward and native physical replay; not evidence that all brain.json phenomena are satisfied','versions':{'jax':jax.__version__,'numpy':np.__version__,'mujoco':mujoco.__version__}}
report['reference_panel']=reference_details
(a.out/'evaluation.json').write_text(json.dumps(report,indent=2)+'\n')
bundle=a.out/f'Joint_BestUpdate{epoch}_Replay.zip'
with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED) as z:
 for path in a.out.iterdir():
  if path!=bundle and path.suffix in ['.npz','.json','.mp4','.jpg']:z.write(path,path.name)
 z.write(a.archive,'checkpoint/'+a.archive.name);z.write(a.snapshot,'checkpoint/snapshot.json');z.write(Path(__file__),'code/render_checkpoint.py')
print(json.dumps(report,indent=2))
