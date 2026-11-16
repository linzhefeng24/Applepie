"""Implicit derivative of the original converged MJX contact equations.
Forward uses the unchanged native-budget/tolerance Newton stopping loop. The
backward differentiates stationarity M*a-f_smooth-f_constraint(a)=0, rather
than the numerical decision to stop an iterative solver. Accuracy is checked
against residuals and finite physical perturbations, including friction cones.
"""
import jax
import jax.numpy as j
from mujoco.mjx._src import solver,support
_original_solve=solver.solve

def solve(m,d):
 def residual(acceleration):
  state=d.replace(qacc=acceleration)
  ctx=solver.Context.create(m,state,grad=False)
  return support.mul_m(m,d,acceleration)-d.qfrc_smooth-ctx.qfrc_constraint
 def solve_root(unused_f,guess):
  result=_original_solve(m,d.replace(qacc_warmstart=guess))
  return result.qacc,result.solver_niter.astype(j.float64)
 def tangent_solve(operator,rhs):
  matrix=jax.vmap(operator)(j.eye(m.nv,dtype=rhs.dtype)).T
  return j.linalg.solve(matrix,rhs)
 acceleration,niter=jax.lax.custom_root(residual,d.qacc_warmstart,solve_root,tangent_solve,has_aux=True)
 ctx=solver.Context.create(m,d.replace(qacc=acceleration),grad=False)
 return d.replace(qacc_warmstart=acceleration,qacc=acceleration,qfrc_constraint=ctx.qfrc_constraint,efc_force=ctx.efc_force,solver_niter=niter.astype(d.solver_niter.dtype))

def install():
 if solver.solve is not solve:solver.solve=solve
