"""One-second free-body continuation: actual HH-derived inputs, no repetition
of the0.4s program and no body-state resets. Auxiliary head/abdomen controls
hold their final archived values after0.4s; adhesion remains off throughout.
"""
from pathlib import Path
import json,sys,numpy as np,mujoco
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks
R=Path(__file__).parent;O=R/'results/asymmetry';from archived_model import Simulation
reports=[];guarded='--guarded' in sys.argv;guarded_fine='--guarded-fine' in sys.argv;output='long-body-guarded-fine-validation.json' if guarded_fine else 'long-body-guarded-validation.json' if guarded else 'long-body-validation.json'
with Simulation() as sim:
 m=sim.model;d=sim.data;saved=sim.load_ab('A');mi=sim.muscle_indices;names=['T1_left','T2_left','T3_left','T1_right','T2_right','T3_right'];qa=[m.jnt_qposadr[m.joint('walker/tibia_'+s).id] for s in names];dv=[m.jnt_dofadr[m.joint('walker/tibia_'+s).id] for s in names];adh=[i for i,n in enumerate(sim.actuator_names) if n.startswith('walker/adhere_claw_')];bid=m.body('walker/thorax').id;work=mujoco.MjData(m)
 for mode in (['guarded_fine','guarded_fine_mean','guarded_fine_E2'] if guarded_fine else ['guarded','guarded_mean','guarded_E2'] if guarded else ['dynamic','mean','fine','E2_silenced','zero']):
  z=np.load(O/('long-input-'+('guarded_fine' if mode=='guarded_fine_mean' else 'guarded' if mode=='guarded_mean' else 'dynamic' if mode in ['mean','zero'] else mode)+'.npz'));u=z['u'].copy()
  if mode in ['mean','guarded_mean','guarded_fine_mean']:u[:]=u.mean(axis=0)
  if mode=='zero':u[:]=0.
  sim.reset('A');angles=[];poses=[];acts=[];torques=[];up=[]
  for k,ctrl in enumerate(u):
   d.ctrl[:]=saved['controls'][min(k,len(saved['controls'])-1)];d.ctrl[mi]=ctrl;d.ctrl[adh]=0;assert not np.any(d.qfrc_applied) and not np.any(d.xfrc_applied);mujoco.mj_step(m,d)
   if k%2==1:
    angles.append(d.qpos[qa].copy());poses.append(d.qpos.copy());acts.append(d.act[sim.activation_addresses].copy());torques.append(d.qfrc_actuator[dv].copy());work.qpos[:]=d.qpos;mujoco.mj_kinematics(m,work);up.append(float(work.xmat[bid].reshape(3,3)[2,2]))
  a=np.array(angles);ms=[]
  for j,leg in enumerate(['LF','LM','LH','RF','RM','RH']):
   x=gaussian_filter1d(np.rad2deg(a[2000:,j]),10);hi,_=find_peaks(x,distance=150,prominence=2.);lo,_=find_peaks(-x,distance=150,prominence=2.);ms.append({'leg':leg,'peak_to_peak_deg_after0_4s':float(np.ptp(x)),'peaks':len(hi),'troughs':len(lo),'repeated_motion_after0_4s':bool(np.ptp(x)>=5 and len(hi)>=2 and len(lo)>=2)})
  record={'case':mode,'duration_s':float(d.time),'min_body_up_z':min(up),'min_body_up_z_first0_4s':min(up[:2000]),'root_displacement_mm':((np.array(poses)[-1,:3]-saved['initial_state'][1:4])*10).tolist(),'metrics':ms,'repeated_motion_legs_after0_4s':sum(x['repeated_motion_after0_4s'] for x in ms),'upright_criterion_pass':bool(min(up)>=.8),'finite':bool(np.isfinite(poses).all()),'no_reset_or_rescue':True,'adhesion':False,'walking_validated':False};reports.append(record);np.savez_compressed(O/('long-body-'+mode+'.npz'),qpos=poses,tibia_angle_rad=a,activation=acts,actuator_torque=torques,upright=up,time_s=np.arange(1,len(a)+1)*.0002)
  if mode in ['dynamic','fine','E2_silenced','guarded','guarded_E2','guarded_fine','guarded_fine_E2']:
   err=float(np.max(abs(np.array(acts)-z['activation'])));assert err<1e-8,err;record['native_activation_max_error']=err
  (O/output).write_text(json.dumps(reports,indent=2));print(mode,'up',round(min(up),3),'repeated legs after.4s',record['repeated_motion_legs_after0_4s'],'amplitudes',[round(x['peak_to_peak_deg_after0_4s'],1) for x in ms],flush=True)
