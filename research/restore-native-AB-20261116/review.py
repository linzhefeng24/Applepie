"""Verify downloaded native-AB matched comparison and standalone bundle."""
from pathlib import Path
import hashlib,io,json,sys,zipfile
import numpy as np
folder=Path(sys.argv[1]);manifest=json.loads((folder/'NativeAB_manifest.json').read_text())
for row in manifest['assets']:
 p=folder/row['name'];assert p.stat().st_size==row['bytes'];assert hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256']
def load(z,name):
 with np.load(io.BytesIO(z.read(name)),allow_pickle=False) as a:return {k:a[k] for k in a.files}
report=manifest['report'];assert report['matched_simulation_verified'] and report['target_substitution_identity_exact'];identities=[];warms=[];controls=[]
with zipfile.ZipFile(folder/'NativeAB_Reproduction_Bundle.zip') as z:
 config=json.loads(z.read('config.json'))
 for name,h in config['model_files'].items():assert hashlib.sha256(z.read('model/'+name)).hexdigest()==h
 for name in ['A','B','Epoch123','Epoch1000']:
  t=load(z,f'outputs/NativeAB_{name}_state.npz');identities.append(t['initial_state']);warms.append(t['initial_warmstart']);controls.append(t['controls_all_141'])
  assert np.isfinite(t['full_state']).all();assert np.diff(t['time_s']).min()>0;assert abs(t['time_s'][-1]-.4)<1e-9
  assert hashlib.sha256(t['full_state'].tobytes()).hexdigest()==report['conditions'][name]['full_state_sha256']
 assert all(np.array_equal(identities[0],x) for x in identities)
 assert all(np.array_equal(warms[0],x) for x in warms)
 # The original archived ordering is head/abdomen5 + adhesion6, then muscles130.
 assert all(np.array_equal(controls[0][:,:11],x[:,:11]) for x in controls)
 for name in ['A','B']:assert report['conditions'][name]['archived_replayer_exact_state_equality'] and report['conditions'][name]['min_body_up_z']>.9
 assert 'replay_compare.py' in z.namelist() and 'inputs/neural-u.npz' in z.namelist() and 'RUN.txt' in z.namelist()
review={'remote_asset_bytes_and_hashes_verified':True,'original_simulator_and_yaml_unchanged':True,'initial_full_state_warmstart_and_auxiliary_controls_identical':True,'all_four_physics_time_axes_native_and_continuous':True,'original_AB_full_state_matches_archived_replayer':True,'standalone_bundle_contains_exact_model_driver_and_inputs':True,'manifest':manifest}
(folder/'delivery-review.json').write_text(json.dumps(review,indent=2)+'\n');print(json.dumps({k:v for k,v in review.items() if k!='manifest'},indent=2))
