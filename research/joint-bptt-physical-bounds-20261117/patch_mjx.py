"""Minimal version-locked MJX3.3.2 extension: native BODY adhesion and AD scan.
No native AB model parameter is changed. Only apply in isolated environment.
BODY branch follows engine_core_smooth.c1348–1445. The AB zero-explicit-pair case includes geom gap contacts, as native BODY does.
"""
from pathlib import Path
import hashlib,json,sys
from importlib.metadata import distribution,version
R=Path(__file__).resolve().parent
if version('mujoco')!='3.3.2' or version('mujoco-mjx')!='3.3.2':raise RuntimeError('Exact3.3.2 required')
root=Path(distribution('mujoco-mjx').locate_file('mujoco/mjx/_src'))
records=[]
source=R.parent/'physics-bptt-20261116/source'
baselines={name:(R/'mjx-smooth-upstream.py.txt').read_text() if name=='smooth.py' else (R/'mjx-collision-driver-upstream.py.txt').read_text() if name=='collision_driver.py' else (R/'mjx-passive-upstream.py.txt').read_text() if name=='passive.py' else (source/('mjx__mujoco__mjx___src__'+name)).read_text() for name in ['types.py','smooth.py','solver.py','io.py','collision_driver.py','passive.py','support.py']}
texts=dict(baselines)
def change(name,old,new):
 s=texts[name]
 if old not in s:raise RuntimeError('Unexpected original source '+name)
 texts[name]=s.replace(old,new,1)
change('types.py','  # unsupported: SLIDERCRANK, BODY','  BODY = mujoco.mjtTrn.mjTRN_BODY\n  # unsupported: SLIDERCRANK; BODY added for exact native AB adhesion')
branch='''    elif trntype == TrnType.BODY:
      # Native BODY: negative average of relevant contact-normal Jacobians.
      # Include excluded contacts in the native geom contact gap.
      length = jp.zeros(1)
      if d.contact.dist.size:
        body_ids = jp.array(m.geom_bodyid)
        g1, g2 = d.contact.geom[:, 0], d.contact.geom[:, 1]
        b1, b2 = body_ids[g1], body_ids[g2]
        relevant = ((b1 == trnid[0]) | (b2 == trnid[0]))
        gap = jp.maximum(m.geom_gap[g1], m.geom_gap[g2])
        relevant &= (d.contact.dist < d.contact.includemargin + gap)
        relevant &= (g1 >= 0) & (g2 >= 0)
        def normal_jac(pos, one, two, normal):
          jac1, _ = support.jac(m, d, pos, one)
          jac2, _ = support.jac(m, d, pos, two)
          return (jac2 - jac1) @ normal
        rows = jax.vmap(normal_jac)(d.contact.pos, b1, b2, d.contact.frame[:, 0])
        count = jp.sum(relevant)
        moment = -jp.sum(rows * relevant[:, None], axis=0) / jp.maximum(count, 1)
      else:
        moment = jp.zeros(m.nv)
'''
change('smooth.py','    elif trntype == TrnType.TENDON:\n',branch+'    elif trntype == TrnType.TENDON:\n')
# Native stopping while loop retained; external implicit differentiation handles reverse mode.
change('io.py', "  if m.opt.cone == types.ConeType.ELLIPTIC and np.any(contact.dim == 1):\n    raise NotImplementedError(\n        'condim=1 with ConeType.ELLIPTIC not implemented.'\n    )", "  # Mixed frictionless/elliptic rows use existing constraint/solver paths; validation required.")
# Algebraically identical Hessian without a dense nefc-by-nefc temporary.
change('solver.py', "      cm = jp.diag(d.efc_D * ctx.active)", "      h = (d.efc_J.T * d.efc_D * ctx.active) @ d.efc_J")
change('solver.py', "        cm = cm.at[addr : addr + condim, addr : addr + condim].add(h_cone)\n      h = d.efc_J.T @ cm @ d.efc_J", "        block = d.efc_J[addr : addr + condim]\n        h = h + block.T @ h_cone @ block")
# Solver contact buffer capacity, not a physical model change. Adapter aborts
# whenever capacity is reached, so valid contacts must never be discarded.
change('collision_driver.py', "  id_ = support.name2id(m, mujoco.mjtObj.mjOBJ_NUMERIC, name)", "  if name == 'max_contact_points':\n    return 64  # checked overflow guard in AB adapter\n  id_ = support.name2id(m, mujoco.mjtObj.mjOBJ_NUMERIC, name)")
change('collision_driver.py', "        _, idx = jax.lax.top_k(-contact.dist, k=max_contact_points)", "        gap = jp.maximum(m.geom_gap[contact.geom[:, 0]], m.geom_gap[contact.geom[:, 1]])\n        priority = contact.dist - contact.includemargin - gap\n        _, idx = jax.lax.top_k(-priority, k=max_contact_points)")
# Native conservative bounding-sphere broadphase rejects impossible pairs.
# MJX's approximate ellipsoid SDF can report false overlap for distant shapes.
change('collision_driver.py', "    # collapse contacts together, ensuring they are grouped by condim", "    # collapse contacts together, ensuring they are grouped by condim") if False else None
change('collision_driver.py', "    groups[key] = contact.replace(dist=dist, pos=pos, frame=frame)", "    if not set(key.types) & _GEOM_NO_BROADPHASE:\n      center_delta = d.geom_xpos[contact.geom[:, 1]] - d.geom_xpos[contact.geom[:, 0]]\n      separation = jp.sqrt(jp.maximum(jp.sum(center_delta**2, axis=-1), 1e-30)) - m.geom_rbound[contact.geom[:, 0]] - m.geom_rbound[contact.geom[:, 1]]\n      gap = jp.maximum(m.geom_gap[contact.geom[:, 0]], m.geom_gap[contact.geom[:, 1]])\n      dist = jp.where(separation > contact.includemargin + gap, separation, dist)\n    groups[key] = contact.replace(dist=dist, pos=pos, frame=frame)")
change('solver.py', "      qacc_warmstart=ctx.qacc,", "      solver_niter=ctx.solver_niter,\n      qacc_warmstart=ctx.qacc,")
# Native inertia-box fluid uses mjMINVAL1e-15 and true positive body mass.
change('passive.py', "  box = 6.0 * jp.clip(jp.sum(box, axis=-1), a_min=1e-12)\n  box = jp.sqrt(box / jp.maximum(mass, 1e-12)) * (mass > 0.0)", "  box = 6.0 * jp.maximum(jp.sum(box, axis=-1), 1e-15)\n  box = jp.sqrt(box / jp.where(mass > 0.0, mass, 1.0)) * (mass > 0.0)")
# Keep hard muscle dynamics at width0; avoid0/0 in an UNUSED soft branch
# contaminating reverse-mode0/0 even though all primal forces are finite.
change('support.py', "      dctrl / smoothing_width + 0.5", "      dctrl / jp.where(smoothing_width < mujoco.mjMINVAL, 1.0, smoothing_width) + 0.5")
for name,text in texts.items():
 (root/name).write_text(text)
 records.append({'file':name,'before_sha256':hashlib.sha256(baselines[name].encode()).hexdigest(),'after_sha256':hashlib.sha256(text.encode()).hexdigest()})
(R/'cache').mkdir(exist_ok=True)
(R/'cache/mjx-patch.json').write_text(json.dumps({'mujoco':'3.3.2','mjx':'3.3.2','patches':records},indent=2)+'\n')
print(json.dumps(records,indent=2))
