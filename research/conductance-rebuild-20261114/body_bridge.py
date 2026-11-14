"""Native MuJoCo3.3.2 bridge diagnostic, NOT an independent walking policy.
Uses the archived two-file model; no resetting inside .4s or rescue forces.
Two auxiliary-control conditions are labelled, never conflated with neural
control of all141 actuators. Activation agreement tests the whole interface.
"""
from pathlib import Path
import argparse,sys,json
import numpy as np,mujoco
R=Path(__file__).parent
p=argparse.ArgumentParser();p.add_argument('--model-dir',type=Path,default=Path('/workspace/flymimic-twofile'));args=p.parse_args();sys.path.insert(0,str(args.model_dir));from simulation import Simulation,_table
z=np.load(R/'results/adult-muscle-readout.npz');u=z['predicted_u_native'];reports=[]
with Simulation(args.model_dir/'parameters.yaml') as sim:
 np.testing.assert_array_equal(np.array(sim.muscle_ids),z['muscle_ids']);m=sim.model;d=sim.data;stored=sim.load_ab('A');qa=np.array(sim.config['reference']['joint_qpos_indices']);ref=_table(sim.config['reference']['joint_angles'])[1:];bid=m.body('walker/thorax').id;adh=[i for i,name in enumerate(sim.actuator_names) if name.startswith('walker/adhere_claw_')]
 for mode in ['archived_auxiliaries','adhesion_off']:
  sim.reset('A');q=[];acts=[];ups=[];w=mujoco.MjData(m)
  for k,ctrl in enumerate(stored['controls']):
   d.ctrl[:]=ctrl;d.ctrl[sim.muscle_indices]=u[k]
   if mode=='adhesion_off':d.ctrl[adh]=0.
   assert not np.any(d.qfrc_applied) and not np.any(d.xfrc_applied)
   mujoco.mj_step(m,d)
   if k%2==1:
    q.append(d.qpos.copy());acts.append(d.act[sim.activation_addresses].copy());w.qpos[:]=d.qpos;mujoco.mj_kinematics(m,w);ups.append(float(w.xmat[bid].reshape(3,3)[2,2]))
  q=np.array(q);acts=np.array(acts);err=float(np.max(abs(acts-z['predicted_a'])));assert err<1e-8,err
  report={'condition':mode,'duration_s':float(d.time),'activation_bridge_max_error':err,'root_displacement_mm':((q[-1,:3]-stored['initial_state'][1:4])*sim.config['units']['native_length_to_mm']).tolist(),'min_body_up_z':min(ups),'joint_path_RMSE_deg':float(np.sqrt(np.mean(np.rad2deg(q[:,qa]-ref)**2))),'finite':bool(np.isfinite(q).all()),'extra_applied_forces':False,'continuous_without_state_reset':True,'walking_validated':False,'reason':'Only0.4s diagnostic; no body-to-neural feedback; head/abdomen auxiliaries retained; first condition also retains old adhesion.'};reports.append(report);np.savez_compressed(R/'results'/f'neural-body-{mode}.npz',qpos=q,activation=acts,upright=ups)
  print(report,flush=True)
(R/'results/body-bridge.json').write_text(json.dumps(reports,indent=2))
