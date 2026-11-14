"""Adult flexor MN class exemplars, not assignments of unknown EM cells.
Fit somatic zero-drive mean and small-current differential resistance in the
active HH simulation. Slow tonic rate is tested separately, never inferred from
Rin or from fast/slow extensor names. No extra liquid-junction correction.
"""
from pathlib import Path
import json
import numpy as np
from scipy.optimize import least_squares
from model import simulate,DEFAULT
R=Path(__file__).parent;targets={'fast':{'rin':150.,'rmp':-68.,'rest_rate':0.},'intermediate':{'rin':300.,'rmp':-60.,'rest_rate':0.},'slow':{'rin':700.,'rmp':-48.,'rest_rate':30.}}
results={}
def measure(p):
 v=[];rates=[]
 for I in [-1.,0.,1.]:
  r=simulate(np.zeros((1,1)),['MN'],p,drive=[I]);a=r['voltage_first12'][:,0,0];good=a[int(650/r['record_interval_ms']):-1];v.append(float(np.mean(good)));rates.append(float(r['spike_counts_1ms'][650:].sum()/.35))
 return {'rmp_mV':v[1],'rin_MOhm':(v[2]-v[0])*500.,'rest_rate_hz':rates[1]}
for kind,t in targets.items():
 base={**DEFAULT,'duration_ms':1000.,'onset_ms':200.,'drive_pA':0.,'rin_mn_MOhm':t['rin'],'mn_leak_mV':t['rmp']}
 def fun(x):
  p={**base,'leak_scale':float(np.exp(x[0])),'mn_leak_mV':float(x[1]),'coupling_nS':float(np.exp(x[2]))};m=measure(p)
  return [(m['rmp_mV']-t['rmp'])/5.,(m['rin_MOhm']-t['rin'])/t['rin'],(x[2]-np.log(12.))*.005]
 fit=least_squares(fun,[0.,t['rmp'],np.log(12.)],bounds=([np.log(.01),-85.,np.log(.05)],[np.log(10.),-20.,np.log(30.)]),max_nfev=60,diff_step=.001)
 p={**base,'leak_scale':float(np.exp(fit.x[0])),'mn_leak_mV':float(fit.x[1]),'coupling_nS':float(np.exp(fit.x[2]))};m=measure(p)
 results[kind]={'source':'Azevedo et al., eLife.56754; adult tibia flexor classes','target':t,'measured_model':m,'parameters':p,'resistance_relative_error':abs(m['rin_MOhm']/t['rin']-1),'rmp_error_mV':abs(m['rmp_mV']-t['rmp']),'rest_rate_error_hz':abs(m['rest_rate_hz']-t['rest_rate']),'optimizer_success':bool(fit.success),'scope':'Unassigned class exemplar; mean somatic potential is not necessarily identical to experimental RMP during spiking.'}
 (R/'results/adult-calibration.json').write_text(json.dumps(results,indent=2));print(kind,m,'target',t,flush=True)
