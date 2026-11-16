"""Joint-only HH→MN→muscle→white-box-physics objective with bounded drift."""
from pathlib import Path
import hashlib,io,json,os,sys,zipfile
import numpy as np
import jax
jax.config.update('jax_enable_x64',True)
import jax.numpy as j
from physics import ABPhysics
R=Path(__file__).resolve().parent;ROOT=R.parents[1]

class JointContext:
 def __init__(self):
  self.cfg=json.loads((R/'config.json').read_text());c=self.cfg
  os.environ['BPTT_CONFIG']=str(R/'neural-config.json')
  from full_hh import FullDifferentiableHH
  self.neural=FullDifferentiableHH();assert self.neural.model.sha256==c['baseline_model_sha256']
  assert hashlib.sha256(np.asarray(self.neural.model.cells).tobytes()).hexdigest()==c['manual_cell_array_sha256'],'Manual cell bank changed; do not anchor to a fitted checkpoint'
  # Original group factors equal1 in the manually tuned baseline; raw=0.
  self.reference=j.zeros((self.neural.n_groups,len(self.neural.cfg['train_fields'])),dtype=j.float64)
  assert c['start_from_manual_parameters'] and self.neural.model.sha256==c['anchor_model_sha256']
  self.bound=c['original_group_bound'];self.delta0=self.bound*j.tanh(self.reference)
  drift=c['maximum_fractional_change_from_start']
  low=j.maximum(-self.bound+1e-12,self.delta0-drift*(1+self.delta0));high=j.minimum(self.bound-1e-12,self.delta0+drift*(1+self.delta0))
  self.raw_low=j.arctanh(low/self.bound);self.raw_high=j.arctanh(high/self.bound)
  self.physics=ABPhysics(c)
  from native_whitebox import NativeWhitebox
  self.native_physics=NativeWhitebox(self.physics)
  neural_ids=[x['muscle_id'] for x in self.neural.model.mapping]
  self.order=j.asarray([neural_ids.index(x) for x in self.physics.native.muscle_ids])
 def fractional_shift(self,raw):return (self.bound*j.tanh(raw)-self.delta0)/(1+self.delta0)
 def project(self,raw):return j.clip(raw,self.raw_low,self.raw_high)
 def neural_u(self,raw):return self.neural.forward(raw,end_ms=self.cfg['neural_end_ms'])[0]
 def loss(self,raw,coefficient):
  u=self.neural_u(raw);physical_u=u[self.physics.clock_indices][:,self.order]
  qloss,aux=self.native_physics.objective(physical_u)
  shift=self.fractional_shift(raw);reg=coefficient*j.mean(shift**2)
  aux.update(joint_loss=qloss,regularization=reg,max_fractional_drift=j.max(j.abs(shift)),rms_fractional_drift=j.sqrt(j.mean(shift**2)))
  return qloss+reg,aux
