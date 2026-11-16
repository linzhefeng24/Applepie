"""Native-forward identity, analytic force and implicit joint-gradient gates."""
from pathlib import Path
import argparse,hashlib,json,time,sys
import numpy as np
import jax
jax.config.update('jax_enable_x64',True)
import jax.numpy as j
from physics import ABPhysics
from native_whitebox import NativeWhitebox
R=Path(__file__).resolve().parent
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--steps',type=int,default=10);p.add_argument('--force-only',action='store_true');a=p.parse_args()
jax.config.update('jax_compilation_cache_dir',str(R/'cache/jax-whitebox'));jax.config.update('jax_persistent_cache_min_compile_time_secs',0)
cfg=json.loads((R/'config.json').read_text());physics=ABPhysics(cfg);body=NativeWhitebox(physics);native=physics.native
initial=tuple(np.asarray(x) for x in physics.initial);control=np.asarray(physics.controls[0,physics.muscles]);result=body.native_step_numpy(initial,0,control)
print('Compile exact-contact force audit',flush=True);start=time.monotonic()
def force_fields(state,u,acc,contacts,geoms):
 d=body.whitebox_data(state,0,u,acc,contacts,geoms)
 return d.actuator_force,d.qfrc_actuator,d.qfrc_constraint,d.qfrc_passive,d.qacc
fields=jax.jit(force_fields)(physics.initial,j.asarray(control),j.asarray(result[3]),j.asarray(result[5]),j.asarray(result[6]));jax.block_until_ready(fields)
force={key:float(abs(np.asarray(x)-getattr(body.data,key)).max()) for key,x in zip(['actuator_force','qfrc_actuator','qfrc_constraint','qfrc_passive','qacc'],fields)}
report={'command':sys.argv,'steps':a.steps,'force_max_abs_errors':force,'force_audit_seconds':time.monotonic()-start,'source_sha256':{name:hashlib.sha256((R/name).read_bytes()).hexdigest() for name in ['native_whitebox.py','contact_geometry.py','implicit_solver.py','physics.py']},'versions':{'jax':jax.__version__,'numpy':np.__version__},'training_allowed':False}
(R/f'whitebox-validation-{a.steps}.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
if a.force_only:sys.exit(0)
# Interior controls for directional derivative checks, with exact original auxiliaries.
u=.1+.8*np.asarray(physics.controls[:a.steps,physics.muscles]);value_grad=jax.jit(jax.value_and_grad(lambda x:body.objective(x)[0]));print('Compile/compute analytic joint VJP',flush=True);start=time.monotonic();value,gradient=value_grad(j.asarray(u));value.block_until_ready();gradient=np.asarray(gradient)
report.update(joint_loss=float(value),gradient_norm=float(np.linalg.norm(gradient)),gradient_seconds=time.monotonic()-start,all_gradients_finite=bool(np.isfinite(gradient).all()))
print('gradient',report['joint_loss'],report['gradient_norm'],report['gradient_seconds'],flush=True)
np.savez_compressed(R/'cache'/f'whitebox-gradient-{a.steps}.npz',u=u,gradient=gradient,target=np.asarray(physics.target[:a.steps]))
def native_value(controls):
 state=initial;loss=0.;target=np.asarray(physics.target[:len(controls)]);jq=np.asarray(physics.joint_ids)
 for k,row in enumerate(controls):state=body.native_step_numpy(state,k,row)[:4];loss+=np.sum((state[0][jq]-target[k])**2)/target.size
 return loss
checks=[];rng=np.random.default_rng(42)
for d in range(3):
 direction=rng.normal(size=u.shape);direction/=abs(direction).max();ad=float(np.sum(gradient*direction))
 for eps in [.001,.003]:
  fd=float((native_value(u+eps*direction)-native_value(u-eps*direction))/(2*eps));checks.append({'direction':d,'epsilon':eps,'adjoint':ad,'native_finite_difference':fd,'relative_error':abs(ad-fd)/max(abs(ad),abs(fd),1e-20)})
report['directional_checks']=checks;report['max_directional_relative_error']=float(max(x['relative_error'] for x in checks));report['gradient_gate_passed']=bool(report['all_gradients_finite'] and report['max_directional_relative_error']<.05)
(R/f'whitebox-validation-{a.steps}.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2),flush=True)
assert report['gradient_gate_passed'],'No joint updates before the physical gradient gate passes'
