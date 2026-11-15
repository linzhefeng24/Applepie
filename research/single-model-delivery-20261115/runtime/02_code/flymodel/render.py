"""Synchronized actual-body rendering and clearly labelled 3D circuit schematic.
Red/green edges denote central excitatory/inhibitory model output. Node colour
is net synaptic+external current, size is firing. Muscle green means decreasing
activation, never a claim of an inhibitory glutamatergic NMJ.
All numerical display settings come from model.yaml.
"""

from pathlib import Path
import subprocess
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from mpl_toolkits.mplot3d.art3d import Line3DCollection
from PIL import Image, ImageDraw, ImageFont


def colors(value, scale, r):
    v = np.asarray(value)
    mag = np.clip(np.abs(v) / scale, 0, 1)
    base = np.asarray(r["neutral"])
    chosen = np.where((v >= 0)[:, None], np.asarray(r["red"]), np.asarray(r["green"]))
    return np.c_[base + (chosen - base) * mag[:, None], np.ones(len(v))]


class Video:
    def __init__(self, path, width, height, r):
        import imageio_ffmpeg

        self.proc = subprocess.Popen(
            [
                imageio_ffmpeg.get_ffmpeg_exe(),
                "-y",
                "-loglevel",
                "error",
                "-f",
                "rawvideo",
                "-pix_fmt",
                "rgb24",
                "-s",
                str(width) + "x" + str(height),
                "-r",
                str(r["fps"]),
                "-i",
                "-",
                "-an",
                "-c:v",
                "libx264",
                "-crf",
                str(r["encoder_crf"]),
                "-threads",
                str(r["encoder_threads"]),
                "-pix_fmt",
                "yuv420p",
                str(path),
            ],
            stdin=subprocess.PIPE,
        )

    def write(self, frame):
        self.proc.stdin.write(np.ascontiguousarray(frame, dtype=np.uint8).tobytes())

    def close(self):
        self.proc.stdin.close()
        if self.proc.wait() != 0:
            raise RuntimeError("Video encoder failed")


def render_videos(model, neural, body, trace, output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    r = model.config["render"]
    mj = body.mj
    m = body.model
    w = r["body_width"]
    h = r["body_height"]
    gw = r["graph_width"]
    gh = r["graph_height"]
    m.vis.global_.offwidth = max(m.vis.global_.offwidth, w)
    m.vis.global_.offheight = max(m.vis.global_.offheight, h)
    renderer = mj.Renderer(m, height=h, width=w, max_geom=r["max_geom"])
    opt = mj.MjvOption()
    opt.flags[mj.mjtVisFlag.mjVIS_TENDON] = False
    opt.sitegroup[:] = 0
    for i in range(m.ngeom):
        name = m.geom(i).name
        if name.startswith(r["hide_geom_prefix"]):
            m.geom_rgba[i, 3] = 0
        elif name.startswith("walker/"):
            m.geom_rgba[i, 3] = r["body_opacity"]
    sites = [
        [m.site(n).id for n in x["path_site_names"]]
        for x in model.config["body"]["muscles"]
    ]
    font = ImageFont.truetype(font_manager.findfont(r["font_family"]), r["font_size"])
    positions = model.layout["positions"]
    muscle_positions = model.layout["muscle_positions"]
    pre = model.layout["display_pre"]
    post = model.layout["display_post"]
    sign = model.layout["display_sign"]
    segments = np.stack((positions[pre], positions[post]), axis=1)
    fig = plt.figure(figsize=(gw / r["dpi"], gh / r["dpi"]), dpi=r["dpi"])
    ax = fig.add_subplot(projection="3d")
    ax.view_init(r["graph_elevation_deg"], r["graph_azimuth_deg"])
    ax.set_axis_off()
    nodes = ax.scatter(*positions.T, s=r["node_base_size"], depthshade=False)
    muscles = ax.scatter(
        *muscle_positions.T, s=r["muscle_marker_base_size"], depthshade=False
    )
    edges = Line3DCollection(segments, linewidths=r["edge_base_width"])
    ax.add_collection3d(edges)
    mp = []
    mt = []
    for j, entry in enumerate(model.mapping):
        for i in entry["MN_indices"]:
            mp.append(i)
            mt.append(j)
    mp = np.asarray(mp, dtype=int)
    mt = np.asarray(mt, dtype=int)
    nmj = Line3DCollection(
        np.stack((positions[mp], muscle_positions[mt]), axis=1),
        linewidths=r["edge_base_width"],
    )
    ax.add_collection3d(nmj)
    for x, label in zip(
        sorted(set(positions[:, 0])) + [float(muscle_positions[0, 0])],
        ["Brain / DN", "VNC", "MN", "Muscles"],
    ):
        ax.text(x, r["layer_label_y"], r["layer_label_z"], label)
    allpos = np.r_[positions, muscle_positions]
    margin = r["graph_margin"]
    ax.set(
        xlim=(allpos[:, 0].min() - margin, allpos[:, 0].max() + margin),
        ylim=(allpos[:, 1].min() - margin, allpos[:, 1].max() + margin),
        zlim=(allpos[:, 2].min() - margin, allpos[:, 2].max() + margin),
    )
    label = fig.text(*r["text_anchor"], "", fontsize=r["font_size"])
    fig.text(
        *r["footer_anchor"],
        "Schematic layout, NOT EM morphology. Full network simulated; display edges sampled.",
        fontsize=r["footer_font_size"],
    )
    fig.tight_layout()
    # Causal display-only rate filter; never fed into neural dynamics.
    bin_ms = model.config["neural"]["solver"]["spike_bin_ms"]
    decay = np.exp(-bin_ms / r["rate_filter_tau_ms"])
    state = np.zeros(len(model.ids))
    rates = np.empty_like(neural["spikes"], dtype=float)
    for k, row in enumerate(neural["spikes"]):
        state = (
            decay * state
            + (1 - decay) * row * model.config["units"]["ms_per_s"] / bin_ms
        )
        rates[k] = state
    if len(neural["record_indices"]) != len(model.ids):
        raise ValueError(
            "3D population video requires all neurons recorded; API supports subsets for other work"
        )
    recsort = np.argsort(neural["record_indices"])
    streams = [
        Video(output / "01_body_muscles.mp4", w, h, r),
        Video(output / "02_neural_chain_3d.mp4", gw, gh, r),
        Video(output / "03_synchronized.mp4", w + gw, h, r),
    ]
    previous = np.zeros(len(model.mapping))
    frame_times = np.linspace(trace["time_s"][0], trace["time_s"][-1], r["frame_count"])
    try:
        for f, ts in enumerate(frame_times):
            bi = int(np.argmin(abs(trace["time_s"] - ts)))
            nt = trace["neural_time_ms"][bi]
            ni = int(np.argmin(abs(neural["time_ms"] - nt)))
            ri = min(int(nt / bin_ms), len(rates) - 1)
            rate = rates[ri]
            curr = neural["currents_pA"][ni][recsort]
            net = curr[:, 0] + curr[:, 1] + curr[:, 3]
            a = trace["muscle_activation"][bi]
            delta = a - previous
            muscle_signal = np.where(delta < -r["muscle_decay_threshold"], -a, a)
            mc = colors(
                muscle_signal, model.config["neuromuscular"]["excitation_bounds"][1], r
            )
            previous = a.copy()
            body.restore_for_render(trace, bi)
            body.data.ctrl[body.indices] = trace["muscle_u_applied"][bi]
            renderer.update_scene(
                body.data, camera=model.config["body"]["camera_id"], scene_option=opt
            )
            for j, ss in enumerate(sites):
                for sa, sb in zip(ss[:-1], ss[1:]):
                    if renderer.scene.ngeom >= r["max_geom"]:
                        raise RuntimeError("Renderer geometry budget exceeded")
                    g = renderer.scene.geoms[renderer.scene.ngeom]
                    mj.mjv_initGeom(
                        g,
                        mj.mjtGeom.mjGEOM_CAPSULE,
                        np.zeros(3),
                        np.zeros(3),
                        np.eye(3).reshape(-1),
                        mc[j].astype(np.float32),
                    )
                    mj.mjv_connector(
                        g,
                        mj.mjtGeom.mjGEOM_CAPSULE,
                        r["muscle_radius_native"]
                        + r["muscle_radius_gain_native"] * a[j],
                        body.data.site_xpos[sa],
                        body.data.site_xpos[sb],
                    )
                    renderer.scene.ngeom += 1
            im = Image.fromarray(renderer.render().copy())
            draw = ImageDraw.Draw(im)
            draw.rectangle((0, 0, w, r["caption_height"]), fill="black")
            x, y = r["caption_margin"]
            draw.text(
                (x, y),
                f"DN-driven native body | body {ts:.3f}s | neural {nt:.1f}ms",
                fill="white",
                font=font,
            )
            draw.text(
                (x, y + r["caption_line_height"]),
                "RED activation | GREEN decreasing activation | gravity + ground contacts",
                fill="white",
                font=font,
            )
            draw.text(
                (x, y + r["caption_line_height"] * 2),
                "Candidate MN-muscle mapping; no target motion or rescue force",
                fill="white",
                font=font,
            )
            body_image = np.asarray(im)
            nodes.set_facecolors(colors(net, r["net_current_scale_pA"], r))
            nodes.set_sizes(
                r["node_base_size"]
                + r["node_rate_gain_size"]
                * np.clip(rate / r["edge_rate_scale_Hz"], 0, 1)
            )
            muscles.set_facecolors(mc)
            muscles.set_sizes(
                r["muscle_marker_base_size"] + r["muscle_marker_gain_size"] * a
            )
            ec = colors(sign, r["sign_color_scale"], r)
            strength = np.clip(rate[pre] / r["edge_rate_scale_Hz"], 0, 1)
            ec[:, 3] = r["edge_base_alpha"] + r["edge_active_alpha"] * strength
            edges.set_color(ec)
            edges.set_linewidth(
                r["edge_base_width"] + r["edge_active_width"] * strength
            )
            nc = colors(np.ones(len(mp)), r["sign_color_scale"], r)
            nc[:, 3] = r["edge_base_alpha"] + r["edge_active_alpha"] * np.clip(
                rate[mp] / r["edge_rate_scale_Hz"], 0, 1
            )
            nmj.set_color(nc)
            label.set_text(
                f"Neural {nt:.1f}ms | nodes: net input, size: firing | edges: RED E / GREEN I"
            )
            fig.canvas.draw()
            graph_image = np.asarray(fig.canvas.buffer_rgba())[:, :, :3].copy()
            streams[0].write(body_image)
            streams[1].write(graph_image)
            combined = np.concatenate((body_image, graph_image), axis=1)
            streams[2].write(combined)
            if f in {0, len(frame_times) // 2, len(frame_times) - 1}:
                Image.fromarray(combined).save(output / f"preview_{f:03d}.png")
            if f % r["progress_frame_stride"] == 0:
                print("Rendered", f, "/", len(frame_times), flush=True)
    finally:
        renderer.close()
        plt.close(fig)
        for v in streams:
            v.close()
    return [
        str(output / n)
        for n in [
            "01_body_muscles.mp4",
            "02_neural_chain_3d.mp4",
            "03_synchronized.mp4",
        ]
    ]
