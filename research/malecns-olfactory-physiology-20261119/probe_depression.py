"""Analytic event-driven check of published ORN-PN resource dynamics.
This is a local equation check, not a replay of published recordings or network fit.
No physiological numbers are hard-coded: read the evidence and protocol YAMLs.
"""
from pathlib import Path
import csv,json,math
import yaml
R=Path(__file__).resolve().parent
p={x['id']:x for x in yaml.safe_load((R/'parameter-evidence.yaml').read_text())['parameters']}
protocol=yaml.safe_load((R/'protocols.yaml').read_text())['ORN_PN_depression'];rows=[];checks=[]
for name,ids in protocol['components'].items():
 f=p[ids['f_parameter']]['value'];tau=p[ids['recovery_parameter']]['value'];assert 0<f<1 and tau>0
 for rate in protocol['rates_Hz']:
  dt=1000/rate;q=math.exp(-dt/tau);a=1.0;fixed=(1-q)/(1-f*q)
  for pulse in range(protocol['pulse_count']):
   rows.append({'component':name,'rate_Hz':rate,'pulse':pulse+1,'time_ms':pulse*dt,'resource_before_spike':a});a=1-(1-f*a)*q
  last=rows[-1]['resource_before_spike'];residual=abs(a-(1-(1-f*last)*q));assert residual<1e-12
  checks.append({'component':name,'rate_Hz':rate,'analytic_asymptote':fixed,'last_pulse_resource':last,'all_states_bounded':all(0<=x['resource_before_spike']<=1 for x in rows),'note':'f is remaining fraction, not depleted fraction'})
with (R/'depression-probe.csv').open('w') as file:
 writer=csv.DictWriter(file,fieldnames=rows[0],lineterminator="\n");writer.writeheader();writer.writerows(rows)
(R/'depression-probe.json').write_text(json.dumps({'status':'local analytic equation check only','cases':checks},indent=2)+'\n');print(json.dumps(checks,indent=2))
