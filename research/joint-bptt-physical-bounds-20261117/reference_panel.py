"""Shared exact-target kinematic panel for intermediate and final comparisons."""
from pathlib import Path
import hashlib,json
import numpy as np
import mujoco
R=Path(__file__).resolve().parent
def load(native,training_target):
 provenance=json.loads((R/'reference/provenance.json').read_text());path=R/'reference/target-video-frames.npz';assert hashlib.sha256(path.read_bytes()).hexdigest()==provenance['frame_asset']['sha256']
 with np.load(path,allow_pickle=False) as z:data={k:z[k] for k in z.files}
 ids=np.asarray(native.config['reference']['joint_qpos_indices']);assert np.array_equal(ids,data['joint_qpos_indices'])
 table=native.config['reference']['joint_angles'];angles=np.fromstring(table['values'],sep=' ').reshape(table['shape']);assert hashlib.sha256(angles.tobytes()).hexdigest()==provenance['reference_joint_table_sha256']
 assert np.array_equal(angles[data['source_frame_indices']],data['qpos'][:,ids])
 error=float(abs(np.asarray(training_target)[49::50]-data['qpos'][:,ids]).max());assert error<1e-12
 model=native.model;d=mujoco.MjData(model);states=[]
 for k,t in enumerate(data['time_s']):
  d.time=t;d.qpos[:]=data['qpos'][k];d.qvel[:]=data['qvel'][k];d.act[:]=0
  state=np.empty(mujoco.mj_stateSize(model,mujoco.mjtState.mjSTATE_FULLPHYSICS));mujoco.mj_getState(model,d,state,mujoco.mjtState.mjSTATE_FULLPHYSICS);states.append(state)
 details={'kind':'original prescribed kinematic reference, not muscle-driven simulation','root_motion_in_loss':False,'target_frame_max_abs_error':error,'provenance':provenance,'root_displacement_mm':((data['qpos'][-1,:3]-data['initial_qpos'][:3])*native.config['units']['native_length_to_mm']).tolist()}
 return np.asarray(states),details
