"""Resolve finite-rollout gradient noise versus contact-topology changes.
No parameter fitting or change to the original solver tolerance/iterations.
"""
from pathlib import Path
import hashlib,json,sys
import numpy as np
import mujoco
from physics_adjoint import NativeAdjoint
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'cache/model'));from simulation import Simulation
sim=Simulation(R/'cache/model/parameters.yaml')
with np.load(R/'gradient-check-20ms.npz',allow_pickle=False) as z:u=z['u'];target=z['target_q'];gradient=z['gradient']
engine=NativeAdjoint(sim,target,1e-6)
def trace(u):
 loss,states,controls,local=engine.rollout(u)
 signatures=[];iterations=[]
 for s,c in zip(states[:-1],controls):
  engine.step(s,c);d=engine.d;pairs=tuple(sorted(tuple(map(int,d.contact[k].geom)) for k in range(d.ncon)));signatures.append(pairs);iterations.append(int(d.solver_niter[0]))
 return loss,signatures,np.array(iterations)
base,contacts,it=trace(u);rng=np.random.default_rng(42);rows=[]
for k in range(3):
 v=rng.normal(size=u.shape);v/=np.linalg.norm(v);adj=float(np.sum(gradient*v))
 for eps in [.1,.03,.01,.003,.001,.0003,.0001,.00001]:
  p,pc,pi=trace(u+eps*v);n,nc,ni=trace(u-eps*v);fd=(p-n)/(2*eps)
  rows.append(dict(direction=k,epsilon=eps,adjoint=adj,finite_rollout_gradient=fd,relative_error=abs(adj-fd)/max(abs(adj),abs(fd),1e-30),contact_topology_samples_changed=sum(a!=b or a!=c for a,b,c in zip(contacts,pc,nc)),solver_iteration_samples_changed=int(np.count_nonzero((it!=pi)|(it!=ni)))))
# Inspect actual force equations on a work copy, preserving the physical rollout.
sim.reset('A')
for c in sim.load_ab('A')['controls'][:len(u)]:sim.data.ctrl[:]=c;mujoco.mj_step(sim.model,sim.data)
terms=sim.equation_terms();f=terms['muscle_force_formula_native'];native=terms['muscle_force_engine_native'];rhs=terms['qfrc_smooth_native']+terms['qfrc_constraint_native'];res=terms['dynamics_residual_native']
report=dict(command=sys.argv,source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),solver_changed=False,force_formula_max_abs_error=float(abs(f-native).max()),dynamics_residual_norm=float(np.linalg.norm(res)),dynamics_residual_relative=float(np.linalg.norm(res)/max(np.linalg.norm(rhs),1e-30)),diagnostic=rows,interpretation='Different perturbation scales probe solver/contact branch sensitivity; this does not prove all full-length gradients are correct.')
(R/'gradient-noise-diagnosis.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
