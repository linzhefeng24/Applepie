from pathlib import Path
import json,itertools
import numpy as np
from model import simulate
R=Path(__file__).parent;base=json.load(open(R/'results/adult-calibration.json'))['slow']['parameters'];rows=[]
for scale,el,speed in itertools.product([.3,.5,.7],[-48.,-45.,-42.],[.4,.45,.5]):
 p={**base,'leak_scale':scale,'mn_leak_mV':el,'gate_speed':speed,'gNaP_nS':.1,'axon_bias_pA':40.};means=[];rate=0.
 for I in [-1.,0.,1.]:
  out=simulate(np.zeros((1,1)),['MN'],p,drive=[I]);means.append(float(out['voltage_first12'][1300:-1,0,0].mean()))
  if I==0:rate=float(out['spike_counts_1ms'][650:].sum()/.35)
 m={'mean_soma_mV':means[1],'differential_Rin_MOhm':(means[2]-means[0])*500.,'rest_rate_hz':rate};loss=((m['mean_soma_mV']+48.)/5)**2+((m['differential_Rin_MOhm']-700)/700)**2+((rate-30)/10)**2
 rows.append({'parameters':p,'measured_model':m,'selection_loss':loss})
rows.sort(key=lambda x:x['selection_loss']);(R/'results/slow-rest-grid.json').write_text(json.dumps(rows,indent=2));(R/'configs/slow-tonic-selected.json').write_text(json.dumps(rows[0],indent=2));print(json.dumps(rows[0]['measured_model']),rows[0]['selection_loss'],flush=True)
