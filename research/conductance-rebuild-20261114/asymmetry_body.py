"""Actual-body validation with matched constant-mean and zero-input controls.
All runs preserve original initial state/warmstart and head/abdomen controls;
adhesion is off, no applied rescue forces, no resets within0.4s.
"""
from pathlib import Path
import argparse,sys,json
import numpy as np,mujoco
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks
R=Path(__file__).parent;O=R/'results/asymmetry';p=argparse.ArgumentParser();p.add_argument('--model-dir',type=Path,default=Path('/workspace/flymimic-twofile'));args=p.parse_args();sys.path.insert(0,str(args.model_dir));from simulation import Simulation
rows=json.load(open(O/'trials.json'));rank=sorted(rows,key=lambda x:x['metrics']['training_score']);best=rank[0]['trial'];second=next(x['trial'] for x in rank if x['trial'] not in {best,'baseline'});reports=[]
def joint_metrics(q,tau,pos,neg):
 out=[]
 for j,leg in enumerate(['LF','LM','LH','RF','RM','RH']):
  x=gaussian_filter1d(np.rad2deg(q[400:,j]),10);peaks,_=find_peaks(x,distance=150,prominence=2.);troughs,_=find_peaks(-x,distance=150,prominence=2.);amp=float(np.ptp(x));active=tau[400:,j];ampT=float(np.std(active));denom=max(float(np.mean(pos[400:,j]-neg[400:,j])),1e-12);balance=(pos[400:,j]+neg[400:,j])/denom
  out.append({'leg':leg,'angle_peak_to_peak_deg':amp,'peaks':len(peaks),'troughs':len(troughs),'repeated_motion':bool(amp>=5 and len(peaks)>=2 and len(troughs)>=2),'active_torque_std_native':ampT,'positive_active_torque_mean_native':float(pos[400:,j].mean()),'negative_active_torque_mean_native':float(neg[400:,j].mean()),'normalized_active_imbalance_std':float(balance.std())})
 return out
with Simulation(args.model_dir/'parameters.yaml') as sim:
 m=sim.model;d=sim.data;stored=sim.load_ab('A');bid=m.body('walker/thorax').id;mi=sim.muscle_indices;auxadh=[i for i,n in enumerate(sim.actuator_names) if n.startswith('walker/adhere_claw_')];names=['T1_left','T2_left','T3_left','T1_right','T2_right','T3_right'];qa=[m.jnt_qposadr[m.joint('walker/tibia_'+n).id] for n in names];dv=[m.jnt_dofadr[m.joint('walker/tibia_'+n).id] for n in names];J=np.zeros((m.nu,m.nv))
 cases=[('previous_readout',R/'results/adult-muscle-readout.npz','dynamic'),('shared_baseline',O/'baseline.npz','dynamic'),('selected',O/f'{best}.npz','dynamic'),('second_candidate',O/f'{second}.npz','dynamic'),('selected_mean',O/f'{best}.npz','mean'),('selected_zero',O/f'{best}.npz','zero')]
 for label,path,mode in cases:
  z=np.load(path);u=z['predicted_u_native'].copy()
  if mode=='mean':u[:]=u.mean(axis=0)
  if mode=='zero':u[:]=0.
  sim.reset('A');poses=[];angles=[];acts=[];tau=[];positive=[];negative=[];up=[];w=mujoco.MjData(m)
  for k,ctrl in enumerate(stored['controls']):
   d.ctrl[:]=ctrl;d.ctrl[mi]=u[k];d.ctrl[auxadh]=0;assert not np.any(d.qfrc_applied) and not np.any(d.xfrc_applied);mujoco.mj_step(m,d)
   if k%2==1:
    mujoco.mju_sparse2dense(J,d.actuator_moment,d.moment_rownnz,d.moment_rowadr,d.moment_colind)
    bias=np.array([mujoco.mju_muscleBias(d.actuator_length[i],m.actuator_lengthrange[i],m.actuator_acc0[i],m.actuator_biasprm[i,:9]) for i in mi]);active=d.actuator_force[mi]-bias;contributions=J[mi][:,dv]*active[:,None]
    positive.append(np.maximum(contributions,0).sum(axis=0));negative.append(np.minimum(contributions,0).sum(axis=0));tau.append(contributions.sum(axis=0));angles.append(d.qpos[qa].copy());poses.append(d.qpos.copy());acts.append(d.act[sim.activation_addresses].copy());w.qpos[:]=d.qpos;mujoco.mj_kinematics(m,w);up.append(float(w.xmat[bid].reshape(3,3)[2,2]))
  angles=np.array(angles);tau=np.array(tau);positive=np.array(positive);negative=np.array(negative);metrics=joint_metrics(angles,tau,positive,negative);record={'case':label,'neural_candidate':best if label.startswith('selected') else second if label=='second_candidate' else label,'input':mode,'metrics':metrics,'repeated_motion_legs':sum(x['repeated_motion'] for x in metrics),'min_body_up_z':min(up),'root_displacement_mm':((np.array(poses)[-1,:3]-stored['initial_state'][1:4])*10).tolist(),'finite':bool(np.isfinite(poses).all()),'duration_s':float(d.time),'adhesion':False,'extra_applied_forces':False,'physical_scope':'archived A initial state; original head/abdomen auxiliary controls; no intra-run reset','walking_validated':False};reports.append(record)
  np.savez_compressed(O/f'body-{label}.npz',qpos=poses,tibia_angle_rad=angles,activation=acts,upright=up,active_torque=tau,positive_active_torque=positive,negative_active_torque=negative)
  (O/'body-validation.json').write_text(json.dumps(reports,indent=2));print(label,'repeated motion',record['repeated_motion_legs'],'up',round(min(up),3),'amplitudes',[round(x['angle_peak_to_peak_deg'],2) for x in metrics],flush=True)
