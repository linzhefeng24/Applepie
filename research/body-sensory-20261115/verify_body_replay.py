"""Check observing contact forces leaves the archived integration unchanged."""
from pathlib import Path
import argparse,json,sys
import numpy as np
import mujoco
R=Path(__file__).parent;a=argparse.ArgumentParser();a.add_argument('--model-directory',type=Path,required=True);args=a.parse_args();sys.path.insert(0,str(args.model_directory));from simulation import Simulation
rows=[]
for case in ['A','B']:
 s=Simulation(args.model_directory/'parameters.yaml',case=case)
 for u in s.load_ab(case)['controls']:s.data.ctrl[:]=u;mujoco.mj_step(s.model,s.data)
 d=json.load(open(R/'results'/(case+'-ground')/'manifest.json'));delta=float(np.max(np.abs(s.data.qpos-np.array(d['final_qpos_native']))));assert delta==0
 z=np.load(R/'results'/(case+'-ground')/'body-sensory.npz');np.testing.assert_allclose(z['ground_world_force_native'][:,:,2],z['ground_normal_native'],atol=1e-12);assert np.max(np.abs(z['ground_tangent_force_native'][:,:,2]))<1e-12
 rows.append({'case':case,'observed_vs_unobserved_final_qpos_max_abs':delta,'ground_frame_world_force_balance':'verified for horizontal plane'})
z=np.load(R/'results/A-no-ground/body-sensory.npz');assert not z['ground_normal_native'].any();assert not z['ground_world_force_native'].any();(R/'results/observation-validation.json').write_text(json.dumps({'status':'independent replay equality and force-frame checks passed','conditions':rows,'ground_removal_contact_force_zero':True},indent=2)+'\n');print(rows)
