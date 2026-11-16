"""Rerun the original full hard-spike network, using two distinct saved epochs.
No retraining, target replay, imposed phase offsets, or physical rescue forces.
Only shared cell parameters receive the archived bounded BPTT factors.
"""
from pathlib import Path
import argparse, hashlib, io, json, platform, subprocess, sys, zipfile
from importlib.metadata import version
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path[:0] = [str(ROOT/'research/single-model-delivery-20261115/runtime/02_code'),
                str(ROOT/'research/conductance-rebuild-20261114')]
from flymodel import Model
from flymodel.render import render_videos
from grouped_parameters import group_key


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read_npz(z, suffix):
    name, = [n for n in z.namelist() if n.endswith(suffix)]
    with np.load(io.BytesIO(z.read(name)), allow_pickle=False) as a:
        return {k: a[k] for k in a.files}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--cache', type=Path, default=HERE/'cache')
    p.add_argument('--out', type=Path, default=HERE/'results')
    a = p.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    cp = a.cache/'bptt-checkpoint-1000-44304aa747c7.zip'
    ref = a.cache/'bptt-1000-full-validation.zip'
    assert sha(cp.read_bytes()) == '44304aa747c7078755cb16720d39a32ec839cc5e4953b47fcb3bf2fbd888fe70'
    assert sha(ref.read_bytes()) == '569e64258dac14739684725603af5c5565b762bc04b29f03d6b2985a3415b4bf'
    with zipfile.ZipFile(cp) as z:
        opt = read_npz(z, 'latest-optimizer.npz')
    assert int(opt['completed_updates']) == 1000 and int(opt['best_step']) == 123
    assert not np.array_equal(opt['raw'], opt['best_raw'])
    identity = json.loads((ROOT/'research/surrogate-bptt-20261115/input-identity.json').read_text())
    fields = [5,7,8,11,12,13,14,15,16]  # archived training configuration
    base = ROOT/'research/single-model-delivery-20261115/build/UnifiedFlyModel/01_model/model.yaml'
    reports = []
    for epoch, raw in [(123, opt['best_raw']), (1000, opt['raw'])]:
        folder = a.out/f'epoch{epoch}'
        folder.mkdir(exist_ok=True)
        m = Model(base)
        assert m.sha256 == identity['baseline_model_sha256']
        baseline = m.cells.copy()
        factors = .2*np.tanh(raw)
        groups = dict(zip(identity['groups'], factors))
        for i, row in enumerate(m.neurons):
            if group_key(row) in groups:
                m.cells[i,fields] *= 1 + groups[group_key(row)]
        if epoch == 123:
            with zipfile.ZipFile(ref) as z:
                expected = read_npz(z, 'resolved-cell-parameters.npz')['values']
            assert np.array_equal(expected, m.cells), 'Best-epoch grouping differs from independently validated parameters'
        cell_sha = sha(m.cells.tobytes())
        np.savez_compressed(folder/'resolved-cell-parameters.npz', values=m.cells,
                            raw=raw, relative_factors=factors, epoch=epoch)
        print(f'Epoch {epoch}: full hard-spike DN_drive, all cell states recorded', flush=True)
        r = m.run_neural('DN_drive')
        r['run_id'] = np.array(str(r['run_id'])+f'-epoch{epoch}-{cell_sha[:16]}')
        r['effective_cell_array_sha256'] = np.array(cell_sha)
        r['checkpoint_epoch'] = np.array(epoch)
        np.savez_compressed(folder/'neural-state.npz', **r)
        body, trace = m.simulate_body(r, fixed_root=True)
        np.savez_compressed(folder/'body-state.npz', **trace)
        assert np.isfinite(trace['qpos']).all()
        assert np.ptp(trace['thorax_position_native'], axis=0).max() == 0
        assert np.ptp(trace['thorax_quaternion'], axis=0).max() == 0
        assert trace['ground_contact_count'].max() > 0
        assert trace['ground_contact_normal_force_native'].max() > 0
        render_videos(m,r,body,trace,folder/'videos',epoch_label=f'EPOCH {epoch}')
        report = dict(epoch=epoch, role='best training objective' if epoch==123 else 'last optimizer state',
                      base_model_sha256=m.sha256, effective_cell_array_sha256=cell_sha,
                      optimizer_raw_sha256=sha(raw.tobytes()), checkpoint_sha256=sha(cp.read_bytes()),
                      changed_cells=int(np.any(m.cells!=baseline,axis=1).sum()),
                      max_relative_parameter_change=float(abs(factors).max()),
                      spikes=int(r['spikes'].sum()), fixed_body=True,
                      max_thorax_position_drift_native=float(np.ptp(trace['thorax_position_native'],axis=0).max()),
                      max_ground_contacts=int(trace['ground_contact_count'].max()),
                      max_ground_normal_force_native=float(trace['ground_contact_normal_force_native'].max()),
                      extra_applied_force=bool(trace['extra_applied_force'].any()),
                      neural_protocol='Original DN_drive; DNg100 10045/10056, 160 pA, 200–1500 ms',
                      body_duration_s=float(trace['time_s'][-1]),
                      scope='Fixed body, native legs and ground forces; not evidence of free walking or correct left/right alternation')
        (folder/'report.json').write_text(json.dumps(report,indent=2)+'\n')
        reports.append(report)
        print(json.dumps(report),flush=True)
        del m,r,body,trace
    assert reports[0]['effective_cell_array_sha256'] != reports[1]['effective_cell_array_sha256']
    ffmpeg = __import__('imageio_ffmpeg').get_ffmpeg_exe()
    comparison = a.out/'BPTT_Epoch123_vs_1000.mp4'
    subprocess.run([ffmpeg,'-y','-loglevel','error','-i',str(a.out/'epoch123/videos/01_body_muscles.mp4'),
                    '-i',str(a.out/'epoch1000/videos/01_body_muscles.mp4'),'-filter_complex','hstack=inputs=2',
                    '-c:v','libx264','-crf','20','-pix_fmt','yuv420p',str(comparison)],check=True)
    import shutil
    for epoch in (123,1000):
        shutil.copyfile(a.out/f'epoch{epoch}/videos/01_body_muscles.mp4',a.out/f'BPTT_Epoch{epoch}_FixedBody.mp4')
    for path in a.out.rglob('*.mp4'):
        subprocess.run([ffmpeg,'-v','error','-i',str(path),'-f','null','-'],check=True)
    # All videos, schematic renderings, and previews in one ZIP; large full state separately.
    for name, include in [('Videos',lambda p:p.suffix in ('.mp4','.png','.json')),
                          ('State',lambda p:p.suffix in ('.npz','.json'))]:
        with zipfile.ZipFile(a.out/f'BPTT_Epoch123_1000_{name}.zip','w',zipfile.ZIP_DEFLATED) as z:
            for path in sorted(a.out.rglob('*')):
                if path.is_file() and include(path):z.write(path,path.relative_to(a.out))
    assets = [*a.out.glob('*.mp4'),*a.out.glob('*.zip')]
    manifest = dict(code_revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                    python=platform.python_version(),versions={n:version(n) for n in ['numpy','numba','mujoco','matplotlib','imageio-ffmpeg']},
                    command=sys.argv,reports=reports, assets=[dict(name=p.name,bytes=p.stat().st_size,sha256=sha(p.read_bytes()),
                    url='https://github.com/linzhefeng24/Applepie/releases/download/fixed-body-video-20261115/'+p.name) for p in assets])
    (a.out/'BPTT_Epoch123_1000.manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')

if __name__=='__main__': main()
