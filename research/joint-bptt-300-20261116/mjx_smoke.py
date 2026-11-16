"""Compile one unchanged AB step and inspect physical force/adhesion parity."""
from pathlib import Path
import sys,time,json,hashlib
import numpy as np
import jax
jax.config.update('jax_enable_x64',True)
import jax.numpy as j
import mujoco
from mujoco import mjx
R=Path(__file__).resolve().parent;ROOT=R.parents[1]
sys.path.insert(0,str(ROOT/'research/restore-native-AB-20261116/cache'))
from simulation import Simulation
sim=Simulation(ROOT/'research/restore-native-AB-20261116/cache/parameters.yaml');m=sim.model
assert m.npair==0
mm=mjx.put_model(m);dd=mjx.make_data(mm);dd=dd.replace(qpos=j.asarray(sim.data.qpos),qvel=j.asarray(sim.data.qvel),act=j.asarray(sim.data.act),qacc_warmstart=j.asarray(sim.data.qacc_warmstart),ctrl=j.asarray(sim.load_ab('A')['controls'][0]))
print('dimensions',dd.ncon,dd.nefc,'compile forward',flush=True);start=time.time();f=jax.jit(mjx.step);result=f(mm,dd);result.qpos.block_until_ready();elapsed=time.time()-start
sim.data.ctrl[:]=sim.load_ab('A')['controls'][0];mujoco.mj_step(m,sim.data)
mat=np.zeros((m.nu,m.nv));mujoco.mju_sparse2dense(mat,sim.data.actuator_moment,sim.data.moment_rownnz,sim.data.moment_rowadr,sim.data.moment_colind)
report={'compile_and_step_seconds':elapsed,'qpos_max_error':float(abs(np.asarray(result.qpos)-sim.data.qpos).max()),'qvel_max_error':float(abs(np.asarray(result.qvel)-sim.data.qvel).max()),'activation_max_error':float(abs(np.asarray(result.act)-sim.data.act).max()),'actuator_force_max_error':float(abs(np.asarray(result.actuator_force)-sim.data.actuator_force).max()),'moment_max_error':float(abs(np.asarray(result.actuator_moment)-mat).max()),'adhesion_moment_max_error':float(abs(np.asarray(result.actuator_moment)[5:11]-mat[5:11]).max()),'qfrc_constraint_max_error':float(abs(np.asarray(result.qfrc_constraint)-sim.data.qfrc_constraint).max()),'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
(R/'smoke-report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2),flush=True)
print('second step timing',flush=True);start=time.time();result=f(mm,result.replace(ctrl=j.asarray(sim.load_ab('A')['controls'][1])));result.qpos.block_until_ready();print(time.time()-start,flush=True)
