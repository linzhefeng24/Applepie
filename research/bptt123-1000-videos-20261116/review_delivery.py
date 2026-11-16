"""Verify the downloaded Release bytes and original-network replay identities."""
from pathlib import Path
import hashlib, io, json, sys, zipfile
import numpy as np
R=Path(__file__).resolve().parent
folder=Path(sys.argv[1])
manifest=json.loads((folder/'BPTT_Epoch123_1000.manifest.json').read_text())
for item in manifest['assets']:
 p=folder/item['name']
 assert p.stat().st_size==item['bytes']
 assert hashlib.sha256(p.read_bytes()).hexdigest()==item['sha256']

def load(z,suffix):
 n,=[n for n in z.namelist() if n.endswith(suffix)]
 with np.load(io.BytesIO(z.read(n)),allow_pickle=False) as a:return {k:a[k] for k in a.files}
with zipfile.ZipFile(folder/'BPTT_Epoch123_1000_State.zip') as z:
 a=load(z,'epoch123/neural-state.npz');b=load(z,'epoch1000/neural-state.npz')
 ta=load(z,'epoch123/body-state.npz');tb=load(z,'epoch1000/body-state.npz')
with zipfile.ZipFile(R/'cache/bptt-1000-full-validation.zip') as z:
 original=load(z,'DN_drive.npz')
assert np.array_equal(a['spikes'],original['spikes'])
assert not np.array_equal(a['spikes'],b['spikes'])
assert not np.array_equal(ta['muscle_u_requested'],tb['muscle_u_requested'])
assert not np.array_equal(ta['muscle_activation'],tb['muscle_activation'])
assert not np.array_equal(ta['qpos'],tb['qpos'])
for t in [ta,tb]:
 assert bool(t['fixed_root']) and np.isfinite(t['qpos']).all()
 assert np.ptp(t['thorax_position_native'],axis=0).max()==0
 assert t['ground_contact_normal_force_native'].max()>0
report=dict(all_release_asset_hashes_verified=True,
 epoch123_spikes_exactly_reproduce_prior_full_validation=True,
 epochs_have_distinct_spikes_excitation_and_activation=True,
 fixed_body_and_nonzero_ground_contact_verified_for_both=True,
 manifest=manifest)
(folder/'delivery-review.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='manifest'},indent=2))
