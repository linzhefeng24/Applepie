"""Locate first-step performance/force differences without changing AB physics."""
from pathlib import Path
import sys,time,json
import numpy as np
import mujoco
from mujoco.mjx._src import support
import jax
jax.config.update('jax_enable_x64',True)
import jax.numpy as j
from mujoco import mjx
from mujoco.mjx._src import smooth,collision_driver,constraint,forward,solver
R=Path(__file__).resolve().parent;ROOT=R.parents[1];sys.path.insert(0,str(ROOT/'research/restore-native-AB-20261116/cache'));from simulation import Simulation
sim=Simulation(ROOT/'research/restore-native-AB-20261116/cache/parameters.yaml');m=mjx.put_model(sim.model);d=mjx.make_data(m);d=d.replace(qpos=j.asarray(sim.data.qpos),qvel=j.asarray(sim.data.qvel),act=j.asarray(sim.data.act),qacc_warmstart=j.asarray(sim.data.qacc_warmstart),ctrl=j.asarray(sim.load_ab('A')['controls'][0]))
native=mujoco.MjData(sim.model);mujoco.mj_setState(sim.model,native,sim.load_ab('A')['initial_state'],mujoco.mjtState.mjSTATE_FULLPHYSICS);native.qacc_warmstart[:]=sim.load_ab('A')['initial_warmstart'];native.ctrl[:]=sim.load_ab('A')['controls'][0];mujoco.mj_forward(sim.model,native)
jax.config.update('jax_compilation_cache_dir',str(R/'cache/jax-cache'))
jax.config.update('jax_persistent_cache_min_compile_time_secs',0)
rows=[];detail={}
for fn in [smooth.kinematics,smooth.com_pos,smooth.camlight,smooth.tendon,smooth.crb,smooth.factor_m,collision_driver.collision,constraint.make_constraint,smooth.transmission,forward.fwd_velocity,forward.fwd_actuation,forward.fwd_acceleration,solver.solve,forward.euler]:
 print('START',fn.__module__,fn.__name__,flush=True);a=time.time();d=jax.jit(fn)(m,d);jax.block_until_ready(d);row={'stage':fn.__name__,'seconds':time.time()-a};rows.append(row);print(json.dumps(row),flush=True)
 if fn.__name__=='factor_m':
  nm=np.empty((sim.model.nv,sim.model.nv));mujoco.mj_fullM(sim.model,nm,native.qM);detail['mass_max_difference']=float(abs(nm-np.asarray(support.full_m(m,d))).max())
 if fn.__name__=='collision':
  c=d.contact;valid=np.asarray(c.dist)<np.asarray(c.includemargin)+np.maximum(np.asarray(m.geom_gap)[np.asarray(c.geom[:,0])],np.asarray(m.geom_gap)[np.asarray(c.geom[:,1])]);detail['native_contacts']=[dict(geom=list(map(int,x.geom)),dist=float(x.dist),exclude=int(x.exclude)) for x in native.contact];detail['mjx_contacts']=[dict(geom=list(map(int,np.asarray(c.geom)[k])),dist=float(np.asarray(c.dist)[k]),dim=int(c.dim[k])) for k in np.flatnonzero(valid)]
 if fn.__name__ in ['fwd_velocity','fwd_actuation','fwd_acceleration','solve']:
  for key in ['qfrc_bias','qfrc_passive','qfrc_actuator','qacc_smooth','qacc','qfrc_constraint']:
   if hasattr(d,key):detail[fn.__name__+'_'+key+'_max_difference']=float(abs(np.asarray(getattr(d,key))-getattr(native,key)).max())
 if fn.__name__=='make_constraint':
  pairs=[]
  for nc in native.contact:
   if nc.efc_address<0:continue
   slots=[i for i,p in enumerate(np.asarray(d.contact.geom)) if tuple(p)==tuple(nc.geom)]
   if not slots:continue
   slot=min(slots,key=lambda i:abs(float(d.contact.dist[i])-nc.dist));aa=int(nc.efc_address);bb=int(d.contact.efc_address[slot]);dim=int(nc.dim);nj=native.efc_J.reshape(native.nefc,sim.model.nv) if native.efc_J.size==native.nefc*sim.model.nv else None
   nativeJ=np.zeros((native.nefc,sim.model.nv))
   if nj is not None:nativeJ[:]=nj
   else:mujoco.mju_sparse2dense(nativeJ,native.efc_J,native.efc_J_rownnz,native.efc_J_rowadr,native.efc_J_colind)
   pairs.append({'geom':list(map(int,nc.geom)),'frame_max_diff':float(abs(nc.frame.reshape(3,3)-np.asarray(d.contact.frame)[slot]).max()),'jac_max_diff':float(abs(nativeJ[aa:aa+dim]-np.asarray(d.efc_J)[bb:bb+dim]).max()),'nativeD':native.efc_D[aa:aa+dim].tolist(),'mjxD':np.asarray(d.efc_D)[bb:bb+dim].tolist(),'native_aref':native.efc_aref[aa:aa+dim].tolist(),'mjx_aref':np.asarray(d.efc_aref)[bb:bb+dim].tolist()})
  detail['contact_constraint_parity']=pairs
 if fn.__name__=='solve':
  err=abs(np.asarray(d.qacc)-native.qacc);detail['worst_acc_dofs']=[dict(dof=int(k),joint=sim.model.joint(int(sim.model.dof_jntid[k])).name,native=float(native.qacc[k]),mjx=float(np.asarray(d.qacc)[k])) for k in np.argsort(err)[-10:]];detail['solver_iterations']={'native':native.solver_niter.tolist(),'mjx':int(d.solver_niter)}
 (R/'force-audit.json').write_text(json.dumps(detail,indent=2)+'\n')
(R/'stage-probe.json').write_text(json.dumps(rows,indent=2)+'\n')
