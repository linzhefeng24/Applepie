"""Public neural interface with explicit sensory axon-terminal input compartments."""
from pathlib import Path
import sys,os,numpy as np
P=Path(os.environ.get('MANUAL_R2_PACKAGE',str(Path(__file__).resolve().parents[2]/'research/manual-full-rerun-20261119/cache/extracted/Manual_FreeBody')));sys.path.insert(0,str(P/'02_code'))
from flymodel import Model as OriginalModel
import flymodel.simulator as simulator
from terminal_dynamics import _kernel
class Model(OriginalModel):
 def __init__(self,path):
  super().__init__(path);ids=set(self.config['neural'].get('synaptic_target_compartment',{}).get('axon_terminal_body_ids',[]));self.terminal_targets=np.array([b in ids for b in self.ids]);self.exact_events=None
 def run_neural(self,*args,**kwargs):
  previous=simulator._kernel
  def call(*a):
   out=_kernel(*a,self.terminal_targets);assert not out[14],'Exact-event capacity exceeded';self.exact_events=out[13];return out[:13]
  simulator._kernel=call
  try:return super().run_neural(*args,**kwargs)
  finally:simulator._kernel=previous
