"""Exact original AB forward with a white-box implicit physical custom VJP.
No local finite-difference physics Jacobians. Native collision/contact forward
is never replaced by a different physical trajectory; gradients differentiate
muscle, kinematic/inertial/contact equations and must pass directional checks.
"""
import threading
import numpy as np
import jax
import jax.numpy as j
import mujoco
from mujoco.mjx._src import forward,smooth,constraint
from contact_geometry import attach
from implicit_solver import solve_at_native_acceleration

class NativeWhitebox:
 def __init__(self,physics):
  self.p=physics;self.sim=physics.native;self.m=self.sim.model;self.data=mujoco.MjData(self.m);self.lock=threading.RLock();self.controls=np.asarray(physics.controls);self.indices=np.asarray(physics.muscles);self.dims=sorted(set(physics.contact_dims));self.capacity=physics.cfg['contact_capacity_per_dim'];self.contact_slots=len(physics.contact_dims)
  shapes=(jax.ShapeDtypeStruct((self.m.nq,),j.float64),jax.ShapeDtypeStruct((self.m.nv,),j.float64),jax.ShapeDtypeStruct((self.m.na,),j.float64),jax.ShapeDtypeStruct((self.m.nv,),j.float64),jax.ShapeDtypeStruct((len(self.dims),),j.int32),jax.ShapeDtypeStruct((self.contact_slots,28),j.float64),jax.ShapeDtypeStruct((self.contact_slots,2),j.int32))
  def native_step(state,k,u):
   with self.lock:
    q,v,a,w=[np.asarray(x) for x in state];d=self.data;d.time=int(k)*self.m.opt.timestep;d.qpos[:]=q;d.qvel[:]=v;d.act[:]=a;d.qacc_warmstart[:]=w;d.ctrl[:]=self.controls[int(k)];d.ctrl[self.indices]=u;d.qfrc_applied[:]=0;d.xfrc_applied[:]=0
    mujoco.mj_step(self.m,d)
    if abs(d.time-(int(k)+1)*self.m.opt.timestep)>1e-9:raise RuntimeError('Native physics reset; update invalid')
    if not np.isfinite(d.qpos).all():raise FloatingPointError('Invalid native body state')
    counts=np.array([sum(int(c.dim)==dim for c in d.contact) for dim in self.dims],dtype=np.int32)
    if counts.max(initial=0)>=self.p.cfg['contact_capacity_per_dim']:raise RuntimeError('Contact capacity reached; update invalid')
    packed=np.zeros((self.contact_slots,28));geoms=np.zeros((self.contact_slots,2),dtype=np.int32);packed[:,0]=1e6;packed[:,4:13]=np.eye(3).reshape(9);packed[:,13:18]=[1,1,.005,.0001,.0001];packed[:,18:22]=[.02,1,.02,1];packed[:,22:27]=[.9,.95,.001,.5,2]
    for jdim,dim in enumerate(self.dims):
     row=jdim*self.capacity
     for c in d.contact:
      if int(c.dim)!=dim or c.exclude>1:continue
      geoms[row]=c.geom;packed[row]=np.r_[c.dist,c.pos,c.frame,c.friction,c.solref,c.solreffriction,c.solimp,c.includemargin];row+=1
    return (d.qpos.copy(),d.qvel.copy(),d.act.copy(),d.qacc_warmstart.copy(),counts,packed,geoms)
  self.native_step_numpy=native_step
  @jax.custom_vjp
  def step(state,k,u):return jax.pure_callback(native_step,shapes,state,k,u)
  def fwd(state,k,u):
   result=jax.pure_callback(native_step,shapes,state,k,u)
   return result,(state,k,u,result[3],result[5],result[6])
  def bwd(residual,bar):
   state,k,u,native_acceleration,contacts,geoms=residual
   _,pullback=jax.vjp(lambda s,control:self.whitebox_transition(s,k,control,native_acceleration,contacts,geoms),state,u)
   bs,bu=pullback(bar[:4])
   return bs,None,bu
  step.defvjp(fwd,bwd);self.step=step
 def whitebox_data(self,state,k,u,native_acceleration,contacts,geoms):
  q,v,a,w=state;p=self.p;d=p.template.replace(time=k*p.dt,qpos=q,qvel=v,act=a,qacc_warmstart=w,ctrl=p.controls[k].at[p.muscles].set(u))
  d=smooth.kinematics(p.m,d);d=smooth.com_pos(p.m,d);d=smooth.tendon(p.m,d);d=smooth.crb(p.m,d);d=smooth.factor_m(p.m,d)
  d=attach(p.m,d,jax.lax.stop_gradient(contacts),jax.lax.stop_gradient(geoms));d=constraint.make_constraint(p.m,d);d=smooth.transmission(p.m,d)
  d=forward.fwd_velocity(p.m,d);d=forward.fwd_actuation(p.m,d);d=forward.fwd_acceleration(p.m,d)
  d=solve_at_native_acceleration(p.m,d,jax.lax.stop_gradient(native_acceleration))
  return d
 def whitebox_transition(self,state,k,u,native_acceleration,contacts,geoms):
  p=self.p;d=self.whitebox_data(state,k,u,native_acceleration,contacts,geoms)
  d=forward.euler(p.m,d)
  g1,g2=d.contact.geom[:,0],d.contact.geom[:,1];gap=j.maximum(p.m.geom_gap[g1],p.m.geom_gap[g2]);valid=d.contact.dist<d.contact.includemargin+gap
  overflow=j.any(j.stack([j.sum(valid*(p.contact_dims==dim)) for dim in self.dims])>=p.cfg['contact_capacity_per_dim'])
  return tuple(j.where(overflow,j.nan,x) for x in (d.qpos,d.qvel,d.act,d.qacc_warmstart))
 def rollout(self,u):
  def body(state,inputs):
   k,row=inputs;result=self.step(state,k,row);state=result[:4]
   return state,(state[0],result[4])
  return jax.lax.scan(jax.checkpoint(body),self.p.initial,(j.arange(len(u)),u))
 def objective(self,u):
  state,(q,counts)=self.rollout(u);loss=j.mean((q[:,self.p.joint_ids]-self.p.target[:len(u)])**2)
  return loss,{'joint_q':q[:,self.p.joint_ids],'overflow':j.asarray(False),'finite':j.all(j.isfinite(q)),'max_contacts':j.max(counts,axis=0)}
