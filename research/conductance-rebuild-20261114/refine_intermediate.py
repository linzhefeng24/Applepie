"""Reject unconstrained depolarized-leak fit; add a candidate NaP mechanism
and constrain leak reversal before rechecking adult MN physiology."""
from pathlib import Path
import json,itertools
import numpy as np
from scipy.optimize import least_squares
from model import simulate,DEFAULT
R=Path(__file__).parent;records=[]
def measure(p):
 means=[];rate=0.
 for I in [-1.,0.,1.]:
  o=simulate(np.zeros((1,1)),['MN'],p,drive=[I]);means.append(float(o['voltage_first12'][1300:-1,0,0].mean()))
  if I==0:rate=float(o['spike_counts_1ms'][650:].sum()/.35)
 return {'rmp_mV':means[1],'rin_MOhm':(means[2]-means[0])*500.,'rest_rate_hz':rate}
for nap,gc in itertools.product([.3,1.,3.],[1.,4.,12.]):
 base={**DEFAULT,'rin_mn_MOhm':300.,'duration_ms':1000.,'onset_ms':200.,'gNaP_nS':nap,'coupling_nS':gc}
 def objective(x):
  m=measure({**base,'leak_scale':float(np.exp(x[0])),'mn_leak_mV':float(x[1])});return [(m['rmp_mV']+60.)/5.,(m['rin_MOhm']-300.)/300.]
 f=least_squares(objective,[0.,-60.],bounds=([np.log(.02),-85.],[np.log(10.),-45.]),max_nfev=30,diff_step=.002);p={**base,'leak_scale':float(np.exp(f.x[0])),'mn_leak_mV':float(f.x[1])};m=measure(p);loss=sum(np.array(objective(f.x))**2)+(m['rest_rate_hz']/10)**2
 records.append({'parameters':p,'measured_model':m,'loss':float(loss)});(R/'results/intermediate-refinement.json').write_text(json.dumps(records,indent=2));print('intermediate',nap,gc,m,loss,flush=True)
records.sort(key=lambda x:x['loss']);(R/'configs/intermediate-adult-selected.json').write_text(json.dumps(records[0],indent=2))
