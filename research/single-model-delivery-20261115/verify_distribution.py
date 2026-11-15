"""Fresh extraction, hash verification and public-API smoke check of delivered ZIP.

Run with the distribution's declared dependencies. Does not alter its parameters.
"""

from pathlib import Path
import argparse, hashlib, json, sys, tempfile, zipfile
import numpy as np

p = argparse.ArgumentParser(description=__doc__)
p.add_argument("archive", type=Path)
p.add_argument("--report", type=Path, required=True)
a = p.parse_args()
with tempfile.TemporaryDirectory(prefix="fly-delivery-check-") as temp:
    with zipfile.ZipFile(a.archive) as z:
        assert z.testzip() is None
        for name in z.namelist():
            assert not Path(name).is_absolute() and ".." not in Path(name).parts
        z.extractall(temp)
    root = Path(temp) / "UnifiedFlyModel"
    manifest = json.loads((root / "MANIFEST.json").read_text())
    for entry in manifest["contents"]:
        f = root / entry["path"]
        assert f.stat().st_size == entry["bytes"]
        assert hashlib.sha256(f.read_bytes()).hexdigest() == entry["sha256"]
    assert len(list(root.rglob("model.yaml"))) == 1
    sys.path.insert(0, str(root / "02_code"))
    from flymodel import Model

    m = Model(root / "01_model/model.yaml")
    with np.load(root / "04_results/data/neural_state.npz", allow_pickle=False) as z:
        result = {k: z[k] for k in z.files}
    assert str(result["model_sha256"]) == m.sha256
    ids = m.neuron_ids(type="DNg100")
    state = m.state(
        ids, m.config["experiments"]["DN_drive"]["events"][0]["on_ms"], result=result
    )
    assert len(ids) == 2 and "gating_m_h_n" in state
    u = m.muscle_excitation(result)
    assert u.shape[1] == 130 and np.isfinite(u).all()
    body = m.body()
    initial = body.observe()
    body.step(np.zeros(len(m.mapping)))
    observed = body.observe()
    assert (
        observed["time_s"] > initial["time_s"] and np.isfinite(observed["qpos"]).all()
    )
    assert isinstance(body.contacts(), list)
    videos = list((root / "04_results/videos").glob("*.mp4"))
    assert len(videos) == 3
    report = {
        "status": "passed fresh extraction, full manifest and public interfaces",
        "archive_sha256": hashlib.sha256(a.archive.read_bytes()).hexdigest(),
        "archive_bytes": a.archive.stat().st_size,
        "code_revision": manifest["code_revision"],
        "model_sha256": m.sha256,
        "verified_files": len(manifest["contents"]),
        "neurons": len(m.ids),
        "muscle_channels": len(m.mapping),
        "video_count": len(videos),
        "state_fields": list(state),
        "independent_body_and_contact_interfaces": True,
        "laboratory_experiments_newly_validated": [],
    }
a.report.write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
