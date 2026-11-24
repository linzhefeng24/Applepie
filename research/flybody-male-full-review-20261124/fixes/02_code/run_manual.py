"""来源说明（自动添加）：
本文件来自原始 Manual_FreeBody 包（MaleCNS v1.0 连接组 + MANC v1.0 肌肉/身体）。
除本注释外代码未修改；模型内容与来源见 01_model/model.yaml 的 source_notes。
"""
"""Replay manual R2 neural output in the canonical native AB free-body model.
All neural/physical parameters are loaded from01_model, never from BPTT files.
Body motion is integrated once continuously. No root fixation, pose resets,
rescue forces or prescribed leg trajectories. Native auxiliary controls remain.
"""
from pathlib import Path
import argparse,hashlib,json,os,platform
os.environ.setdefault('MUJOCO_GL','egl' if platform.system()=='Linux' else 'glfw')
import numpy as np
import yaml,mujoco
from flymodel import Model
from flymodel.simulator import Body
from flymodel.render import render_videos
from native_ab import Simulation,_table
P=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--render',action='store_true');ap.add_argument('--recompute-neural',action='store_true');args=ap.parse_args()
 cfg=yaml.safe_load((P/'01_model/replay.yaml').read_text());modelpath=P/'01_model/model.yaml';assert sha(modelpath)==cfg['neural_model_sha256'];model=Model(modelpath)
 assert hashlib.sha256(np.ascontiguousarray(model.cells).tobytes()).hexdigest()==cfg['manual_cell_array_sha256']
 data=P/'04_results/data';data.mkdir(parents=True,exist_ok=True);np.savez_compressed(data/'manual-resolved-parameters.npz',cell_parameters=model.cells,global_parameters=model.global_values,HH_kinetics=model.kinetics,body_ids=np.asarray(model.ids))
 path=data/'neural_state.npz'
 if args.recompute_neural:
  result=model.run_neural(experiment='DN_drive');np.savez_compressed(data/'neural_state_recomputed.npz',**result)
 else:
  assert sha(path)==cfg['neural_data_sha256']
  with np.load(path,allow_pickle=False) as z:result={k:z[k] for k in z.files}
 assert str(result['model_sha256'])==model.sha256
 u=model.muscle_excitation(result)
 sim=Simulation(P/'01_model/body_parameters.yaml',case=cfg['case']);m=sim.model;d=sim.data
 root=m.joint('walker/');assert int(root.type[0])==int(mujoco.mjtJoint.mjJNT_FREE)
 ids=[x['muscle_id'] for x in model.mapping];order=np.asarray([ids.index(x) for x in sim.muscle_ids]);to_neural=np.argsort(order)
 protocol=sim.load_ab(cfg['case']);steps=round(cfg['body_duration_ms']/1000/m.opt.timestep);stride=round(cfg['record_interval_ms']/1000/m.opt.timestep);assert len(protocol['controls'])>=steps
 q0=d.qpos.copy();body=Body.__new__(Body);body.owner=model;body.mj=mujoco;body.model=m;body.data=d;body.fixed_root=False;body.indices=sim.muscle_indices[to_neural];body.actadr=m.actuator_actadr[body.indices];body.thorax=m.body(model.config['body']['thorax_name']).id
 qref=_table(sim.config['reference']['joint_angles']);joints=np.asarray(sim.config['reference']['joint_qpos_indices']);refdt=m.opt.timestep*protocol['sample_stride'];target=np.stack([np.interp(np.arange(1,steps+1)*m.opt.timestep,np.arange(len(qref))*refdt,qref[:,j]) for j in range(qref.shape[1])],axis=1)
 poses=[];rows=[];controls=[];extra=False
 for k in range(steps):
  nt=cfg['neural_start_ms']+k*m.opt.timestep*1000*cfg['neural_ms_per_physical_ms'];ni=int(np.floor(nt/model.config['neural']['solver']['spike_bin_ms']));assert ni<len(u)
  row=u[ni].copy()
  for _j,_v in model.external_drive_values(k).items(): row[_j]=_v
  control=protocol['controls'][k].copy();control[sim.muscle_indices]=row[order];d.ctrl[:]=control
  assert not d.qfrc_applied.any() and not d.xfrc_applied.any()
  mujoco.mj_step(m,d);assert np.isfinite(d.qpos).all();poses.append(d.qpos.copy());controls.append(control)
  if (k+1)%stride==0 or k==steps-1:
   body.requested=row.copy();body.applied=d.ctrl[body.indices].copy();obs=body.observe();obs['neural_time_ms']=cfg['neural_start_ms']+d.time*1000*cfg['neural_ms_per_physical_ms'];rows.append(obs)
 trace={key:np.array([x[key] for x in rows]) for key in rows[0]};trace.update(model_sha256=np.array(model.sha256),neural_run_id=result['run_id'],experiment=result['experiment'],fixed_root=np.array(False))
 poses=np.asarray(poses);error=poses[:,joints]-target;mse=float(np.mean(error**2));assert np.isclose(mse,cfg['expected_manual_joint_mse_rad2'],rtol=cfg['expected_mse_relative_tolerance'],atol=cfg['expected_mse_absolute_tolerance']),('Manual replay mismatch',mse)
 np.savez_compressed(data/'body_state.npz',**trace);np.savez_compressed(data/'full_physical_rollout.npz',qpos=poses,controls=np.asarray(controls),initial_qpos=q0,target_joint_angles=target,joint_qpos_indices=joints,dt_s=m.opt.timestep)
 assert not trace['root_fixed'].any();assert np.ptp(poses[:,:3],axis=0).max()>0
 report={'condition':'manual R2 parameters, native AB free body; no BPTT weights','manual_model_sha256':model.sha256,'manual_cell_array_sha256':cfg['manual_cell_array_sha256'],'hand_parameters_included':True,'neural_source':'independently recomputed this run' if args.recompute_neural else 'recovered previously computed manual neural-state archive, SHA256 verified','neural_input_sha256':sha(data/('neural_state_recomputed.npz' if args.recompute_neural else 'neural_state.npz')),'neural_run_id':str(result['run_id']),'physical_replay':'newly integrated this run','fixed_root':False,'root_joint_type':'free','extra_applied_forces':False,'state_resets_during_rollout':False,'native_auxiliary_schedules_retained':len(sim.nonmuscle_indices),'physical_duration_s':steps*m.opt.timestep,'neural_clock_scale':cfg['neural_ms_per_physical_ms'],'joint_mse_rad2':mse,'joint_rmse_deg':float(np.sqrt(mse)*180/np.pi),'root_displacement_native':(poses[-1,:3]-q0[:3]).tolist(),'min_body_up_z_sampled':float(trace['body_up_z'].min()),'ground_contact_samples':int(np.count_nonzero(trace['ground_contact_count'])),'ground_normal_force_max_native':float(trace['ground_contact_normal_force_native'].max()),'validation':'matches archived manual native-AB joint loss; not a claim of stable walking','software':{'python':platform.python_version(),'numpy':np.__version__,'mujoco':mujoco.__version__}}
 (P/'04_results/report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False),flush=True)
 if args.render:
  model.config['render']['frame_count']=cfg['video_frames'];render_videos(model,result,body,trace,P/'04_results/videos',epoch_label='MANUAL R2 | native AB | 3x neural clock')
 sim.close()
if __name__=='__main__':main()
