"""Predeclared uniform NMJ-gain reduction, retaining neural spikes and ratios.
No per-leg phase changes. Compare with the frozen guarded baseline; all outcomes
are retained, including loss of movement or posture. This is a model prior test.
"""
from pathlib import Path
import json,sys,numpy as np
from scipy.signal import find_peaks
from scipy.ndimage import gaussian_filter1d
R=Path(__file__).parent;O=R/'results/asymmetry';z=np.load(O/'long-input-guarded.npz');records=[]
# Reconstruct pre-clipping signal from actual spikes and frozen gains rather
# than simply scaling clipped input, preserving the same causal NMJ equation.
if '--prepare' in sys.argv:
 from asymmetry_refinement import pools,T
 src=np.load(O/'guard-flexor_only-baseline.npz');spikes=src['spikes'];gain=z['constant_gain'];tau=float(z['tau_ms']);rates=np.array([spikes[:,p].mean(axis=1)*1000 if p else np.zeros(len(spikes)) for p in pools]).T
 state=np.zeros(130);f=np.empty_like(rates);decay=np.exp(-1/tau)
 for k in range(len(rates)):state=state*decay+(1-decay)*rates[k];f[k]=state
 signal=f[400+np.arange(10000)//10-1]/100*gain
 np.savez_compressed(O/'saturation-unclipped-signal.npz',signal=signal)
 sys.exit(0)
import mujoco
from archived_model import Simulation
signal=np.load(O/'saturation-unclipped-signal.npz')['signal']
with Simulation() as sim:
 m=sim.model;d=sim.data;old=sim.load_ab('A');bid=m.body('walker/thorax').id;work=mujoco.MjData(m);jn=m.joint('walker/tibia_T1_right').id;qa=m.jnt_qposadr[jn];upper=m.jnt_range[jn,1];adh=[i for i,n in enumerate(sim.actuator_names) if n.startswith('walker/adhere_claw_')]
 for scale in ([.5] if "--mean-only" in sys.argv else [.75,.5]):
  sim.reset('A');u=np.clip(signal*scale,0,1)
  mode='mean-' if '--mean-only' in sys.argv else ''
  if mode:u[:]=u.mean(axis=0)
  angles=[];up=[];a=[];poses=[]
  for k,ctrl in enumerate(u):
   d.ctrl[:]=old['controls'][min(k,len(old['controls'])-1)];d.ctrl[sim.muscle_indices]=ctrl;d.ctrl[adh]=0;assert not np.any(d.qfrc_applied) and not np.any(d.xfrc_applied);mujoco.mj_step(m,d)
   if k%2==1:
    angles.append(d.qpos[qa]);a.append(d.act[sim.activation_addresses].copy());poses.append(d.qpos.copy());work.qpos[:]=d.qpos;mujoco.mj_kinematics(m,work);up.append(work.xmat[bid].reshape(3,3)[2,2])
  x=gaussian_filter1d(np.rad2deg(angles[2000:]),10);hi,_=find_peaks(x,distance=150,prominence=2);lo,_=find_peaks(-x,distance=150,prominence=2);r={'input_mode':mode or 'rhythmic','uniform_readout_scale':scale,'RF_range_deg':float(np.ptp(x)),'peaks':len(hi),'troughs':len(lo),'min_body_up':float(min(up)),'fraction_near_upper_limit':float(np.mean(np.array(angles)[2000:]>=upper-np.deg2rad(1))),'passes_repetition_and_upright':bool(np.ptp(x)>=5 and len(hi)>=2 and len(lo)>=2 and min(up)>=.8),'no_reset_or_rescue':True};records.append(r);np.savez_compressed(O/f'saturation-{mode}scale-{scale}.npz',u=u,qpos=poses,activation=a,RF_angle_rad=angles,upright=up,time_s=np.arange(1,len(angles)+1)*.0002);(O/('saturation-mean-control.json' if mode else 'saturation-search.json')).write_text(json.dumps(records,indent=2));print(r,flush=True)
