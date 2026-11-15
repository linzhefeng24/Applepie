"""Same neural input, exact fixed initial body pose, native leg/ground dynamics."""

from pathlib import Path
import hashlib, json, sys
import numpy as np

R = Path(__file__).resolve().parent
D = R.parent / "single-model-delivery-20261115"
P = D / "build/UnifiedFlyModel"
sys.path.insert(0, str(D / "runtime/02_code"))
from flymodel import Model
from flymodel.render import render_videos

out = R / "results"
out.mkdir(exist_ok=True)
path = P / "04_results/data/neural_state.npz"
with np.load(path, allow_pickle=False) as z:
    r = {k: z[k] for k in z.files}
m = Model(P / "01_model/model.yaml")
assert str(r["model_sha256"]) == m.sha256
body, trace = m.simulate_body(r, fixed_root=True)
np.savez_compressed(out / "body_state.npz", **trace)
positions = trace["thorax_position_native"]
quats = trace["thorax_quaternion"]
report = {
    "condition": "root rigidly fixed to initial pose; native legs and ground contacts",
    "model_sha256": m.sha256,
    "neural_input_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    "neural_run_id": str(r["run_id"]),
    "position_max_drift_native": float(np.max(abs(positions - positions[0]))),
    "quaternion_max_drift": float(np.max(abs(quats - quats[0]))),
    "ground_contact_sample_count": int(np.count_nonzero(trace["ground_contact_count"])),
    "ground_normal_force_max_native": float(
        trace["ground_contact_normal_force_native"].max()
    ),
    "qpos_max_range": float(np.ptp(trace["qpos"], axis=0).max()),
    "native_contact_forces_retained": True,
    "neural_parameters_changed": False,
    "interpretation": "externally supported experiment; not free walking or balance",
}
assert report["position_max_drift_native"] == 0 and report["quaternion_max_drift"] == 0
assert report["ground_normal_force_max_native"] > 0
(out / "report.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2), flush=True)
render_videos(m, r, body, trace, out / "videos")
