from pathlib import Path
import json,numpy as np
from model import simulate
R=Path(__file__).parent;cal=json.load(open(R/'results/adult-calibration.json'));profiles={'fast':cal['fast']['parameters'],'intermediate':json.load(open(R/'configs/intermediate-adult-selected.json'))['parameters'],'slow':json.load(open(R/'configs/slow-tonic-selected.json'))['parameters']};out={}
for kind,p in profiles.items():
 rows=[]
 for I in [0.,5.,10.,20.,40.,80.,160.,320.,640.]:
  r=simulate(np.zeros((1,1)),['MN'],p,drive=[I]);rows.append({'current_pA':I,'rate_hz':float(r['spike_counts_1ms'][600:].sum()/.4),'numerical_failure':r['numerical_failure']})
 out[kind]={'parameters':p,'fI':rows,'first_tested_current_with_rate_ge5Hz':next((a['current_pA'] for a in rows if a['rate_hz']>=5.),None)}
print({k:v['first_tested_current_with_rate_ge5Hz'] for k,v in out.items()},flush=True);(R/'results/adult-fI.json').write_text(json.dumps(out,indent=2))
