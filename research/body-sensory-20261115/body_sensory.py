"""Read actual MuJoCo mechanics; no contact-derived force is called strain or SI.

All ground-contact pairs contribute an equal/opposite world force on the leg.
Normal forces sum magnitudes (compression); tangential forces sum vectors before
norm. Feet are distal tarsal/claw geoms, with other leg contacts kept separately.
The load signal uses force/body-weight in the same native units, avoiding an
unsupported mass/force unit conversion. No neural feedback to motor is implied.
"""
import numpy as np
LEGS=('LF','LM','LH','RF','RM','RH')
def leg_of(name):
 for side,letter in [('left','L'),('right','R')]:
  for segment,suffix in [('T1','F'),('T2','M'),('T3','H')]:
   if segment+'_'+side in name:return letter+suffix
 return None

def sample_mechanics(model,data):
 import mujoco
 normal=np.zeros(6);foot_normal=normal.copy();world=np.zeros((6,3));tangent=world.copy();contacts=np.zeros(6,dtype=int)
 ground=mujoco.mj_name2id(model,mujoco.mjtObj.mjOBJ_GEOM,'groundplane')
 for k in range(data.ncon):
  c=data.contact[k];g1,g2=int(c.geom1),int(c.geom2)
  if ground not in (g1,g2):continue
  other=g2 if g1==ground else g1;name=model.geom(other).name;leg=leg_of(name)
  if leg is None:continue
  i=LEGS.index(leg);f=np.zeros(6);mujoco.mj_contactForce(model,data,k,f)
  # contact frame rows are normal/tangents; force is on geom2.
  sign=1. if g1==ground else -1.;fw=sign*c.frame.reshape(3,3).T@f[:3];ft=sign*c.frame.reshape(3,3)[1:].T@f[1:3]
  normal[i]+=max(0.,f[0]);world[i]+=fw;tangent[i]+=ft;contacts[i]+=int(f[0]>0.)
  if 'tars' in name:foot_normal[i]+=max(0.,f[0])
 q=[];v=[]
 for leg in LEGS:
  suffix={'F':'T1','M':'T2','H':'T3'}[leg[1]]+'_'+('left' if leg[0]=='L' else 'right');j=model.joint('walker/tibia_'+suffix);q.append(data.qpos[j.qposadr[0]]);v.append(data.qvel[j.dofadr[0]])
 weight=model.body_mass.sum()*np.linalg.norm(model.opt.gravity)
 return dict(knee_deg=np.rad2deg(q),knee_velocity_deg_s=np.rad2deg(v),ground_normal_native=normal,foot_normal_native=foot_normal,ground_world_force_native=world,ground_tangent_force_native=tangent,contact_count=contacts,load_bodyweights=normal/weight,foot_load_bodyweights=foot_normal/weight)

def transduce(mechanics,p):
 """Functional currents, NOT measured receptor channels or strain reconstruction.
 angle convention must be independently calibrated before anatomical claims.
 """
 q=np.asarray(mechanics['knee_deg']);v=np.asarray(mechanics['knee_velocity_deg_s']);load=np.asarray(mechanics['load_bodyweights']);touch=np.asarray(mechanics['foot_load_bodyweights'])
 if not all(np.isfinite(x).all() for x in (q,v,load,touch)) or np.any(load<0) or np.any(touch<0):raise ValueError('Invalid mechanics')
 hook=np.stack((np.maximum(-v,0),np.maximum(v,0)),axis=-1)*p['hook_pA_per_deg_s']
 claw=np.stack((np.maximum(p['neutral_knee_deg']-q,0),np.maximum(q-p['neutral_knee_deg'],0)),axis=-1)*p['claw_pA_per_deg']
 # Saturating compression/touch proxies, not calibrated receptor firing rates.
 load_i=p['load_max_pA']*load/(p['load_half_bodyweights']+load)
 touch_i=p['touch_max_pA']*touch/(p['touch_half_bodyweights']+touch)
 current=np.concatenate((hook,claw),axis=-1)
 if 'proprio_max_pA' in p:current=p['proprio_max_pA']*current/(p['proprio_max_pA']+current)
 return dict(proprio_current_pA=current,load_current_pA=load_i,touch_current_pA=touch_i)
