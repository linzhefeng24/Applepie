"""Test missing adult slow-MN tonic activity without a periodic input.
Persistent sodium and constant unresolved axonal bias are candidate mechanisms,
not experimental claims. Never reuse a slow flexor identity for SETi extensor.
"""
from pathlib import Path
import json,itertools
import numpy as np
from scipy.optimize import least_squares
from model import simulate
R=Path(__file__).parent;old=json.load(open(R/'results/adult-calibration.json'))['slow']['parameters'];results=[]
def measure(p):
 means=[];rate=0.
 for I in [-1.,0.,1.]:
  r=simulate(np.zeros((1,1)),['MN'],p,drive=[I]);v=r['voltage_first12'][1300:-1,0,0];means.append(float(np.mean(v)))
  if I==0.:rate=float(r['spike_counts_1ms'][650:].sum()/.35)
 return {'rmp_mV':means[1],'rin_MOhm':(means[2]-means[0])*500.,'rest_rate_hz':rate}
for gnap,bias,speed in itertools.product([.1,.3,.7],[0.,4.,12.],[.4,.7]):
 base={**old,'gNaP_nS':gnap,'axon_bias_pA':bias,'gate_speed':speed}
 def objective(x):
  p={**base,'leak_scale':float(np.exp(x[0])),'mn_leak_mV':float(x[1])};m=measure(p);return [(m['rmp_mV']+48.)/5.,(m['rin_MOhm']-700.)/700.]
 fit=least_squares(objective,[np.log(.7),-60.],bounds=([np.log(.02),-85.],[np.log(10.),-40.]),max_nfev=20,diff_step=.002)
 p={**base,'leak_scale':float(np.exp(fit.x[0])),'mn_leak_mV':float(fit.x[1])};m=measure(p);loss=((m['rmp_mV']+48.)/5.)**2+((m['rin_MOhm']-700.)/700.)**2+((m['rest_rate_hz']-30.)/15.)**2
 results.append({'parameters':p,'measured_model':m,'selection_loss':loss});(R/'results/slow-MN-tuning.json').write_text(json.dumps(results,indent=2));print('slow',gnap,bias,speed,m,'loss',round(loss,3),flush=True)
results.sort(key=lambda x:x['selection_loss']);(R/'configs/slow-MN-selected.json').write_text(json.dumps(results[0],indent=2))
