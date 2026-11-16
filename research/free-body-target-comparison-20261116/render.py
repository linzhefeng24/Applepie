"""Free-root comparison: actual neural outputs versus the exact training u(t).
No new parameter fitting. Original 130-channel MuJoCo body and native contacts.
"""
from pathlib import Path
import hashlib,io,json,subprocess,sys,zipfile
from importlib.metadata import version
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from matplotlib import font_manager
R=Path(__file__).resolve().parent;ROOT=R.parents[1]
sys.path.insert(0,str(ROOT/'research/single-model-delivery-20261115/runtime/02_code'))
from flymodel import Model
from flymodel.render import Video,colors

def sha(b):return hashlib.sha256(b).hexdigest()
def load(z,name):
 with np.load(io.BytesIO(z.read(name)),allow_pickle=False) as a:return {k:a[k] for k in a.files}

def render(m,body,t,label,path):
 r=m.config['render'];mj=body.mj;bm=body.model;w=r['body_width'];h=r['body_height']
 bm.vis.global_.offwidth=max(bm.vis.global_.offwidth,w);bm.vis.global_.offheight=max(bm.vis.global_.offheight,h)
 renderer=mj.Renderer(bm,height=h,width=w,max_geom=r['max_geom']);opt=mj.MjvOption();opt.flags[mj.mjtVisFlag.mjVIS_TENDON]=False;opt.sitegroup[:]=0
 for i in range(bm.ngeom):
  name=bm.geom(i).name
  if name.startswith(r['hide_geom_prefix']):bm.geom_rgba[i,3]=0
  elif name.startswith('walker/'):bm.geom_rgba[i,3]=r['body_opacity']
 sites=[[bm.site(n).id for n in x['path_site_names']] for x in m.config['body']['muscles']]
 font=ImageFont.truetype(font_manager.findfont(r['font_family']),r['font_size']);v=Video(path,w,h,r);previous=np.zeros(len(m.mapping));previews=[]
 try:
  for f,ts in enumerate(np.linspace(t['time_s'][0],t['time_s'][-1],r['frame_count'])):
   k=int(np.argmin(abs(t['time_s']-ts)));a=t['muscle_activation'][k];signal=np.where(a-previous < -r['muscle_decay_threshold'],-a,a);previous=a.copy();mc=colors(signal,m.config['neuromuscular']['excitation_bounds'][1],r)
   body.restore_for_render(t,k);body.data.ctrl[body.indices]=t['muscle_u_applied'][k]
   renderer.update_scene(body.data,camera=m.config['body']['camera_id'],scene_option=opt)
   for j,ss in enumerate(sites):
    for sa,sb in zip(ss[:-1],ss[1:]):
     assert renderer.scene.ngeom<r['max_geom'];g=renderer.scene.geoms[renderer.scene.ngeom]
     mj.mjv_initGeom(g,mj.mjtGeom.mjGEOM_CAPSULE,np.zeros(3),np.zeros(3),np.eye(3).reshape(-1),mc[j].astype(np.float32))
     mj.mjv_connector(g,mj.mjtGeom.mjGEOM_CAPSULE,r['muscle_radius_native']+r['muscle_radius_gain_native']*a[j],body.data.site_xpos[sa],body.data.site_xpos[sb]);renderer.scene.ngeom+=1
   im=Image.fromarray(renderer.render().copy());d=ImageDraw.Draw(im);d.rectangle((0,0,w,r['caption_height']),fill='black');x,y=r['caption_margin']
   for line,text in enumerate([f'{label} | FREE BODY | {ts:.3f}s','RED activation | GREEN decreasing activation | native ground contacts','No root constraint, no rescue forces, no state resets']):d.text((x,y+line*r['caption_line_height']),text,fill='white',font=font)
   v.write(np.asarray(im))
   if f in (0,r['frame_count']//2,r['frame_count']-1):previews.append(im.copy())
 finally:renderer.close();v.close()
 return previews

def main():
 out=R/'results';out.mkdir(exist_ok=True);archive=R/'cache/BPTT_Epoch123_1000_State.zip'
 assert sha(archive.read_bytes())=='375594694d2d199aca8da485e7b82be14ba5a44db63556e9c3f43f61f7b5a820' # checked against source manifest below
 base=ROOT/'research/single-model-delivery-20261115/build/UnifiedFlyModel/01_model/model.yaml'
 target=ROOT/'research/conductance-rebuild-20261114/data/old-A-muscle-targets.npz'
 assert sha(target.read_bytes())=='f9f888bdfe2ce296fcc05edb719289d05ba051d1dda79be9aea66ade6f5b949b'
 reports=[];preview=Image.new('RGB',(1440,1080));initial=None
 for row,(name,label) in enumerate([('Epoch123','EPOCH 123'),('Epoch1000','EPOCH 1000'),('TargetU','DIRECT TARGET u(t), 3x time stretch')]):
  m=Model(base);assert m.sha256=='858d1818b8d8394c95bb62a6ce60474cb534a83b94265ef8615e367c110d262c'
  if name!='TargetU':
   epoch=int(name[5:])
   with zipfile.ZipFile(archive) as z:
    n=load(z,f'epoch{epoch}/neural-state.npz');m.cells[:]=load(z,f'epoch{epoch}/resolved-cell-parameters.npz')['values'];u=m.muscle_excitation(n)
   origin={'epoch':epoch,'neural_run_id':str(n['run_id']),'effective_cell_array_sha256':sha(m.cells.tobytes()),'channels_with_candidate_MN_mapping':104}
  else:
   with np.load(target,allow_pickle=False) as z:
    ids=list(z['muscle_ids']);native_t=np.arange(len(z['target_u']))*float(z['dt_s'])*1000
    ms=np.arange(1600);u=np.stack([np.interp((ms-200)/3,native_t,z['target_u'][:,ids.index(x['muscle_id'])]) for x in m.mapping],axis=1)
   origin={'target_sha256':sha(target.read_bytes()),'input':'target_u, not target_a','time_mapping':'target_ms=(neural_ms-200)/3; same mapping as training; hold last sample after 1.2 s body time','channels':130,'neural_network_bypassed':True}
  body=m.body(fixed_root=False);assert not body.fixed_root
  start=np.r_[body.data.qpos,body.data.qvel,body.data.act]
  if initial is None:initial=start.copy()
  else:assert np.array_equal(start,initial)
  p=m.config['demo'];step_ms=body.model.opt.timestep*1000;steps=round(p['body_duration_ms']/step_ms);stride=max(1,round(p['body_record_interval_ms']/step_ms));rows=[]
  for k in range(steps):
   idx=min(int((p['body_neural_start_ms']+k*step_ms)/m.config['neural']['solver']['spike_bin_ms']),len(u)-1)
   body.step(u[idx])
   if k%stride==0 or k==steps-1:rows.append(body.observe())
  t={key:np.array([x[key] for x in rows]) for key in rows[0]};t['fixed_root']=np.array(False);t['model_sha256']=np.array(m.sha256);t['neural_time_ms']=p['body_neural_start_ms']+t['time_s']*1000
  assert np.isfinite(t['qpos']).all() and not t['extra_applied_force'].any()
  np.savez_compressed(out/f'FreeBody_{name}_state.npz',**t);np.savez_compressed(out/f'FreeBody_{name}_inputs.npz',u=u,initial_state=start)
  print('Rendering',name,flush=True);frames=render(m,body,t,label,out/f'FreeBody_{name}.mp4')
  for j,im in enumerate(frames):preview.paste(im.resize((480,360)),(j*480,row*360))
  report=dict(condition=name,base_model_sha256=m.sha256,initial_state_sha256=sha(start.tobytes()),input_u_sha256=sha(u.tobytes()),origin=origin,fixed_root=False,max_thorax_displacement_native=float(np.linalg.norm(t['thorax_position_native']-t['thorax_position_native'][0],axis=1).max()),min_body_up_z=float(t['body_up_z'].min()),max_ground_contacts=int(t['ground_contact_count'].max()),ground_normal_force_max_native=float(t['ground_contact_normal_force_native'].max()),body_duration_s=float(t['time_s'][-1]),no_sensory_to_neural_feedback=True,free_walking_success_not_assumed=True)
  reports.append(report);print(json.dumps(report),flush=True)
 preview.save(out/'FreeBody_preview.jpg',quality=90)
 import imageio_ffmpeg
 ff=imageio_ffmpeg.get_ffmpeg_exe();inputs=sum((['-i',str(out/f'FreeBody_{name}.mp4')] for name in ['Epoch123','Epoch1000','TargetU']),[])
 subprocess.run([ff,'-y','-v','error',*inputs,'-filter_complex','hstack=inputs=3','-c:v','libx264','-crf','20','-pix_fmt','yuv420p',str(out/'FreeBody_Comparison.mp4')],check=True)
 for path in out.glob('*.mp4'):subprocess.run([ff,'-v','error','-i',str(path),'-f','null','-'],check=True)
 report={'code_revision':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'command':sys.argv,'versions':{k:version(k) for k in ['numpy','mujoco','matplotlib','imageio-ffmpeg']},'conditions':reports,'limitations':'All cases use the current body and initial state. Target replay does not reproduce the old AB model/initial state; time stretch matches fitting, not native-speed old walking. Neural conditions have 26 unmapped channels whereas direct target drives all130. Fixed camera can lose a moving/falling body. No sensory feedback, stabilization or success inference.'}
 (out/'FreeBody_report.json').write_text(json.dumps(report,indent=2)+'\n')
 with zipfile.ZipFile(out/'FreeBody_Comparison_Bundle.zip','w',zipfile.ZIP_DEFLATED) as z:
  for path in sorted(out.iterdir()):
   if path.is_file() and path.suffix!='.zip':z.write(path,path.name)
 manifest=dict(report=report,assets=[{'name':p.name,'bytes':p.stat().st_size,'sha256':sha(p.read_bytes()),'url':'https://github.com/linzhefeng24/Applepie/releases/download/fixed-body-video-20261115/'+p.name} for p in sorted(out.iterdir()) if p.suffix in ('.mp4','.zip','.jpg')])
 (out/'FreeBody_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
if __name__=='__main__':main()
