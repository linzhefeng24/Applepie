"""Finite native joint-loss perturbations along the actual surrogate direction.
Recover g at best16 from consecutive Adam moment states16/17. This is an
independent forward intervention, not another claim of exact spike derivatives.
"""
from pathlib import Path
import argparse,hashlib,io,json,sys,time,zipfile
import numpy as np
import jax
jax.config.update('jax_enable_x64',True)
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R.parents[1]/'research/joint-bptt-physical-bounds-20261117'))
from training_context import JointContext
p=argparse.ArgumentParser();p.add_argument('before',type=Path);p.add_argument('after',type=Path);a=p.parse_args();banks=[];history=[]
for path in [a.before,a.after]:
 with zipfile.ZipFile(path) as z:
  history=json.loads(z.read('history.json'))
  with np.load(io.BytesIO(z.read('optimizer.npz')),allow_pickle=False) as f:banks.append({k:f[k] for k in f.files})
before,after=banks;assert int(before['completed_updates'])==16 and int(after['completed_updates'])==17
row=history[-1];assert row['evaluated_parameter_updates']==16
clipped=(after['adam_m']-.9*before['adam_m'])/.1;g=clipped*max(1.,row['gradient_norm']);theta=before['raw'];direction=-g/max(abs(g).max(),1e-30)
ctx=JointContext();forward=jax.jit(ctx.neural_u);phys=ctx.physics;body=ctx.native_physics;initial=tuple(np.asarray(x) for x in phys.initial);target=np.asarray(phys.target);ids=np.asarray(phys.joint_ids)
def evaluate(raw):
 u=forward(raw);u.block_until_ready();controls=np.asarray(u[phys.clock_indices][:,ctx.order]);state=initial;loss=0.
 for k,control in enumerate(controls):
  state=body.native_step_numpy(state,k,control)[:4];loss+=np.sum((state[0][ids]-target[k])**2)/target.size
 reg=10*np.mean(np.expm1(raw)**2)
 return {'joint_mse':float(loss),'regularization':float(reg),'total':float(loss+reg)}
report={'point':'best16','coefficient':10,'parameter_direction':'negative actual clipped-backward surrogate direction at16, before Adam momentum','predicted_total_directional_derivative':float(np.sum(g*direction)),'source_archives':[{'name':f.name,'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'bytes':f.stat().st_size} for f in [a.before,a.after]],'checks':[],'comparison_caveat':'Hard spike finite differences need not match a surrogate with temporal truncation and nonlinear cotangent clipping. Direct descent or ascent is measured rather than assumed.'}
def save(name):(R/name).write_text(json.dumps(report,indent=2)+'\n')
start=time.monotonic();base=evaluate(theta);report['baseline']=base;assert np.isclose(base['joint_mse'],row['joint_mse_before_update'],rtol=1e-8,atol=1e-10);save('end-to-end-incomplete.json');print('BASE',json.dumps(base),flush=True)
for eps in [1e-4,1e-3]:
 plus=evaluate(theta+eps*direction);minus=evaluate(theta-eps*direction);fd=(plus['total']-minus['total'])/(2*eps)
 result={'epsilon':eps,'negative_gradient_direction_point':plus,'opposite_direction_point':minus,'negative_direction_total_change':plus['total']-base['total'],'negative_direction_joint_change':plus['joint_mse']-base['joint_mse'],'central_finite_difference_total':fd,'same_sign_as_surrogate_projection':bool(fd*report['predicted_total_directional_derivative']>0)};report['checks'].append(result);save('end-to-end-incomplete.json');print(json.dumps(result),flush=True)
report['seconds']=time.monotonic()-start;save('end-to-end.json');(R/'end-to-end-incomplete.json').unlink()
