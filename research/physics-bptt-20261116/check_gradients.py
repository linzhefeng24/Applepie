"""Short joint-loss BPTT reference check and native-vs-AD muscle parity.
This tests derivative correctness, not a trained neural candidate or gait.
"""
from pathlib import Path
import hashlib,io,json,platform,sys,time,zipfile
import numpy as np
import jax
jax.config.update('jax_enable_x64',True)
import jax.numpy as j
import mujoco
from mujoco.mjx._src import support
from physics_adjoint import NativeAdjoint,jax_loss
R=Path(__file__).resolve().parent;ROOT=R.parents[1];cfg=json.loads((R/'config.json').read_text());cache=R/'cache/model';cache.mkdir(parents=True,exist_ok=True)
archive=ROOT/cfg['model_archive'];assert hashlib.sha256(archive.read_bytes()).hexdigest()==cfg['model_archive_sha256']
with zipfile.ZipFile(archive) as z:
 for n in ['parameters.yaml','simulation.py']:(cache/n).write_bytes(z.read(n))
sys.path.insert(0,str(cache));from simulation import Simulation,_table
sim=Simulation(cache/'parameters.yaml');m=sim.model;T=cfg['pilot_physics_steps'];reference=_table(sim.config['reference']['joint_angles']);sample_dt=m.opt.timestep*sim.load_ab('A')['sample_stride'];target=np.stack([np.interp(np.arange(1,T+1)*m.opt.timestep,np.arange(len(reference))*sample_dt,reference[:,k]) for k in range(reference.shape[1])],axis=1)
# Interior controls isolate smooth gradient checks from actuator clipping edges.
u=.1+.8*sim.load_ab('A')['controls'][:T,sim.muscle_indices];engine=NativeAdjoint(sim,target,cfg['jacobian_epsilon']);start=time.perf_counter();value,grad=engine.value_and_grad(u);seconds=time.perf_counter()-start
print('adjoint',float(value),'grad norm',float(np.linalg.norm(grad)),'seconds',seconds,flush=True)
rng=np.random.default_rng(42);checks=[]
for seed in range(3):
 direction=rng.normal(size=u.shape);direction/=np.linalg.norm(direction);adj=float(np.sum(grad*direction))
 for eps in cfg['directional_epsilon']:
  fd=(engine.value(u+eps*direction)-engine.value(u-eps*direction))/(2*eps);checks.append(dict(direction=seed,epsilon=eps,adjoint=adj,full_rollout_difference=fd,absolute_error=abs(adj-fd),relative_error=abs(adj-fd)/max(abs(adj),abs(fd),1e-20)))
# True automatic differentiation of the native muscle formulas, checked separately.
muscles=[]
for i in sim.muscle_indices[::13]:
 length=float(m.actuator_lengthrange[i].mean());vel=.001;act=.35;ctrl=.6;lr=j.asarray(m.actuator_lengthrange[i]);acc=j.asarray(m.actuator_acc0[i]);gp=j.asarray(m.actuator_gainprm[i,:9]);bp=j.asarray(m.actuator_biasprm[i,:9]);dp=j.asarray(m.actuator_dynprm[i,:3])
 def force(x):return support.muscle_gain(x[0],x[1],lr,acc,gp)*x[2]+support.muscle_bias(x[0],lr,acc,bp)
 x=j.array([length,vel,act]);f=float(force(x));native=float(mujoco.mju_muscleGain(length,vel,np.asarray(lr),float(acc),np.asarray(gp))*act+mujoco.mju_muscleBias(length,np.asarray(lr),float(acc),np.asarray(bp)));ad=np.asarray(jax.grad(force)(x));fd=[]
 for k in range(3):
  xx=np.asarray(x).copy();xx[k]+=1e-6;yy=np.asarray(x).copy();yy[k]-=1e-6;fd.append((float(force(j.asarray(xx)))-float(force(j.asarray(yy))))/2e-6)
 adot=float(support.muscle_dynamics(j.asarray(ctrl),j.asarray(act),dp));native_adot=float(mujoco.mju_muscleDynamics(ctrl,act,np.asarray(dp)))
 muscles.append(dict(actuator=int(i),force_error=abs(f-native),activation_derivative_error=abs(adot-native_adot),force_gradient_max_error=float(abs(ad-np.asarray(fd)).max())))
# Check the actual JAX custom-VJP composition using one scalar input perturbation.
pattern=rng.normal(size=u.shape);pattern/=np.linalg.norm(pattern);physics=jax_loss(engine)
loss,g=jax.value_and_grad(lambda p:physics(j.asarray(u)+p*j.asarray(pattern)))(j.asarray(0.));jax_expected=float(np.sum(grad*pattern));assert np.isfinite(g)
# One bounded direction step uses joint loss only; retain incomplete/failed results.
scaled=grad/max(float(np.max(abs(grad))),1e-30);trials=[]
for rate in [.02,.01,.005]:
 trial=np.clip(u-rate*scaled,0,1);loss_new=engine.value(trial);trials.append(dict(step_size=rate,joint_loss=loss_new,improved=loss_new<float(value)))
report=dict(command=sys.argv,python=platform.python_version(),versions={'numpy':np.__version__,'mujoco':mujoco.__version__,'jax':jax.__version__},seed=42,model_archive_sha256=cfg['model_archive_sha256'],config=cfg,physical_horizon_s=T*m.opt.timestep,reference_joint_count=target.shape[1],state_tangent_dimensions=engine.n,jacobian_evaluation_seconds=seconds,joint_loss=float(value),gradient_norm=float(np.linalg.norm(grad)),directional_checks=checks,muscle_analytic_AD_checks=muscles,jax_custom_vjp_gradient=float(g),jax_expected_gradient=jax_expected,jax_callback_max_error=abs(float(g)-jax_expected),joint_loss_direction_steps=trials,source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),R/'physics_adjoint.py']},scope='new short component test; interior controls derived from A, not epoch123/1000 training; local physics Jacobians are finite differences, not fully analytic')
(R/'gradient-report.json').write_text(json.dumps(report,indent=2)+'\n');np.savez_compressed(R/'gradient-check.npz',u=u,target_q=target,gradient=grad)
print(json.dumps(report,indent=2),flush=True)
assert max(x['relative_error'] for x in checks)<.05,'Gradient check failed; do not train until resolved'
assert max(x['force_error'] for x in muscles)<1e-9
assert max(x['activation_derivative_error'] for x in muscles)<1e-9
assert abs(float(g)-jax_expected)<1e-12
assert any(x['improved'] for x in trials)
