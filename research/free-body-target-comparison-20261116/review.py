"""Verify remote bytes, identical starts and drives, and continuous free-body time."""
from pathlib import Path
import hashlib,io,json,sys,zipfile
import numpy as np
folder=Path(sys.argv[1]);source=Path(sys.argv[2]);manifest=json.loads((folder/'FreeBody_manifest.json').read_text())
for item in manifest['assets']:
 p=folder/item['name'];assert p.stat().st_size==item['bytes'];assert hashlib.sha256(p.read_bytes()).hexdigest()==item['sha256']
def load(z,name):
 with np.load(io.BytesIO(z.read(name)),allow_pickle=False) as a:return {k:a[k] for k in a.files}
starts=[];summary=[]
with zipfile.ZipFile(folder/'FreeBody_Comparison_Bundle.zip') as z,zipfile.ZipFile(source) as old:
 for name in ['Epoch123','Epoch1000','TargetU']:
  t=load(z,f'FreeBody_{name}_state.npz');inputs=load(z,f'FreeBody_{name}_inputs.npz');starts.append(inputs['initial_state'])
  assert not bool(t['fixed_root']);assert not t['root_fixed'].any();assert np.diff(t['time_s']).min()>0;assert abs(t['time_s'][-1]-1.4)<1e-9
  assert not t['extra_applied_force'].any();assert np.isfinite(t['qpos']).all()
  if name!='TargetU':
   fixed=load(old,f'epoch{name[5:]}/body-state.npz');assert np.array_equal(t['muscle_u_requested'],fixed['muscle_u_requested'])
  summary.append(dict(condition=name,final_up_z=float(t['body_up_z'][-1]),min_up_z=float(t['body_up_z'].min()),initial_thorax_z_native=float(t['thorax_position_native'][0,2]),final_thorax_z_native=float(t['thorax_position_native'][-1,2]),min_thorax_z_native=float(t['thorax_position_native'][:,2].min())))
assert all(np.array_equal(starts[0],x) for x in starts[1:])
report=dict(all_remote_asset_hashes_verified=True,all_three_initial_states_exactly_equal=True,neural_drives_identical_to_fixed_body_runs=True,all_time_axes_monotonic_and_complete_1_4s=True,no_extra_applied_forces=True,summary=summary,manifest=manifest)
(folder/'delivery-review.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='manifest'},indent=2))
