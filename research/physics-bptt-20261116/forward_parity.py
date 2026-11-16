"""Full0.4s AB check: restoring augmented adjoint state preserves native stepping."""
from pathlib import Path
import hashlib,json,sys
import numpy as np
import mujoco
from physics_adjoint import NativeAdjoint
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'cache/model'));from simulation import Simulation
sim=Simulation(R/'cache/model/parameters.yaml');rows=[]
for case in ['A','B']:
 engine=NativeAdjoint(sim,np.zeros((1,len(sim.config['reference']['joint_qpos_indices']))));sim.reset(case);s=engine.initial;maximum=0.
 for c in sim.load_ab(case)['controls']:
  s=engine.step(s,c);sim.data.ctrl[:]=c;mujoco.mj_step(sim.model,sim.data)
  maximum=max(maximum,float(abs(s.q-sim.data.qpos).max()),float(abs(s.v-sim.data.qvel).max()),float(abs(s.a-sim.data.act).max()),float(abs(s.warm-sim.data.qacc_warmstart).max()),abs(s.time-sim.data.time))
 assert maximum==0;rows.append(dict(case=case,physical_steps=len(sim.load_ab(case)['controls']),duration_s=s.time,qpos_qvel_activation_warmstart_time_max_difference=maximum))
report=dict(command=sys.argv,source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),native_augmented_forward_elementwise_exact=True,conditions=rows)
(R/'forward-parity.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
