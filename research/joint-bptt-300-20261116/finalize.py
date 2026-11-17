"""After300 actual updates, evaluate manual/best/final banks on identical AB physics.
Uses hard neural forward and raw native controls; no training or rescue forces.
Saves full physical states and130-channel inputs alongside comparison video.
"""
from pathlib import Path
import hashlib,json,os,subprocess,zipfile,sys,base64
os.environ.setdefault('MUJOCO_GL','egl')
import numpy as np
import jax
import mujoco
from PIL import Image,ImageDraw
import imageio_ffmpeg
from training_context import JointContext
from reference_panel import load as load_reference_panel
R=Path(__file__).resolve().parent;OUT=R/'cache/train';D=R/'cache/final';D.mkdir(parents=True,exist_ok=True)
report=json.loads((OUT/'chunk-report.json').read_text());assert report['completed_updates']>=300
ctx=JointContext();body=ctx.native_physics;native=ctx.physics.native;p=ctx.physics
with np.load(OUT/'optimizer.npz',allow_pickle=False) as z:final=z['raw']
with np.load(OUT/'best-parameters.npz',allow_pickle=False) as z:best=z['raw'];best_epoch=int(z['completed_updates'])
forward=jax.jit(ctx.neural_u);panels={};metrics={}
banks={'Manual':np.asarray(ctx.reference),'Best':best,'Epoch300':final}
for label,raw in banks.items():
 u=forward(raw);u.block_until_ready();physical=np.asarray(u[p.clock_indices][:,ctx.order]);state=tuple(np.asarray(x) for x in p.initial);poses=[];states=[];contacts=[]
 for k,row in enumerate(physical):
  result=body.native_step_numpy(state,k,row);state=result[:4];poses.append(state[0]);contacts.append(result[4])
  full=np.empty(mujoco.mj_stateSize(body.m,mujoco.mjtState.mjSTATE_FULLPHYSICS));mujoco.mj_getState(body.m,body.data,full,mujoco.mjtState.mjSTATE_FULLPHYSICS);states.append(full)
 poses=np.asarray(poses);states=np.asarray(states);error=poses[:,np.asarray(p.joint_ids)]-np.asarray(p.target)
 metrics[label]={'joint_mse_rad2':float(np.mean(error**2)),'joint_rmse_deg':float(np.sqrt(np.mean(error**2))*180/np.pi),'max_parameter_fractional_change_from_manual':float(np.max(abs(ctx.fractional_shift(raw)))),'max_contacts':np.max(contacts,axis=0).tolist(),'all_states_finite':bool(np.isfinite(states).all()),'parameter_update':0 if label=='Manual' else best_epoch if label=='Best' else 300}
 np.savez_compressed(D/f'{label}.npz',raw=raw,physical_u=physical,neural_u=np.asarray(u),full_state=states,qpos=poses,target_joint_angles=np.asarray(p.target),joint_qpos_indices=np.asarray(p.joint_ids),dt_s=p.dt)
 panels[label]=states[49::50]
 print(label,json.dumps(metrics[label]),flush=True)
# Archived direct-A input is a separate mechanical comparison, never copied
# into any of the neural muscle controls above.
reference=native.replay_ab('A');panels['DirectAB_A']=reference['full_state'][24::25];metrics['DirectAB_A']=reference['metrics']
panels['Reference_kinematic'],reference_details=load_reference_panel(native,p.target)
labels=['Reference_kinematic','DirectAB_A','Manual','Best','Epoch300'];video=D/'Joint300_Comparison.mp4';writer=imageio_ffmpeg.write_frames(str(video),(1920,1024),fps=20,codec='libx264',quality=7);writer.send(None)
try:
 for k in range(min(len(panels[x]) for x in labels)):
  canvas=Image.new('RGB',(1920,1024),'white');draw=ImageDraw.Draw(canvas)
  for i,label in enumerate(labels):
   image=Image.fromarray(native._image(panels[label][k])).convert('RGB').resize((640,480));x=(i%3)*640;y=(i//3)*512;canvas.paste(image,(x,y+32));draw.text((x+10,y+3),label,fill='black')
   if i==0:draw.text((x+10,y+17),'Prescribed reference; original root motion NOT in loss',fill='black')
  writer.send(np.asarray(canvas))
finally:writer.close()
revision=subprocess.run(['git','rev-parse','HEAD'],text=True,capture_output=True)
result={'completed_main_updates':300,'coefficient_trials':json.loads((OUT/'coefficient-trials.json').read_text()),'selected_coefficient':report['selected_coefficient'],'best_update':best_epoch,'metrics':metrics,'anchor':json.loads((R/'manual-anchor.json').read_text()),'training_source_revision':report['source_revision'],'evaluation_code_revision':revision.stdout.strip() if revision.returncode==0 else 'offline-bundle','limitations':json.loads((R/'validation-report.json').read_text())['limitation'],'physical_body':'free native AB body, same initial state and11 auxiliary schedules, no rescue forces','video':'four panels at10x slow motion; all0.4s physical rollouts are displayed without resets'}
result['reference_panel']=reference_details
result['video']='five panels including exact-target kinematic reference, nativeA/manual/best/epoch300;10x slow of full0.4s'
(D/'evaluation.json').write_text(json.dumps(result,indent=2)+'\n')
if '--local' in sys.argv:
 print(json.dumps(result,indent=2));sys.exit(0)
archive=D/'Joint300_Reproduction.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
 for file in D.iterdir():
  if file!=archive and file.suffix in ['.npz','.json','.mp4']:z.write(file,file.name)
 for file in [OUT/'optimizer.npz',OUT/'best-parameters.npz',OUT/'history.json',OUT/'run-identity.json',R/'config.json',R/'neural-config.json',R/'manual-anchor.json',R/'validation-report.json']:z.write(file,'training/'+file.name)
 root=R.parents[1]
 runtime=[p for p in (root/'research/single-model-delivery-20261115/runtime').rglob('*') if p.is_file() and '__pycache__' not in p.parts]
 runtime+=[p for p in R.iterdir() if p.is_file() and p.suffix in ['.py','.json','.md','.txt']]
 runtime+=[p for p in (R/'reference').iterdir() if p.is_file()]
 runtime+=[p for p in (root/'research/physics-bptt-20261116/source').iterdir() if p.is_file()]
 runtime +=[root/name for name in ['research/single-model-delivery-20261115/build/UnifiedFlyModel/01_model/model.yaml','research/conductance-rebuild-20261114/grouped_parameters.py','research/surrogate-bptt-20261115/input-identity.json','research/assets/flymimic-legacy-AB-twofile.zip']]
 runtime +=[p for p in OUT.iterdir() if p.is_file() and p.suffix in ['.json','.npz']]
 for file in runtime:z.write(file,file.relative_to(root))
 z.writestr('REPLAY.txt','From this directory create a Python3.12 virtual environment. Install research/joint-bptt-300-20261116/requirements.txt, run patch_mjx.py in that folder, then MUJOCO_GL=egl python research/joint-bptt-300-20261116/finalize.py --local. No GitHub token or network upload is used for local replay. Linux EGL libraries are needed for rendering. Results go into research/joint-bptt-300-20261116/cache/final/.')
tag='joint-trajectory-bptt-300-20261116';repo=os.environ['GITHUB_REPOSITORY']
subprocess.run(['gh','release','upload',tag,str(video),str(archive),str(D/'evaluation.json'),'--repo',repo,'--clobber'],check=True)
manifest={'source_revision':report['source_revision'],'evaluation_code_revision':result['evaluation_code_revision'],'completed_main_updates':300,'assets':[{'name':f.name,'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'bytes':f.stat().st_size,'url':f'https://github.com/{repo}/releases/download/{tag}/{f.name}'} for f in [video,archive,D/'evaluation.json']]}
(D/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
subprocess.run(['gh','release','upload',tag,str(D/'manifest.json'),'--repo',repo,'--clobber'],check=True)
# Verify the uploaded bytes before making the completed result public.
verify=D/'verify';verify.mkdir(exist_ok=True)
for asset in manifest['assets']:
 subprocess.run(['gh','release','download',tag,'--repo',repo,'--pattern',asset['name'],'--dir',str(verify),'--clobber'],check=True)
 assert hashlib.sha256((verify/asset['name']).read_bytes()).hexdigest()==asset['sha256']
subprocess.run(['gh','release','edit',tag,'--repo',repo,'--draft=false'],check=True)
for file in [D/'evaluation.json',D/'manifest.json']:
 destination='research/joint-bptt-300-20261116/final-'+file.name;raw=file.read_bytes()
 for attempt in range(4):
  old=subprocess.run(['gh','api',f'repos/{repo}/contents/{destination}?ref=main'],text=True,capture_output=True)
  payload={'message':'Save completed300 joint BPTT '+file.name,'branch':'main','content':base64.b64encode(raw).decode()}
  if old.returncode==0:payload['sha']=json.loads(old.stdout)['sha']
  elif '404' not in old.stderr:raise RuntimeError(old.stderr)
  request=D/'commit-payload.json';request.write_text(json.dumps(payload))
  answer=subprocess.run(['gh','api','--method','PUT',f'repos/{repo}/contents/{destination}','--input',str(request)],capture_output=True,text=True)
  if answer.returncode==0:break
  if attempt==3:raise RuntimeError(answer.stderr)
 fresh=json.loads(subprocess.check_output(['gh','api',f'repos/{repo}/contents/{destination}?ref=main'],text=True));assert base64.b64decode(fresh['content'])==raw
print(json.dumps(manifest,indent=2))
