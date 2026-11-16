"""Full0.4s joint-loss optimizer, persistent Adam and explicit actual-update count.
Pilot coefficient runs are independent and never count toward the main300.
Each saved state has optimizer moments, exact neural raw factors and inputs IDs.
"""
from pathlib import Path
import argparse,hashlib,json,os,platform,subprocess,sys,time
from importlib.metadata import version
import numpy as np
import jax
jax.config.update('jax_enable_x64',True)
import jax.numpy as j
from training_context import JointContext
R=Path(__file__).resolve().parent;OUT=R/'cache/train';OUT.mkdir(parents=True,exist_ok=True)

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,obj):p.write_text(json.dumps(obj,indent=2)+'\n')
def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--updates',type=int,default=10);a=parser.parse_args();ctx=JointContext();cfg=ctx.cfg
 validation=R/'validation-report.json'
 if not validation.exists() or not json.loads(validation.read_text()).get('training_allowed',False):raise RuntimeError('Physics/gradient parity gate has not passed; zero updates counted')
 for name,digest in json.loads(validation.read_text())['critical_source_sha256'].items():assert sha(R/name)==digest,'Unvalidated source: '+name
 source=os.environ.get('TRAIN_SOURCE_REF',subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip())
 identity={'source_revision':source,'body_archive_sha256':cfg['body_archive_sha256'],'manual_anchor_model_sha256':cfg['anchor_model_sha256'],'reference_raw_sha256':hashlib.sha256(np.asarray(ctx.reference).tobytes()).hexdigest(),'config_sha256':sha(R/'config.json'),'neural_config_sha256':sha(R/'neural-config.json'),'physics_validation_sha256':sha(validation),'python':platform.python_version(),'versions':{n:version(n) for n in ['numpy','jax','jaxlib','mujoco','mujoco-mjx']},'seed':cfg['seed'],'command':sys.argv}
 state_path=OUT/'optimizer.npz';history_path=OUT/'history.json';history=json.loads(history_path.read_text()) if history_path.exists() else []
 if state_path.exists():
  previous=json.loads((OUT/'run-identity.json').read_text())
  for key in ['source_revision','config_sha256','neural_config_sha256','physics_validation_sha256','reference_raw_sha256']:assert previous[key]==identity[key],'Resume identity mismatch: '+key
  with np.load(state_path,allow_pickle=False) as z:
   raw=j.asarray(z['raw']);mt=j.asarray(z['adam_m']);vt=j.asarray(z['adam_v']);updates=int(z['completed_updates']);phase=str(z['phase']);pilot=int(z['pilot_index']);phase_step=int(z['phase_updates']);selected=float(z['selected_coefficient']);best=float(z['best_score']);best_raw=j.asarray(z['best_raw']);trials=json.loads(str(z['trials_json']));assert str(z['reference_raw_sha256'])==identity['reference_raw_sha256']
 else:raw=ctx.reference;mt=j.zeros_like(raw);vt=j.zeros_like(raw);updates=0;phase='pilot';pilot=0;phase_step=0;selected=float('nan');best=float('inf');best_raw=raw;trials=[]
 value_grad=jax.jit(jax.value_and_grad(ctx.loss,has_aux=True));value_only=jax.jit(ctx.loss)
 def save():
  np.savez_compressed(state_path,raw=np.asarray(raw),adam_m=np.asarray(mt),adam_v=np.asarray(vt),completed_updates=updates,phase=phase,pilot_index=pilot,phase_updates=phase_step,selected_coefficient=selected,best_score=best,best_raw=np.asarray(best_raw),trials_json=np.array(json.dumps(trials)),reference_raw_sha256=np.array(identity['reference_raw_sha256']))
  dump(history_path,history)
  report={**identity,'completed_updates':updates,'required_updates':cfg['required_updates'],'complete':updates>=cfg['required_updates'],'phase':phase,'pilot_index':pilot,'phase_updates':phase_step,'selected_coefficient':None if not np.isfinite(selected) else selected,'best_score':None if not np.isfinite(best) else best,'history_rows':len(history),'epoch_definition':cfg['epoch_definition'],'last':history[-1] if history else None,'parameter_anchor':cfg['parameter_anchor']}
  dump(OUT/'chunk-report.json',report);dump(OUT/'run-identity.json',identity)
  if os.environ.get('SYNC_EVERY_SAVE')=='1':subprocess.run([sys.executable,str(R/'checkpoint_service.py'),'publish'],check=True)
 save();print('Starting phase',phase,'main updates',updates,flush=True)
 for k in range(a.updates):
  if updates>=cfg['required_updates']:break
  coefficient=cfg['pilot_lambdas'][pilot] if phase=='pilot' else selected
  start=time.monotonic();(loss,aux),grad=value_grad(raw,j.asarray(coefficient));loss.block_until_ready();g=np.asarray(grad)
  if not np.isfinite(float(loss)) or not np.isfinite(g).all():
   dump(OUT/'failure.json',{'phase':phase,'completed_updates':updates,'reason':'nonfinite joint loss/gradient or invalid contact capacity','aux':{key:np.asarray(v).tolist() for key,v in aux.items() if key!='joint_q'}});raise FloatingPointError('No invalid update is counted')
  if phase=='main':
   score=float(aux['joint_loss'])+cfg['coefficient_selection_score_lambda']*float(j.mean(ctx.fractional_shift(raw)**2))
   if score<best:
    best=score;best_raw=raw;np.savez_compressed(OUT/'best-parameters.npz',raw=np.asarray(raw),reference=np.asarray(ctx.reference),completed_updates=updates,score=score)
  norm=float(np.linalg.norm(g));assert norm>0,'No neural parameter gradient; do not count a frozen optimizer as training'
  grad=grad*j.minimum(1.,cfg['gradient_clip_norm']/max(norm,1e-30));mt=cfg['adam_beta1']*mt+(1-cfg['adam_beta1'])*grad;vt=cfg['adam_beta2']*vt+(1-cfg['adam_beta2'])*grad**2
  step_number=phase_step+1;direction=(mt/(1-cfg['adam_beta1']**step_number))/(j.sqrt(vt/(1-cfg['adam_beta2']**step_number))+cfg['adam_epsilon'])
  candidate=ctx.project(raw-cfg['learning_rate']*direction);delta=float(j.max(j.abs(candidate-raw)));assert delta>0,'No actual parameter change'
  raw=candidate;phase_step+=1
  if phase=='main':updates+=1
  row={'phase':phase,'coefficient':float(coefficient),'phase_updates':phase_step,'completed_main_updates':updates,'objective_before_update':float(loss),'joint_mse_before_update':float(aux['joint_loss']),'regularization_before_update':float(aux['regularization']),'gradient_norm':norm,'max_parameter_drift_after_update':float(j.max(j.abs(ctx.fractional_shift(raw)))),'max_raw_update':delta,'seconds':time.monotonic()-start,'max_contacts':np.asarray(aux['max_contacts']).tolist()}
  history.append(row);print(json.dumps(row),flush=True)
  if phase=='pilot' and phase_step>=cfg['pilot_updates_each']:
   total,metrics=value_only(raw,j.asarray(cfg['coefficient_selection_score_lambda']));total.block_until_ready();score=float(total);trials.append({'coefficient':float(coefficient),'updates':phase_step,'common_selection_score':score,'joint_mse':float(metrics['joint_loss']),'drift':float(metrics['max_fractional_drift'])});np.savez_compressed(OUT/f'pilot-{pilot}.npz',raw=np.asarray(raw),reference=np.asarray(ctx.reference))
   pilot+=1;phase_step=0;raw=ctx.reference;mt=j.zeros_like(raw);vt=j.zeros_like(raw)
   if pilot>=len(cfg['pilot_lambdas']):selected=min(trials,key=lambda x:x['common_selection_score'])['coefficient'];phase='main';dump(OUT/'coefficient-trials.json',trials)
  save()
 if updates>=cfg['required_updates']:
  total,metrics=value_only(raw,j.asarray(cfg['coefficient_selection_score_lambda']));total.block_until_ready();score=float(total)
  if score<best:
   best=score;best_raw=raw;np.savez_compressed(OUT/'best-parameters.npz',raw=np.asarray(raw),reference=np.asarray(ctx.reference),completed_updates=updates,score=score)
  dump(OUT/'final-local-evaluation.json',{'completed_updates':updates,'joint_mse':float(metrics['joint_loss']),'max_drift':float(metrics['max_fractional_drift']),'common_selection_score':score})
 save()
if __name__=='__main__':main()
