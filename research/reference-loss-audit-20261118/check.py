"""Audit the actual production loss with injected known joint trajectories.
Only diagnostic instance callbacks are replaced; production files and training
are unchanged. Injection tests the loss, not whether controls can realize qref.
"""
from pathlib import Path
import argparse,hashlib,json,sys,platform,subprocess
from importlib.metadata import version
import numpy as np
import jax
jax.config.update('jax_enable_x64',True)
import jax.numpy as j
import mujoco
R=Path(__file__).resolve().parent;ROOT=R.parents[1];SRC=ROOT/'research/joint-bptt-physical-bounds-20261117'
sys.path.insert(0,str(SRC))
from training_context import JointContext
p=argparse.ArgumentParser();p.add_argument('--reference-source',type=Path,required=True);a=p.parse_args()
ctx=JointContext();physics=ctx.physics;body=ctx.native_physics;model=body.m
source_sha=hashlib.sha256(a.reference_source.read_bytes()).hexdigest();provenance=json.loads((SRC/'reference/provenance.json').read_text());assert source_sha==provenance['source_file_sha256']
with np.load(a.reference_source,allow_pickle=False) as z:source={k:z[k] for k in z.files}
ids=np.asarray(physics.joint_ids);names=[mujoco.mj_id2name(model,mujoco.mjtObj.mjOBJ_JOINT,int(model.dof_jntid[d])) for d in source['joint_dof_indices']]
assert np.array_equal(ids,source['joint_qpos_indices']) and names==source['joint_names'].tolist()
assert len(ids)==66 and len(np.unique(ids))==66
N=physics.nsteps;times=np.arange(1,N+1)*physics.dt
independent_q=np.stack([np.interp(times,source['time_s'],source['qpos'][:,k]) for k in range(model.nq)],axis=1)
target=np.asarray(physics.target);error=independent_q[:,ids]-target
# Also check every original2001 sample against the canonical YAML data.
table=physics.native.config['reference']['joint_angles'];canonical=np.fromstring(table['values'],sep=' ').reshape(table['shape'])
assert np.array_equal(canonical,source['qpos'][:,ids])
assert source['time_s'][0]==0 and np.isclose(source['time_s'][-1],N*physics.dt)
# Route controlled q through the unchanged NativeWhitebox.objective method.
# Neural outputs are irrelevant to this injection; no spike simulation is claimed.
ctx.neural_u=lambda raw:j.zeros((ctx.cfg['neural_end_ms'],len(ctx.order)),dtype=j.float64)
original_rollout=body.rollout
cases={}
def evaluate(q):
 body.rollout=lambda u:(physics.initial,(j.asarray(q),j.zeros((len(q),len(body.dims)),dtype=j.int32)))
 total,aux=ctx.loss(ctx.initial,j.asarray(0.,dtype=j.float64))
 return {'total_without_regularization':float(total),'joint_mse_rad2':float(aux['joint_loss']),'regularization':float(aux['regularization'])}
q_exact=independent_q.copy();q_exact[:,ids]=target
cases['exact_training_reference']=evaluate(q_exact)
cases['original_source_reference_independently_interpolated']=evaluate(independent_q)
q=q_exact.copy();q[:,ids]+=.1;cases['all_joints_plus_0_1_rad']=evaluate(q)
q=q_exact.copy();q[:,ids[0]]+=.1;cases['one_joint_plus_0_1_rad']=evaluate(q)
q=q_exact.copy();q[-1,ids[0]]+=.1;cases['one_joint_one_time_plus_0_1_rad']=evaluate(q)
q=q_exact.copy();q[:,ids]=target[np.r_[0,np.arange(N-1)]];cases['reference_one_physics_step_late']=evaluate(q)
q=q_exact.copy();q[:,:3]+=100.;cases['root_translation_only_changed']=evaluate(q)
body.rollout=original_rollout
assert cases['exact_training_reference']['total_without_regularization']==0.
assert cases['exact_training_reference']['regularization']==0.
assert cases['original_source_reference_independently_interpolated']['joint_mse_rad2']<1e-24
assert np.isclose(cases['all_joints_plus_0_1_rad']['joint_mse_rad2'],.01,rtol=1e-12)
assert np.isclose(cases['one_joint_plus_0_1_rad']['joint_mse_rad2'],.01/66,rtol=1e-12)
assert np.isclose(cases['one_joint_one_time_plus_0_1_rad']['joint_mse_rad2'],.01/(66*N),rtol=1e-12)
assert cases['reference_one_physics_step_late']['joint_mse_rad2']>0
assert cases['root_translation_only_changed']['joint_mse_rad2']==0.
report={'passed':True,'git_revision':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'method':'call unchanged JointContext.loss(coefficient=0) and NativeWhitebox.objective with diagnostic rollout injection; no physics realizability claim','loss_formula':'mean over4000 steps x66 joints of squared radian angle error; no alignment, no rescaling, no endpoint-only mask','physical_dt_s':physics.dt,'time_samples':N,'evaluated_time_s':[float(times[0]),float(times[-1])],'source_sample_time_s':[float(source['time_s'][0]),float(source['time_s'][-1])],'source_dt_s':float(source['time_s'][1]-source['time_s'][0]),'reference_sampling':'linear interpolation of original2001 frames onto4000 post-step samples, no extrapolation','joint_qpos_indices':ids.tolist(),'joint_names':names,'source_original_joint_table_bitwise_equal_to_model_yaml':True,'independent_interpolation_max_abs_error_rad':float(abs(error).max()),'cases':cases,'target_joint_array_sha256':hashlib.sha256(target.tobytes()).hexdigest(),'source_file':{'name':a.reference_source.name,'sha256':source_sha,'bytes':a.reference_source.stat().st_size},'software':{'python':platform.python_version(),**{n:version(n) for n in ['numpy','jax','jaxlib','mujoco','mujoco-mjx']}},'source_sha256':{name:hashlib.sha256((SRC/name).read_bytes()).hexdigest() for name in ['training_context.py','physics.py','native_whitebox.py']},'training_numerics_modified':False}
(R/'results.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
