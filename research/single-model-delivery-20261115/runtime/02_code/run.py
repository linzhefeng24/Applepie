"""CLI entry points for the single model; physical defaults are in model.yaml."""

from pathlib import Path
import argparse, hashlib, json, platform, sys, time
from importlib.metadata import version
import numpy as np
from flymodel import Model

ROOT = Path(__file__).resolve().parents[1]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "command",
        choices=["inspect", "neural", "demo", "render", "state", "connections"],
    )
    p.add_argument(
        "--fixed-body",
        action="store_true",
        help="Fix the body at its initial pose; keep leg and ground dynamics",
    )
    p.add_argument("--model", type=Path, default=ROOT / "01_model/model.yaml")
    p.add_argument("--experiment", default="DN_drive")
    p.add_argument("--out", type=Path, default=ROOT / "04_results")
    p.add_argument("--inputs", type=Path)
    p.add_argument("--neural", type=Path)
    p.add_argument("--body", type=Path)
    p.add_argument("--type")
    p.add_argument("--id", action="append")
    p.add_argument("--time-ms", type=float)
    p.add_argument("--direction", choices=["incoming", "outgoing"], default="incoming")
    args = p.parse_args()
    model = Model(args.model)
    args.out.mkdir(parents=True, exist_ok=True)
    data = args.out / "data"
    data.mkdir(exist_ok=True)
    if args.command == "inspect":
        ids = model.neuron_ids(type=args.type) if args.type else (args.id or [])
        print(
            json.dumps(
                {
                    "identity": model.config["identity"],
                    "model_sha256": model.sha256,
                    "neuron_count": len(model.ids),
                    "fast_edges": len(model.weight),
                    "muscles": len(model.mapping),
                    "mapped_muscles": sum(bool(x["MN_indices"]) for x in model.mapping),
                    "experiments": list(model.config["experiments"]),
                    "cells": {b: model.cell_parameters(b) for b in ids},
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return
    if args.command == "connections":
        if not args.id:
            p.error("--id required")
        print(
            json.dumps(
                {b: model.connections(b, args.direction) for b in args.id},
                ensure_ascii=False,
                indent=2,
            )
        )
        return
    if args.command == "state":
        if args.neural is None or args.time_ms is None:
            p.error("--neural and --time-ms required")
        with np.load(args.neural, allow_pickle=False) as z:
            r = {k: z[k] for k in z.files}
        if str(r["model_sha256"]) != model.sha256:
            raise ValueError("Result belongs to a different model")
        ids = args.id or model.neuron_ids(type=args.type)
        state = model.state(ids, args.time_ms, result=r)
        print(
            json.dumps(
                {
                    k: v.tolist() if isinstance(v, np.ndarray) else v
                    for k, v in state.items()
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return
    if args.command in ["neural", "demo"]:
        events = json.load(open(args.inputs)) if args.inputs else None
        print(
            "Running",
            args.experiment,
            "with",
            len(model.ids),
            "cells; all states recorded",
            flush=True,
        )
        start = time.perf_counter()
        r = model.run_neural(args.experiment, events=events)
        np.savez_compressed(data / "neural_state.npz", **r)
        np.savez_compressed(
            data / "muscle_excitation.npz",
            u=model.muscle_excitation(r),
            muscle_ids=[x["muscle_id"] for x in model.mapping],
        )
        print(
            "Neural integration finished in",
            round(time.perf_counter() - start, 2),
            "seconds",
            flush=True,
        )
        if args.command == "neural":
            return
    else:
        path = args.neural or data / "neural_state.npz"
        with np.load(path, allow_pickle=False) as z:
            r = {k: z[k] for k in z.files}
        if str(r["model_sha256"]) != model.sha256:
            raise ValueError("Neural result/model mismatch")
    if args.command == "demo":
        body, trace = model.simulate_body(r, fixed_root=args.fixed_body)
        np.savez_compressed(data / "body_state.npz", **trace)
    else:
        with np.load(args.body or data / "body_state.npz", allow_pickle=False) as z:
            trace = {k: z[k] for k in z.files}
        if (
            str(trace["model_sha256"]) != model.sha256
            or str(trace.get("neural_run_id", "")) != str(r["run_id"])
            or (args.fixed_body and not bool(trace.get("fixed_root", False)))
        ):
            body, trace = model.simulate_body(r, fixed_root=args.fixed_body)
            np.savez_compressed(data / "body_state.npz", **trace)
        else:
            body = model.body(fixed_root=bool(trace.get("fixed_root", False)))
    from flymodel.render import render_videos

    videos = render_videos(model, r, body, trace, args.out / "videos")
    u = model.muscle_excitation(r)
    movement = np.ptp(trace["qpos"], axis=0)
    report = {
        "model_sha256": model.sha256,
        "experiment": args.experiment,
        "python": platform.python_version(),
        "versions": {
            n: version(n)
            for n in [
                "numpy",
                "scipy",
                "numba",
                "mujoco",
                "PyYAML",
                "matplotlib",
                "imageio-ffmpeg",
            ]
        },
        "command": [sys.executable, *sys.argv],
        "neural_spikes": int(r["spikes"].sum()),
        "mapped_channels": sum(bool(x["MN_indices"]) for x in model.mapping),
        "active_requested_muscle_channels": int(
            (u.max(0) > model.config["neuromuscular"]["excitation_bounds"][0]).sum()
        ),
        "body_duration_s": float(trace["time_s"][-1]),
        "all_body_states_finite": bool(np.isfinite(trace["qpos"]).all()),
        "body_configuration_changed": bool(np.any(movement > 0)),
        "min_body_up_z": float(trace["body_up_z"].min()),
        "extra_applied_force": bool(trace["extra_applied_force"].any()),
        "archived_AB_control_sequence_used": False,
        "physical_state_reset_during_integration": False,
        "sensory_to_neural_feedback": False,
        "stable_walking_verified": False,
        "body_fixed_at_initial_pose": body.fixed_root,
        "muscle_mapping_scope": "candidate functional category mapping, not confirmed individual motor-unit anatomy",
        "network_video_scope": "schematic 3D layout, not reconstructed neuronal morphology",
        "videos": videos,
    }
    (args.out / "verification.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
