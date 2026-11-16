"""Differentiable native5-sweep NoSlip for the exact AB elliptic condim3 case.
Faithful to engine_solver.c:mj_solNoSlip and engine_util_solve.c:mju_QCQP2.
All original AB dry-friction coefficients are0; scalar normal/limit forces stay
fixed, while each tangential2D block is solved serially in native contact order.
"""
import jax
import jax.numpy as j
import numpy as np
from mujoco.mjx._src import smooth


def qcqp2(matrix,linear,friction,radius):
 a=matrix*j.outer(friction,friction);b=linear*friction
 def iteration(state,_):
  lam,v,done,spd=state
  def update(unused):
   aa=a[0,0]+lam;bb=a[1,1]+lam;ab=a[0,1];det=aa*bb-ab*ab;valid=det>=1e-10;den=j.maximum(det,1e-30)
   inverse=j.array([[bb,-ab],[-ab,aa]])/den;newv=-(inverse@b);newv=j.where(valid,newv,0.)
   val=j.dot(newv,newv)-radius**2;deriv=-2*j.dot(newv,inverse@newv);delta=-val/j.minimum(deriv,-1e-30)
   stop=(val<1e-10)|(delta<1e-10)|~valid
   return (lam+j.where(stop,0.,delta),newv,stop,spd&valid)
  return jax.lax.cond(done,lambda unused:state,update,None),None
 (lam,v,done,spd),_=jax.lax.scan(iteration,(j.asarray(0.,matrix.dtype),j.zeros(2,matrix.dtype),j.asarray(False),j.asarray(True)),None,length=20)
 v=v*friction;active=(lam!=0)&spd
 norm=j.sum((v/j.maximum(friction,1e-15))**2);scale=j.sqrt(radius**2/j.maximum(norm,1e-15));v=j.where(active,v*scale,v)
 return j.where(spd,v,0.)


def apply(m,d,iterations=5,tolerance=0.):
 if iterations==0:return d
 assert not m.dof_hasfrictionloss.any() and not m.tendon_hasfrictionloss.any()
 slots=np.flatnonzero(d.contact.dim==3);addresses=d.contact.efc_address[slots];ad=j.asarray(addresses)
 tangent=ad[:,None]+j.array([1,2]);jac=d.efc_J[tangent]
 inv_jac=jax.vmap(lambda rhs:smooth.solve_m(m,d,rhs))(jac.reshape((-1,m.nv))).reshape((-1,2,m.nv))
 blocks=j.einsum('cin,cjn->cij',jac,inv_jac);diag=j.maximum(j.diagonal(blocks,axis1=1,axis2=2),1e-10);blocks=blocks.at[:,0,0].set(diag[:,0]).at[:,1,1].set(diag[:,1])
 mu=d.contact.friction[slots,:2];force=d.efc_force;acc=d.qacc_smooth+smooth.solve_m(m,d,d.efc_J.T@force)
 def one_sweep(state,index):
  force,acc,stopped=state
  def sweep(unused):
   initial_improvement=j.where(index==0,.5*j.sum(force**2/j.maximum(d.efc_D,1e-30)),0.)
   def block(carry,inputs):
    current,acc,improvement=carry;addr,rows,inv_rows,matrix,friction=inputs;old=jax.lax.dynamic_slice(current,(addr+1,),(2,));res=rows@acc-d.efc_aref[addr+j.array([1,2])];b=res-matrix@old;normal=current[addr]
    def solve(unused):return qcqp2(matrix,b,friction,normal)
    new=jax.lax.cond(normal<1e-15,lambda unused:j.zeros(2),solve,None);change=new-old
    current=current.at[addr+j.array([1,2])].set(new);acc=acc+inv_rows.T@change;improvement-=.5*j.dot(change,matrix@change)+j.dot(change,res)
    return (current,acc,improvement),None
   (new_force,new_acc,improvement),_=jax.lax.scan(block,(force,acc,initial_improvement),(ad,jac,inv_jac,blocks,mu))
   stop=improvement/(m.stat.meaninertia*max(1,m.nv))<tolerance
   return new_force,new_acc,stop
  return jax.lax.cond(stopped,lambda unused:state,sweep,None),None
 (force,acc,stopped),_=jax.lax.scan(one_sweep,(force,acc,j.asarray(False)),j.arange(iterations))
 qconstraint=d.efc_J.T@force;acc=d.qacc_smooth+smooth.solve_m(m,d,qconstraint)
 # Keep qacc_warmstart at the PRE-NoSlip solution, exactly as the native engine.
 return d.replace(efc_force=force,qfrc_constraint=qconstraint,qacc=acc)
