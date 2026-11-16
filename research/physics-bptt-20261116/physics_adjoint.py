"""Native MuJoCo discrete adjoint, including solver warmstart in Markov state.
Forward is the unchanged AB engine. Local Jacobians use CENTRAL FINITE
DIFFERENCES, not analytic or MJX derivatives. This is a reference/gradient-check
backend, not an efficient full-horizon training backend and not claimed fully
white-box automatic differentiation. See source audit for exact force chain.
"""
from dataclasses import dataclass
import numpy as np
import mujoco

@dataclass
class State:
 q:np.ndarray
 v:np.ndarray
 a:np.ndarray
 warm:np.ndarray
 time:float

class NativeAdjoint:
 def __init__(self,sim,target_q,epsilon=1e-6):
  self.sim=sim;self.m=sim.model;self.d=mujoco.MjData(self.m);self.nv=self.m.nv;self.na=self.m.na;self.n=3*self.nv+self.na;self.eps=epsilon
  self.archive=sim.load_ab('A');self.target=np.asarray(target_q);self.jq=np.asarray(sim.config['reference']['joint_qpos_indices']);self.jd=[]
  for q in self.jq:
   joint=np.flatnonzero(self.m.jnt_qposadr==q);assert len(joint)==1;self.jd.append(int(self.m.jnt_dofadr[joint[0]]))
  sim.reset('A');self.initial=self.read(sim.data)
 def read(self,d):return State(d.qpos.copy(),d.qvel.copy(),d.act.copy(),d.qacc_warmstart.copy(),float(d.time))
 def step(self,s,control):
  d=self.d;d.time=s.time;d.qpos[:]=s.q;d.qvel[:]=s.v;d.act[:]=s.a;d.qacc_warmstart[:]=s.warm;d.ctrl[:]=control;d.qfrc_applied[:]=0;d.xfrc_applied[:]=0
  mujoco.mj_step(self.m,d);assert abs(d.time-s.time-self.m.opt.timestep)<1e-10
  return self.read(d)
 def perturb(self,s,k,amount):
  p=State(s.q.copy(),s.v.copy(),s.a.copy(),s.warm.copy(),s.time);v=self.nv
  if k<v:
   tangent=np.zeros(v);tangent[k]=amount;mujoco.mj_integratePos(self.m,p.q,tangent,1.)
  elif k<2*v:p.v[k-v]+=amount
  elif k<2*v+self.na:p.a[k-2*v]+=amount
  else:p.warm[k-2*v-self.na]+=amount
  return p
 def difference(self,p,n,denom):
  q=np.empty(self.nv);mujoco.mj_differentiatePos(self.m,q,denom,n.q,p.q)
  return np.r_[q,(p.v-n.v)/denom,(p.a-n.a)/denom,(p.warm-n.warm)/denom]
 def linearize(self,s,control):
  e=self.eps;A=np.empty((self.n,self.n));B=np.empty((self.n,len(self.sim.muscle_indices)))
  for k in range(self.n):A[:,k]=self.difference(self.step(self.perturb(s,k,e),control),self.step(self.perturb(s,k,-e),control),2*e)
  for j,k in enumerate(self.sim.muscle_indices):
   p=control.copy();n=control.copy();p[k]+=e;n[k]-=e;B[:,j]=self.difference(self.step(s,p),self.step(s,n),2*e)
  return A,B
 def rollout(self,u):
  u=np.asarray(u);assert u.shape==self.target.shape[:1]+(len(self.sim.muscle_indices),);states=[self.initial];controls=[];loss=0.;local=[]
  for k,row in enumerate(u):
   c=self.archive['controls'][k].copy();c[self.sim.muscle_indices]=row;s=self.step(states[-1],c);states.append(s);controls.append(c);error=s.q[self.jq]-self.target[k];loss+=np.sum(error**2)/self.target.size;g=np.zeros(self.n);g[self.jd]=2*error/self.target.size;local.append(g)
  return float(loss),states,controls,local
 def value(self,u):return self.rollout(u)[0]
 def value_and_grad(self,u):
  loss,states,controls,local=self.rollout(u);adj=np.zeros(self.n);gu=np.empty_like(u,dtype=float)
  for k in range(len(u)-1,-1,-1):
   A,B=self.linearize(states[k],controls[k]);adj+=local[k];gu[k]=B.T@adj;adj=A.T@adj
  return np.asarray(loss,np.float64),gu

def jax_loss(engine):
 """Compose with existing HH surrogate BPTT via loss(neural_u[clock_indices])."""
 import jax
 import jax.numpy as j
 @jax.custom_vjp
 def loss(u):return jax.pure_callback(lambda x:np.asarray(engine.value(x),np.float64),jax.ShapeDtypeStruct((),j.float64),u)
 def fwd(u):
  value,grad=jax.pure_callback(engine.value_and_grad,(jax.ShapeDtypeStruct((),j.float64),jax.ShapeDtypeStruct(u.shape,j.float64)),u)
  return value,grad
 def bwd(grad,g):return (grad*g,)
 loss.defvjp(fwd,bwd)
 return loss
