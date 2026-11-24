"""运行 07_protocols/protocols.json 中的实验刺激协议。

用法:
  python 07_protocols/run_protocol.py --list
  python 07_protocols/run_protocol.py quiet_400
  python 07_protocols/run_protocol.py twentyoneA_alone
"""
import argparse
import base64
import collections
import hashlib
import io
import json
import math
import sys
import tempfile
from pathlib import Path

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '02_code'))
from flymodel import Model
from flymodel.simulator import decode
import mujoco
from native_ab import Simulation


def load_protocols():
    return json.load(open(Path(__file__).with_name('protocols.json'), encoding='utf-8'))['protocols']


def select(M, phen, spec):
    NS = M.config['neural']['neurons']
    if spec.get('chordotonal'):
        ids = [M.lookup[str(b)] for b in phen['chordotonal_body_ids'] if str(b) in M.lookup]
    elif spec.get('body_ids'):
        ids = [M.lookup[str(b)] for b in spec['body_ids'] if str(b) in M.lookup]
    else:
        ids = []
        for i, x in enumerate(NS):
            t = str(x.get('type', ''))
            if 'type_equals' in spec and t not in spec['type_equals']:
                continue
            if 'type_prefixes' in spec and not t.startswith(tuple(spec['type_prefixes'])):
                continue
            if 'superclass' in spec and str(x.get('superclass')) != spec['superclass']:
                continue
            if 'side' in spec and str(x.get('somaSide')) != spec['side']:
                continue
            ids.append(i)
    if spec.get('limit'):
        ids = ids[:int(spec['limit'])]
    return ids


def put_npz(cfg, key, arrays):
    buf = io.BytesIO()
    np.savez_compressed(buf, **arrays)
    raw = buf.getvalue()
    cfg[key] = dict(encoding='base64_npz_no_pickle',
                    sha256=hashlib.sha256(raw).hexdigest(),
                    payload=base64.b64encode(raw).decode('ascii'))


def build_model(proto, model_path):
    if not (proto.get('edge_boost') or proto.get('cell_param_boost')):
        return Model(model_path), None
    cfg = yaml.load(open(model_path, encoding='utf-8'), Loader=yaml.CSafeLoader)
    base = Model(model_path)
    NS = base.config['neural']['neurons']
    phen = json.load(open(ROOT / '03_phenomena/phenomena.json', encoding='utf-8'))
    if proto.get('cell_param_boost'):
        sb = proto['cell_param_boost']
        rec = decode(cfg['neural']['cell_parameters'])
        vals = rec['values'].copy()
        for i in select(base, phen, sb['selector']):
            for col, mul in sb['columns'].items():
                vals[i, int(col)] *= float(mul)
        rec2 = dict(encoding='base64_npz_no_pickle', sha256='', payload='')
        buf = io.BytesIO(); np.savez_compressed(buf, values=vals); raw = buf.getvalue()
        rec2['sha256'] = hashlib.sha256(raw).hexdigest()
        rec2['payload'] = base64.b64encode(raw).decode('ascii')
        cfg['neural']['cell_parameters'] = rec2
    if proto.get('edge_boost'):
        eb = proto['edge_boost']
        rec = decode(cfg['neural']['connectivity'])
        pre, post = rec['pre'], rec['post']
        cnt = rec['synapse_count'].copy()
        presel = {i for i, x in enumerate(NS)
                  if str(x.get('type', '')).startswith(tuple(eb['pre_type_prefixes']))}
        postsel = {i for i, x in enumerate(NS)
                   if str(x.get('superclass')) == eb['post_superclass']}
        mask = np.isin(pre, list(presel)) & np.isin(post, list(postsel))
        cnt[mask] *= float(eb['factor'])
        buf = io.BytesIO()
        np.savez_compressed(buf, pre=pre, post=post, synapse_count=cnt,
                            transmitter_sign=rec['transmitter_sign'])
        raw = buf.getvalue()
        cfg['neural']['connectivity'] = dict(encoding='base64_npz_no_pickle',
                                             sha256=hashlib.sha256(raw).hexdigest(),
                                             payload=base64.b64encode(raw).decode('ascii'))
    tmp = Path(tempfile.mkdtemp(prefix='flyproto_')) / 'model.yaml'
    tmp.write_text(yaml.dump(cfg, allow_unicode=True, sort_keys=False, width=100000),
                   encoding='utf-8')
    return Model(tmp), tmp


def body_metrics(M, u, duration_ms):
    names = [m['muscle_id'] for m in M.mapping]
    sim = Simulation(ROOT / '01_model/body_parameters.yaml', case='A')
    proto = sim.load_ab('A')
    so = list(sim.muscle_ids)
    u_cols = [names.index(x) for x in so]
    gid = next(i for i in range(sim.model.ngeom) if sim.model.geom(i).name == 'groundplane')
    claw = collections.defaultdict(list)
    for i in range(sim.model.ngeom):
        n = sim.model.body(int(sim.model.geom_bodyid[i])).name
        if n.startswith('walker/claw_T'):
            claw[n].append(i)
    LEG = {'LF': 'walker/claw_T1_left', 'RF': 'walker/claw_T1_right',
           'LM': 'walker/claw_T2_left', 'RM': 'walker/claw_T2_right',
           'LH': 'walker/claw_T3_left', 'RH': 'walker/claw_T3_right'}
    sim.reset('A')
    q0 = sim.data.qpos.copy()
    contacts = {k: [] for k in LEG}
    ups = []
    root_heights = []
    thorax_id = sim.model.body(M.config["body"]["thorax_name"]).id
    for k in range(4000):
        ni = min(int(np.floor(200.0 + k * 0.1 * 3.0)), len(u) - 1)
        rowu = u[ni].copy()
        for jj, vv in M.external_drive_values(k).items():
            rowu[jj] = vv
        c = proto['controls'][k].copy()
        c[sim.muscle_indices] = rowu[u_cols]
        sim.data.ctrl[:] = c
        mujoco.mj_step(sim.model, sim.data)
        if k % 50 == 0:
            cs = set()
            for ct in sim.data.contact:
                a, b = int(ct.geom1), int(ct.geom2)
                if a == gid:
                    cs.add(b)
                elif b == gid:
                    cs.add(a)
            for leg, bn in LEG.items():
                contacts[leg].append(any(x in cs for x in claw[bn]))
            ups.append(float(sim.data.xmat[thorax_id].reshape(3, 3)[2, 2]))
            root_heights.append(float(sim.data.qpos[2]))
    tcs = []
    for legs in (['LF', 'RM', 'LH'], ['RF', 'LM', 'RH']):
        sw = 1 - np.asarray([contacts[l] for l in legs], float)
        tcs.append(float(sw.all(0).sum() / sw.any(0).sum()) if sw.any().sum() else 0)
    q = sim.data.qpos
    w, x, y, z = q[3], q[4], q[5], q[6]
    yaw = math.atan2(2 * (w * z + x * y), 1 - 2 * (y * y + z * z))
    w0, x0, y0, z0 = q0[3], q0[4], q0[5], q0[6]
    yaw0 = math.atan2(2 * (w0 * z0 + x0 * y0), 1 - 2 * (y0 * y0 + z0 * z0))
    out = {'stance': {k: round(float(np.mean(v)), 2) for k, v in contacts.items()},
           'TCS': [round(t, 3) for t in tcs],
           'min_up': round(min(ups), 3),
           'min_root_height_native': round(min(root_heights), 6),
           'root_disp': [round(float(v), 4) for v in (q[:3] - q0[:3])],
           'yaw': round(float(yaw - yaw0), 4)}
    sim.close()
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('name', nargs='?')
    ap.add_argument('--list', action='store_true')
    ap.add_argument('--model', default=str(ROOT / '01_model/model.yaml'))
    args = ap.parse_args()
    P = load_protocols()
    if args.list or not args.name:
        for k, v in P.items():
            print('%-28s %s' % (k, v.get('phenomenon', '')))
        return
    if args.name not in P:
        raise SystemExit('unknown protocol: ' + args.name)
    proto = P[args.name]
    phen = json.load(open(ROOT / '03_phenomena/phenomena.json', encoding='utf-8'))
    M, tmp = build_model(proto, args.model)
    NS = M.config['neural']['neurons']
    IDS = M.ids
    MN = np.array(sorted({i for m in M.config['neuromuscular']['mapping']
                          for i in m['MN_indices']}), dtype=int)
    events = []
    for e in proto.get('events', []) + proto.get('background', []):
        ids = select(M, phen, e['selector'])
        if ids:
            events.append(dict(neuron_ids=[str(IDS[i]) for i in ids],
                               current_pA=float(e['current_pA']),
                               on_ms=float(e['on_ms']), off_ms=float(e['off_ms'])))
    dur = float(proto.get('duration_ms', 1600))
    M.config['experiments']['quiet']['duration_ms'] = dur
    r = M.run_neural('quiet', events=events, record_ids=[IDS[0]])
    sp = r['spikes']
    rate = sp[300:int(min(dur, 1500))].mean(0) * 1000 if dur > 400 else sp.mean(0) * 1000
    out = {'protocol': args.name,
           'cells': sum(len(e['neuron_ids']) for e in events),
           'total_spikes': int(sp.sum()),
           'MN_active': int((rate[MN] > 1).sum()),
           'MN_rate': round(float(rate[MN].mean()), 2) if dur > 400 else None}
    if proto.get('body'):
        out['body'] = body_metrics(M, M.muscle_excitation(r), dur)
    print(json.dumps(out, ensure_ascii=False), flush=True)
    if tmp:
        print('temp model:', tmp, flush=True)


if __name__ == '__main__':
    main()
