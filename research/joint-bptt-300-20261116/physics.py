"""White-box MJX3.3.2 AB dynamics with BODY adhesion and reverse solver scan.
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
  from implicit_solver import install
  install()
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
 def step(self,state,inputs):
  k,u=inputs;q,v,a,w=state
  ctrl=self.controls[k].at[self.muscles].set(u)
  d=self.template.replace(time=k*self.dt,qpos=q,qvel=v,act=a,qacc_warmstart=w,ctrl=ctrl)
  d=mjx.step(self.m,d)
  g1,g2=d.contact.geom[:,0],d.contact.geom[:,1]
  gap=j.maximum(self.m.geom_gap[g1],self.m.geom_gap[g2]);valid=(d.contact.dist<d.contact.includemargin+gap)&(g1>=0)&(g2>=0)
  counts=j.stack([j.sum(valid*(self.contact_dims==dim)) for dim in sorted(set(self.contact_dims))]);overflow=j.any(counts>=self.cfg['contact_capacity_per_dim'])
  finite=j.all(j.isfinite(d.qpos))&j.all(j.isfinite(d.qvel))&j.all(j.isfinite(d.act))
  state=(d.qpos,d.qvel,d.act,d.qacc_warmstart)
  return state,(d.qpos,overflow,finite,counts)
 def rollout(self,physical_u):
  steps=physical_u.shape[0]
  final,output=jax.lax.scan(jax.checkpoint(self.step),self.initial,(j.arange(steps),physical_u))
  return final,output
 def objective(self,physical_u):
  final,(q,overflow,finite,counts)=self.rollout(physical_u);loss=j.mean((q[:,self.joint_ids]-self.target[:len(physical_u)])**2)
  valid=j.all(finite)&~j.any(overflow)
  loss=j.where(valid,loss,j.nan)
  return loss,{'joint_q':q[:,self.joint_ids],'overflow':j.any(overflow),'finite':j.all(finite),'max_contacts':j.max(counts,axis=0)}
