"""Restore exact native A/B and change ONLY their 130 muscle control columns.
Preserves q/v/all activations, qacc warmstart, original 11 auxiliary controls,
MJCF/assets, native physics clock, free root, gravity and contact/adhesion.
Neural outputs reuse the saved full-network checkpoints, with declared clock map.
"""
from pathlib import Path
import argparse,hashlib,importlib.util,io,json,platform,shutil,subprocess,sys,zipfile
from importlib.metadata import version
import numpy as np
import mujoco
from PIL import Image,ImageDraw
import imageio_ffmpeg
R=Path(__file__).resolve().parent

def sha(b):return hashlib.sha256(b).hexdigest()
def arrays(z,name):
 with np.load(io.BytesIO(z.read(name)),allow_pickle=False) as n:return {k:n[k] for k in n.files}
def git_revision():
 try:return subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True,stderr=subprocess.DEVNULL).strip()
 except subprocess.CalledProcessError:return 'standalone; see packaged source provenance'

def integrate(sim,controls):
 archive=sim.load_ab('A');sim.reset('A');initial=archive['initial_state'];warm=archive['initial_warmstart'];states=[];times=[]
 assert np.array_equal(sim.data.qvel,initial[1+sim.model.nq:1+sim.model.nq+sim.model.nv])
 assert np.array_equal(sim.data.act,initial[1+sim.model.nq+sim.model.nv:])
 assert np.array_equal(sim.data.qacc_warmstart,warm)
 for k,u in enumerate(controls):
  sim.data.ctrl[:]=u;mujoco.mj_step(sim.model,sim.data)
  assert not sim.data.qfrc_applied.any() and not sim.data.xfrc_applied.any()
  assert abs(sim.data.time-(initial[0]+(k+1)*sim.model.opt.timestep))<1e-9, 'Simulator clock reset'
  if (k+1)%archive['sample_stride']==0:
   st=np.empty(mujoco.mj_stateSize(sim.model,mujoco.mjtState.mjSTATE_FULLPHYSICS));mujoco.mj_getState(sim.model,sim.data,st,mujoco.mjtState.mjSTATE_FULLPHYSICS);states.append(st);times.append(sim.data.time)
 states=np.asarray(states);assert np.isfinite(states).all();assert np.diff(times).min()>0
 q=states[:,1:1+sim.model.nq];thorax=sim.model.body('walker/thorax').id;work=mujoco.MjData(sim.model);up=[]
 for pose in q:
  work.qpos[:]=pose;mujoco.mj_kinematics(sim.model,work);up.append(work.xmat[thorax].reshape(3,3)[2,2])
 return dict(full_state=states,time_s=np.asarray(times),controls_all_141=controls,initial_state=initial,initial_warmstart=warm,body_up_z=np.asarray(up)),dict(duration_s=float(times[-1]),min_body_up_z=float(min(up)),root_displacement_mm=((q[-1,:3]-initial[1:4])*sim.config['units']['native_length_to_mm']).tolist(),finite_continuous_physics=True,extra_applied_forces=False)

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--model-dir',type=Path);p.add_argument('--prepared-inputs',type=Path);p.add_argument('--out',type=Path,default=R/'results');a=p.parse_args();out=a.out;out.mkdir(parents=True,exist_ok=True);cfg=json.loads((R/'config.json').read_text());root=R.parents[1]
 if a.model_dir:model_dir=a.model_dir
 else:
  raw=(root/cfg['legacy_archive']['path']).read_bytes();assert sha(raw)==cfg['legacy_archive']['sha256'];model_dir=R/'cache/model';model_dir.mkdir(parents=True,exist_ok=True)
  with zipfile.ZipFile(io.BytesIO(raw)) as z:
   for name in cfg['model_files']:(model_dir/name).write_bytes(z.read(name))
 for name,h in cfg['model_files'].items():assert sha((model_dir/name).read_bytes())==h
 spec=importlib.util.spec_from_file_location('archived_ab_simulation',model_dir/'simulation.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);sim=module.Simulation(model_dir/'parameters.yaml')
 if a.prepared_inputs:
  with np.load(a.prepared_inputs,allow_pickle=False) as z:neural={name:z[name] for name in cfg['neural_outputs']}
 else:
  raw=(R/'cache'/cfg['neural_output_source']['name']).read_bytes();assert sha(raw)==cfg['neural_output_source']['sha256']
  with zipfile.ZipFile(io.BytesIO(raw)) as z:neural={name:arrays(z,f'FreeBody_{name}_inputs.npz')['u'] for name in cfg['neural_outputs']}
 for name,u in neural.items():assert sha(u.tobytes())==cfg['neural_outputs'][name]['u_sha256']
 np.savez_compressed(out/'neural-u.npz',**neural)
 ab={case:sim.load_ab(case) for case in ['A','B']};aux=sim.nonmuscle_indices;muscles=sim.muscle_indices
 for k in ['initial_state','initial_warmstart']:assert np.array_equal(ab['A'][k],ab['B'][k])
 assert np.array_equal(ab['A']['controls'][:,aux],ab['B']['controls'][:,aux])
 assert sha(ab['A']['controls'][:,muscles].tobytes())==cfg['training_target_identity']['native_A_muscle_matrix_sha256']
 baseline=ab['A']['controls'];t=np.arange(len(baseline))*sim.model.opt.timestep;timing=cfg['timing'];index=np.floor((timing['neural_start_ms']+t*1000*timing['neural_ms_per_body_ms'])/timing['u_bin_ms']).astype(int)
 assert index.max()<min(len(u) for u in neural.values())
 controls={case:ab[case]['controls'].copy() for case in ['A','B']}
 for name,u in neural.items():
  c=baseline.copy();c[:,muscles]=u[index];controls[name]=c
 for c in controls.values():assert np.array_equal(c[:,aux],baseline[:,aux])
 results={};reports={}
 for name,c in controls.items():
  z,report=integrate(sim,c)
  if name in ab:
   independent=sim.replay_ab(name)
   assert np.array_equal(z['full_state'],independent['full_state']), 'Generic comparison must exactly reproduce archived replay'
   report['archived_replayer_exact_state_equality']=True;report['original_replay_metrics']=independent['metrics']
   assert report['min_body_up_z']>.9,'Native AB upright replay failed; do not label restored success'
  report['controls_sha256']=sha(c.tobytes());report['full_state_sha256']=sha(z['full_state'].tobytes());report['auxiliary_controls_exactly_archived']=True;report['initial_full_state_sha256']=sha(z['initial_state'].tobytes());report['warmstart_sha256']=sha(z['initial_warmstart'].tobytes())
  report['muscle_u_rmse_to_native_A']=float(np.sqrt(np.mean((c[:,muscles]-controls['A'][:,muscles])**2)));report['muscle_u_rmse_to_native_B']=float(np.sqrt(np.mean((c[:,muscles]-controls['B'][:,muscles])**2)))
  np.savez_compressed(out/f'NativeAB_{name}_state.npz',**z);results[name]=z;reports[name]=report;print(name,json.dumps(report),flush=True)
 # Matched identity test: the A target itself substituted through the same interface
 # gives exactly the restored A state, not a different timing/auxiliary baseline.
 identity=baseline.copy();identity[:,muscles]=controls['A'][:,muscles];check,_=integrate(sim,identity);assert np.array_equal(check['full_state'],results['A']['full_state'])
 render=sim.config['rendering'];w,h=render['panel_width'],render['height'];ff=imageio_ffmpeg.get_ffmpeg_exe();streams={};names=list(results);preview=None
 def encoder(path,width,height):return subprocess.Popen([ff,'-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{width}x{height}','-r',str(render['fps']),'-i','-','-an','-c:v','libx264','-crf','20','-pix_fmt','yuv420p',str(path)],stdin=subprocess.PIPE)
 for name in names:streams[name]=encoder(out/f'NativeAB_{name}.mp4',w,h)
 combined=encoder(out/'NativeAB_Comparison.mp4',w*2,h*2)
 try:
  for f,ts in enumerate(np.linspace(0,results['A']['time_s'][-1],render['frames'])):
   panels=[]
   for name,z in results.items():
    st=z['initial_state'] if f==0 else z['full_state'][int(np.argmin(abs(z['time_s']-ts)))];im=Image.fromarray(sim._image(st));d=ImageDraw.Draw(im);d.rectangle((0,0,w,58),fill='black')
    title='ORIGINAL '+name+' | native 141 controls' if name in ab else name.upper()+' | only muscle controls replaced'
    for y,text in [(4,title),(22,f'Physical t={ts:.3f}s | original AB initial state + 11 aux'),(40,'FREE BODY | native muscles, ground, adhesion | 0.05x')]:d.text((6,y),text,fill='white')
    arr=np.asarray(im);streams[name].stdin.write(arr.tobytes());panels.append(arr)
   frame=np.concatenate([np.concatenate(panels[:2],axis=1),np.concatenate(panels[2:],axis=1)],axis=0);combined.stdin.write(frame.tobytes())
   if f in [0,render['frames']//2,render['frames']-1]:Image.fromarray(frame).save(out/f'NativeAB_preview_{f:03d}.jpg',quality=92)
   if f%30==0:print('Rendered',f,'/',render['frames'],flush=True)
 finally:
  for proc in [*streams.values(),combined]:proc.stdin.close()
  for proc in [*streams.values(),combined]:assert proc.wait()==0
  sim.close()
 for path in out.glob('*.mp4'):subprocess.run([ff,'-v','error','-i',str(path),'-f','null','-'],check=True)
 report=dict(code_revision=git_revision(),command=sys.argv,python=platform.python_version(),versions={n:version(n) for n in ['numpy','mujoco','PyYAML','Pillow','imageio-ffmpeg']},config=cfg,conditions=reports,matched_simulation_verified=True,target_substitution_identity_exact=True,limits='Short0.4s native AB replay, not long-term walking. Both neural checkpoints were trained on A only, with 26 missing MN mappings. Time warp is a neural-output interface convention, not native biological frequency. Auxiliary adhesion/head/abdomen controls remain archived, not neural-generated.')
 (out/'NativeAB_report.json').write_text(json.dumps(report,indent=2)+'\n')
 # Standalone reproduction bundle, with original model/engine, exact inputs and this driver.
 package=out/'NativeAB_Reproduction_Bundle.zip'
 with zipfile.ZipFile(package,'w',zipfile.ZIP_DEFLATED) as z:
  for name in cfg['model_files']:z.write(model_dir/name,'model/'+name)
  z.write(Path(__file__),'replay_compare.py');z.write(R/'config.json','config.json');z.write(out/'neural-u.npz','inputs/neural-u.npz')
  z.writestr('RUN.txt','Install pinned versions in config.json; enable EGL. Run: MUJOCO_GL=egl python replay_compare.py --model-dir model --prepared-inputs inputs/neural-u.npz --out rerun\nNo credentials/network required. Original source identities are in config.json and outputs/NativeAB_report.json.\n')
  for path in sorted(out.iterdir()):
   if path.is_file() and path.suffix in ['.mp4','.jpg','.npz','.json']:z.write(path,'outputs/'+path.name)
 manifest=dict(report=report,assets=[dict(name=p.name,bytes=p.stat().st_size,sha256=sha(p.read_bytes()),url='https://github.com/linzhefeng24/Applepie/releases/download/fixed-body-video-20261115/'+p.name) for p in sorted(out.iterdir()) if p.suffix in ['.mp4','.zip','.jpg']])
 (out/'NativeAB_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
if __name__=='__main__':main()
