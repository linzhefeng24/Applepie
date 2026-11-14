"""Developmental physical-motion search, not a blind walking test.
Checks post-transient tibia motion and body orientation; then reruns the chosen
input at its constant time mean and zero. Same native initial state in all runs.
"""
from pathlib import Path
import sys,json
import numpy as np,mujoco
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks
R=Path(__file__).parent;O=R/'results/asymmetry';sys.path.insert(0,'/workspace/flymimic-twofile');from simulation import Simulation
spec=json.load(open(O/'motion-readout-grid.json'));records=[]

def metrics(q,tau,frequency=spec['analysis_frequency_hz']):
 result=[];t=np.arange(400,2000)*.0002;X=np.column_stack([np.ones(len(t)),t,np.sin(2*np.pi*frequency*t),np.cos(2*np.pi*frequency*t)])
 for j,leg in enumerate(['LF','LM','LH','RF','RM','RH']):
  a=gaussian_filter1d(np.rad2deg(q[400:,j]),10);hi,_=find_peaks(a,distance=150,prominence=2.);lo,_=find_peaks(-a,distance=150,prominence=2.);fit=np.linalg.lstsq(X,a,rcond=None)[0];span=float(np.ptp(a));result.append({'leg':leg,'peak_to_peak_deg':span,'peaks':len(hi),'troughs':len(lo),'harmonic_amplitude_deg':float(np.linalg.norm(fit[-2:])),'repeated_motion':bool(span>=5 and len(hi)>=2 and len(lo)>=2),'actuator_torque_std_native':float(np.std(tau[400:,j]))})
 return result

with Simulation() as sim:
 m=sim.model;d=sim.data;stored=sim.load_ab('A');mi=sim.muscle_indices;legs=['T1_left','T2_left','T3_left','T1_right','T2_right','T3_right'];qa=[m.jnt_qposadr[m.joint('walker/tibia_'+s).id] for s in legs];dv=[m.jnt_dofadr[m.joint('walker/tibia_'+s).id] for s in legs];adh=[i for i,n in enumerate(sim.actuator_names) if n.startswith('walker/adhere_claw_')];bid=m.body('walker/thorax').id;work=mujoco.MjData(m)
 def run(name,u,mode='dynamic'):
  sim.reset('A');angles=[];poses=[];act=[];tau=[];up=[]
  for k,ctrl in enumerate(stored['controls']):
   d.ctrl[:]=ctrl;d.ctrl[mi]=u[k];d.ctrl[adh]=0;assert not np.any(d.qfrc_applied) and not np.any(d.xfrc_applied);mujoco.mj_step(m,d)
   if k%2==1:
    angles.append(d.qpos[qa].copy());poses.append(d.qpos.copy());act.append(d.act[sim.activation_addresses].copy());tau.append(d.qfrc_actuator[dv].copy());work.qpos[:]=d.qpos;mujoco.mj_kinematics(m,work);up.append(float(work.xmat[bid].reshape(3,3)[2,2]))
  angles=np.array(angles);tau=np.array(tau);ms=metrics(angles,tau);row={'name':name,'input_mode':mode,'metrics':ms,'repeated_motion_legs':sum(x['repeated_motion'] for x in ms),'min_body_up_z':min(up),'physical_criterion_pass':bool(min(up)>=.8 and any(x['repeated_motion'] for x in ms)),'finite':bool(np.isfinite(poses).all()),'adhesion':False,'extra_applied_forces':False,'walking_validated':False};records.append(row);np.savez_compressed(O/('body-'+name+'.npz'),qpos=poses,tibia_angle_rad=angles,activation=act,upright=up,actuator_torque=tau);(O/'motion-body-grid.json').write_text(json.dumps(records,indent=2));print(name,'repeated',row['repeated_motion_legs'],'up',round(min(up),3),'amplitudes',[round(x['peak_to_peak_deg'],1) for x in ms],flush=True);return row
 for candidate in spec['trials']:
  z=np.load(O/(candidate['name']+'.npz'));run(candidate['name'],z['predicted_u_native'])
 valid=[r for r in records if r['physical_criterion_pass']];best=max(valid or records,key=lambda r:(r['physical_criterion_pass'],r['repeated_motion_legs'],sum(x['harmonic_amplitude_deg'] for x in r['metrics'] if x['repeated_motion']),r['min_body_up_z']))
 z=np.load(O/(best['name']+'.npz'));u=z['predicted_u_native'];mean=run(best['name']+'_mean',np.tile(u.mean(axis=0),(len(u),1)),'constant_mean');zero=run(best['name']+'_zero',np.zeros_like(u),'zero')
 causal=[]
 for a,b in zip(best['metrics'],mean['metrics']):
  if a['repeated_motion'] and not b['repeated_motion'] and a['harmonic_amplitude_deg']>max(1.5*b['harmonic_amplitude_deg'],.5):causal.append(a['leg'])
 (O/'motion-physical-selection.json').write_text(json.dumps({'selected':best,'mean_control':mean,'zero_control':zero,'causal_contrast_legs':causal,'minimum_goal_supported':bool(best['physical_criterion_pass'] and causal),'selection_used_body_development_data':True,'criterion':'At least2 peaks/troughs with2deg prominence and5deg excursion after80ms, upright>=.8; selected oscillation absent in constant-mean control and harmonic amplitude>1.5x control.','no_full_walking_claim':True},indent=2));print('Supported legs',causal,flush=True)
