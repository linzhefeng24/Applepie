"""Independent audits; reads frozen best16 replay, never edits training state.
Algebra audits validate exact smooth components. Physical finite perturbations
compare the native full400ms objective with its approximate white-box VJP.
"""
from pathlib import Path
import argparse,hashlib,io,json,sys,time,zipfile
import numpy as np
import jax
jax.config.update('jax_enable_x64',True)
import jax.numpy as j
R=Path(__file__).resolve().parent;ROOT=R.parents[1];SRC=ROOT/'research/joint-bptt-physical-bounds-20261117'
sys.path.insert(0,str(SRC))
from full_hh import FullDifferentiableHH

def dump(name,obj):(R/name).write_text(json.dumps(obj,indent=2)+'\n')
def algebra():
 m=FullDifferentiableHH();theta=j.asarray(json.loads((SRC/'initialization.json').read_text())['initial_log_multipliers']);rng=np.random.default_rng(42);d=j.asarray(rng.normal(size=theta.shape));d/=j.linalg.norm(d)
 reg=lambda t:10*j.mean(j.expm1(t)**2)
 g=jax.grad(reg)(theta);analytic=20*j.expm1(theta)*j.exp(theta)/theta.size
 fd=(reg(theta+1e-5*d)-reg(theta-1e-5*d))/2e-5;ad=j.sum(g*d)
 parameter_loss=lambda t:j.mean(m.parameters(t)[0][:,m.fields]**2)
 pg=jax.grad(parameter_loss)(theta);pfd=(parameter_loss(theta+1e-5*d)-parameter_loss(theta-1e-5*d))/2e-5;pad=j.sum(pg*d)
 _,pull=jax.vjp(m.state_clip,j.zeros(1));b1=np.asarray(pull(j.array([6.]))[0]);b2=np.asarray(pull(j.array([12.]))[0])
 # Same spike event, proposed surrogate slope versus actual local FD.
 threshold=float(m.model.aux[7]);old=j.array([threshold-1.]);new=j.array([threshold+.1]);_,spull=jax.vjp(lambda x:m.spike(old,x),new);sg=float(spull(j.ones(1))[0][0]);eps=1e-5;sfd=float(((m.spike(old,new+eps)-m.spike(old,new-eps))/(2*eps))[0])
 report={'source_revision':__import__('subprocess').check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'regularizer_max_gradient_error':float(j.max(j.abs(g-analytic))),'regularizer_directional_relative_error':float(abs(ad-fd)/max(abs(ad),abs(fd),1e-30)),'parameter_map_directional_relative_error':float(abs(pad-pfd)/max(abs(pad),abs(pfd),1e-30)),'state_clip_vjp_at_6':b1.tolist(),'state_clip_vjp_at_12':b2.tolist(),'state_clip_additivity_error':float(abs(b2-2*b1).max()),'state_clip_is_linear_vjp':bool(np.allclose(b2,2*b1)),'hard_spike_local_finite_difference':sfd,'surrogate_spike_gradient':sg,'manual_center_regularizer':float(reg(j.zeros_like(theta))),'conclusion':'Smooth parameter mapping and manual regularizer audited independently. Cotangent clipping violates VJP linearity; hard-spike surrogate is intentionally not exact hard-forward derivative. Full reverse is also200ms-truncated.'}
 assert report['regularizer_max_gradient_error']<1e-12 and report['parameter_map_directional_relative_error']<1e-6 and report['regularizer_directional_relative_error']<1e-6
 dump('algebra.json',report);print(json.dumps(report,indent=2),flush=True)
def physics(archive):
 from physics import ABPhysics
 from native_whitebox import NativeWhitebox
 with zipfile.ZipFile(archive) as z:
  report=json.loads(z.read('evaluation.json'))
  with np.load(io.BytesIO(z.read('BestUpdate16.npz')),allow_pickle=False) as a:u=a['physical_u']
 cfg=json.loads((SRC/'config.json').read_text());p=ABPhysics(cfg);b=NativeWhitebox(p)
 initial=tuple(np.asarray(x) for x in p.initial);target=np.asarray(p.target);ids=np.asarray(p.joint_ids)
 def native_value(control):
  state=initial;loss=0.
  for k,row in enumerate(control):
   state=b.native_step_numpy(state,k,row)[:4];loss+=np.sum((state[0][ids]-target[k])**2)/target.size
  return float(loss)
 print('Compiling full4000-step native physical VJP at best16',flush=True);start=time.monotonic();value,g=jax.jit(jax.value_and_grad(lambda x:b.objective(x)[0]))(j.asarray(u));value.block_until_ready();gradient=np.asarray(g)
 out={'steps':len(u),'physical_duration_s':len(u)*p.dt,'point':'best16 replay','archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'joint_mse':float(value),'expected_joint_mse':report['metrics']['BestUpdate16']['joint_mse_rad2'],'all_gradient_finite':bool(np.isfinite(gradient).all()),'gradient_norm':float(np.linalg.norm(gradient)),'gradient_seconds':time.monotonic()-start,'checks':[],'gradient_class':'native hard forward with piecewise analytic/implicit white-box VJP; not derivative through topology or stopping loops'}
 dump('physics-incomplete.json',out)
 assert out['all_gradient_finite'] and np.isclose(float(value),out['expected_joint_mse'],rtol=1e-9,atol=1e-11)
 rng=np.random.default_rng(42);mask=(u>.02)&(u<.98)
 directions=[('random0',rng.normal(size=u.shape)*mask),('random1',rng.normal(size=u.shape)*mask),('negative_gradient',-gradient*mask)]
 for name,d in directions:
  d/=max(abs(d).max(),1e-30);ad=float(np.sum(gradient*d))
  for eps in [1e-5,1e-4,1e-3]:
   plus=native_value(u+eps*d);minus=native_value(u-eps*d);fd=(plus-minus)/(2*eps)
   row={'direction':name,'epsilon':eps,'adjoint_projection':ad,'native_central_difference':fd,'relative_error':abs(ad-fd)/max(abs(ad),abs(fd),1e-20),'same_sign':bool(ad*fd>0),'loss_plus':plus,'loss_minus':minus,'plus_change':plus-float(value),'predicted_plus_change':eps*ad};out['checks'].append(row);dump('physics-incomplete.json',out);print(json.dumps(row),flush=True)
 out['max_relative_error']=max(x['relative_error'] for x in out['checks']);out['strict_5percent_all_passed']=bool(out['max_relative_error']<.05);out['seconds']=time.monotonic()-start
 dump('physics.json',out);(R/'physics-incomplete.json').unlink();np.savez_compressed(R/'cache-physics-gradient.npz',gradient=gradient,u=u)
 print(json.dumps(out,indent=2),flush=True)
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['algebra','physics']);parser.add_argument('--replay',type=Path);a=parser.parse_args()
 algebra() if a.mode=='algebra' else physics(a.replay)
