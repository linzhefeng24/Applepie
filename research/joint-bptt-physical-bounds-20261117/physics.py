"""Immutable native AB data and white-box derivative templates.
Parameters/initial conditions come only from the immutable original AB archive.
Contact capacity is guarded: reaching it invalidates a rollout/update.
"""
from pathlib import Path
import hashlib,importlib.util,io,json,zipfile
import numpy as np
import jax
jax.config.update('jax_enable_x64',True)
import jax.numpy as j
from mujoco import mjx
R=Path(__file__).resolve().parent;ROOT=R.parents[1]

class ABPhysics:
 def __init__(self,config):
  self.cfg=config;p=ROOT/config['body_archive'];assert hashlib.sha256(p.read_bytes()).hexdigest()==config['body_archive_sha256']
  directory=R/'cache/model';directory.mkdir(parents=True,exist_ok=True)
  with zipfile.ZipFile(p) as z:
   for name in ['parameters.yaml','simulation.py']:(directory/name).write_bytes(z.read(name))
  spec=importlib.util.spec_from_file_location('native_AB_joint300',directory/'simulation.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
  self.native=mod.Simulation(directory/'parameters.yaml');m=self.native.model
  assert m.npair==0 and m.nu==141 and len(self.native.muscle_indices)==130
  assert abs(m.opt.timestep-config['physical_dt_s'])<1e-15
  self.m=mjx.put_model(m);self.template=mjx.make_data(self.m)
  self.initial=(j.asarray(self.native.data.qpos.copy()),j.asarray(self.native.data.qvel.copy()),j.asarray(self.native.data.act.copy()),j.asarray(self.native.data.qacc_warmstart.copy()))
  self.dt=float(m.opt.timestep);self.controls=j.asarray(self.native.load_ab('A')['controls']);self.muscles=j.asarray(self.native.muscle_indices);self.joint_ids=j.asarray(self.native.config['reference']['joint_qpos_indices'])
  self.nsteps=int(config['physical_steps']);reference=mod._table(self.native.config['reference']['joint_angles']);ref_dt=self.dt*self.native.load_ab('A')['sample_stride']
  self.target=j.asarray(np.stack([np.interp(np.arange(1,self.nsteps+1)*self.dt,np.arange(len(reference))*ref_dt,reference[:,k]) for k in range(reference.shape[1])],axis=1))
  self.clock_indices=j.asarray(np.floor(config['neural_start_ms']+np.arange(self.nsteps)*self.dt*1000*config['neural_ms_per_physical_ms']).astype(np.int32))
  self.contact_dims=self.template.contact.dim
  # Every field below is immutable physical data. Templates are reset to the
  # current carried physical state; carried state itself is never reset.
  self.template=self.template.replace(mocap_pos=j.asarray(self.native.data.mocap_pos),mocap_quat=j.asarray(self.native.data.mocap_quat),eq_active=j.asarray(self.native.data.eq_active))
