"""Replay archived MN input through unchanged public backend; render without state edits."""
from pathlib import Path
import json,subprocess,copy,importlib.metadata
import numpy as np,mujoco
from PIL import Image,ImageDraw
from fly_scene.vendor.body_backend_v2 import BodyBackendV2
from mn_muscle.six_leg import SixLegMNBackend
ROOT=Path(__file__).parent;SOURCE=ROOT.parent/'support/motor_experiments_20261013/walk_1khz/open_loop_program.npz'
body=BodyBackendV2(vision=False);renderer=None;writer=None
try:
 body.reset();backend=SixLegMNBackend(body);muscles=backend.muscles;m=body.sim.mj_model;d=body.sim.mj_data
 with np.load(SOURCE,allow_pickle=False) as z:
  assert str(z['graph_sha256'])==muscles.registry.document['graph_sha256']
  np.testing.assert_array_equal(z['body_ids'],muscles.registry.body_ids);np.testing.assert_array_equal(z['R'],muscles.R);np.testing.assert_allclose(z['q_reference'],muscles.q_reference,atol=1e-9)
  excitation=z['group_excitation'].copy();dt=float(z['dt_s'])
 renderer=mujoco.Renderer(m,height=480,width=640);camera=mujoco.MjvCamera();camera.distance=6;camera.azimuth=125;camera.elevation=-25
 writer=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s','640x480','-r','50','-i','-','-an','-c:v','libx264','-crf','19','-pix_fmt','yuv420p',str(ROOT/'reproduced_walk.mp4')],stdin=subprocess.PIPE)
 positions=[];uprights=[];poses=[];velocities=[];states=[];initial=d.xpos[body._thorax_id].copy();frame=0
 for k,groups in enumerate(excitation):
  backend.step(muscles.expand_groups(groups),muscles.registry.body_ids,dt)
  pos=d.xpos[body._thorax_id].copy();positions.append(pos);uprights.append(float(d.xmat[body._thorax_id].reshape(3,3)[2,2]));poses.append(d.qpos.copy());velocities.append(d.qvel.copy())
  if (k+1)%20==0:
   before=d.qpos.copy();warm=d.qacc_warmstart.copy();camera.lookat[:]=pos;renderer.update_scene(d,camera=camera);im=Image.fromarray(renderer.render());np.testing.assert_array_equal(d.qpos,before);np.testing.assert_array_equal(d.qacc_warmstart,warm)
   draw=ImageDraw.Draw(im);draw.rectangle((0,0,640,46),fill='black');draw.text((10,7),f'LOCAL REPLAY | t={(k+1)*dt:.2f}s | forward={pos[0]-initial[0]:.2f} mm',fill='white');draw.text((10,26),'Saved MN input -> simplified muscles -> ground-contact physics',fill='white');writer.stdin.write(np.asarray(im).tobytes())
   if frame in (0,124,249):im.save(ROOT/f'reproduced_frame_{frame:03d}.png')
   frame+=1
  if (k+1)%1000==0:print(f'Replayed {(k+1)*dt:.1f}s / 5.0s; frames={frame}',flush=True)
 writer.stdin.close();assert writer.wait()==0;writer=None
 positions=np.array(positions);report=dict(forward_mm=float(positions[-1,0]-positions[0,0]),min_up=min(uprights),duration_s=backend.elapsed_s,source='saved prescribed MN sequence',sensory_feedback=False,cpg=False,servo=False,learned_MaleCNS=False,public_interface_replay=True)
 report['walking_pass']=report['forward_mm']>2 and report['min_up']>.5
 archived=json.loads((SOURCE.parent.parent/'public_replay.json').read_text());reference=json.loads((ROOT/'original_interface_report.json').read_text())
 assert report==reference==archived,(report,reference,archived)
 np.savez_compressed(ROOT/'reproduced_trajectory.npz',position_mm=positions,upright=uprights,qpos=poses,qvel=velocities,group_excitation=excitation,dt_s=dt)
 report.update(archived_report_exact_match=True,rendered_replay_exact_match=True,video_frames=frame,versions={n:importlib.metadata.version(n) for n in ['flygym','mujoco','numpy','scipy']},initialization='Original 50 ms position-controlled warmup before walking clock; adhesion off during walking')
 (ROOT/'reproduced_report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2),flush=True)
finally:
 if writer is not None:writer.stdin.close();writer.wait()
 if renderer is not None:renderer.close()
 body.close()
