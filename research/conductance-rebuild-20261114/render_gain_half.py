"""Render recorded actual body poses against the matched-mean input control.
Visualization only: no interpolated poses, no trajectory correction. Shadows
and reflections disabled only in renderer options for fast, clear comparison.
"""
from pathlib import Path
import sys,subprocess
import numpy as np,mujoco
from PIL import Image,ImageDraw
R=Path(__file__).parent;O=R/'results/asymmetry';from archived_model import Simulation
traces=[np.load(O/'saturation-scale-0.5.npz'),np.load(O/'saturation-mean-scale-0.5.npz')];output=O/'gain-half-vs-mean.mp4'
with Simulation() as sim:
 m=sim.model;m.vis.quality.offsamples=0;renderer=mujoco.Renderer(m,height=300,width=400);d=mujoco.MjData(m);bid=m.body('walker/thorax').id;cam=mujoco.MjvCamera();cam.azimuth=-100.;cam.elevation=-20.;cam.distance=.65;opt=mujoco.MjvOption();opt.flags[mujoco.mjtVisFlag.mjVIS_TENDON]=False;opt.sitegroup[:]=0
 for i in range(m.ngeom):
  if m.geom(i).name.startswith('ghost/'):m.geom_rgba[i,3]=0.
 writer=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s','800x300','-r','40','-i','-','-an','-c:v','libx264','-crf','19','-pix_fmt','yuv420p',str(output)],stdin=subprocess.PIPE)
 try:
  for k,t in enumerate(np.linspace(0,1,40)):
   panels=[]
   for j,z in enumerate(traces):
    ix=int(np.argmin(abs(z['time_s']-t)));d.qpos[:]=z['qpos'][ix];mujoco.mj_forward(m,d);cam.lookat[:]=d.xpos[bid];renderer.update_scene(d,camera=cam,scene_option=opt)
    for flag in [mujoco.mjtRndFlag.mjRND_SHADOW,mujoco.mjtRndFlag.mjRND_REFLECTION]:renderer.scene.flags[flag]=False
    im=Image.fromarray(renderer.render());draw=ImageDraw.Draw(im);draw.rectangle((0,0,400,50),fill='black');draw.text((7,5),'HH -> muscles | fixed gains x0.5' if j==0 else 'Same initial state | constant mean u',fill='white');draw.text((7,22),f't={t:.3f}s | adhesion OFF | no rescue forces',fill='white');draw.text((7,37),'Single-leg motion assay; NOT six-leg walking',fill='white');panels.append(np.asarray(im))
   frame=np.concatenate(panels,axis=1);writer.stdin.write(frame.tobytes())
   if k in [0,20,39]:Image.fromarray(frame).save(O/f'gain-half-frame-{k:02d}.png')
   if k%10==0:print('Rendered',k,'/40',flush=True)
 finally:writer.stdin.close();renderer.close()
 if writer.wait()!=0:raise RuntimeError('ffmpeg failed')
