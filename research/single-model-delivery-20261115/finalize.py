"""Validate actual outputs and archive the one-model runtime distribution."""

from pathlib import Path
import hashlib, json, os, shutil, subprocess, zipfile
import numpy as np
import imageio_ffmpeg

R = Path(__file__).resolve().parent
P = R / "build/UnifiedFlyModel"
D = R / "dist"
D.mkdir(exist_ok=True)
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
report = json.loads((P / "04_results/verification.json").read_text())
equivalence = json.loads((R / "source-equivalence.json").read_text())
assert (
    report["model_sha256"]
    == sha(P / "01_model/model.yaml")
    == equivalence["model_sha256"]
)
assert equivalence["all_spikes_identical"]
assert all(v == 0 for v in equivalence["recorded_state_max_abs_difference"].values())
assert report["all_body_states_finite"] and report["body_configuration_changed"]
assert (
    not report["extra_applied_force"]
    and not report["archived_AB_control_sequence_used"]
)
assert report["mapped_channels"] == 104
for path in (P / "04_results/data").glob("*.npz"):
    with np.load(path, allow_pickle=False) as z:
        for key in z.files:
            a = z[key]
            if a.dtype.kind in "fc":
                assert np.isfinite(a).all(), (path, key)
videos = sorted((P / "04_results/videos").glob("*.mp4"))
assert len(videos) == 3
for path in videos:
    subprocess.run(
        [
            imageio_ffmpeg.get_ffmpeg_exe(),
            "-v",
            "error",
            "-i",
            str(path),
            "-f",
            "null",
            "-",
        ],
        check=True,
    )
shutil.copy2(R / "source-equivalence.json", P / "04_results/source_equivalence.json")
phenomena_path = P / "03_phenomena/phenomena.json"
phenomena = json.loads(phenomena_path.read_text())
for item in phenomena["can_complete_in_stated_scope"]:
    if item["id"] == "DN_to_muscle_forward_simulation":
        item["status"] = "independently_rerun_in_packaged_demo"
        item["evidence"] = "../04_results/verification.json"
phenomena["demo_scope"] = {
    "laboratory_experiments_newly_validated": [],
    "note": "Forward simulation and software checks do not establish a laboratory phenotype or stable walking.",
}
phenomena_path.write_text(json.dumps(phenomena, indent=2, ensure_ascii=False) + "\n")
for path in P.rglob("__pycache__"):
    shutil.rmtree(path)
revision = (
    os.environ.get("GITHUB_SHA")
    or subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=R, text=True).strip()
)
manifest = {
    "schema": "unified_fly_delivery_v1",
    "code_revision": revision,
    "model_sha256": report["model_sha256"],
    "contents": [
        {"path": str(p.relative_to(P)), "bytes": p.stat().st_size, "sha256": sha(p)}
        for p in sorted(P.rglob("*"))
        if p.is_file() and p.name != "MANIFEST.json"
    ],
}
(P / "MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n")
archive = D / "UnifiedFlyModel_20261115.zip"
with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    for path in sorted(P.rglob("*")):
        if path.is_file():
            z.write(path, str(path.relative_to(P.parent)))
asset = {
    "file": archive.name,
    "bytes": archive.stat().st_size,
    "sha256": sha(archive),
    "code_revision": revision,
    "model_sha256": report["model_sha256"],
    "status": "actual integrated neural/body rerun with three decoded videos; not validated stable walking",
}
(D / "manifest.json").write_text(json.dumps(asset, indent=2) + "\n")
print(json.dumps(asset, indent=2))
