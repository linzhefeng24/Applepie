from pathlib import Path
import json,numpy as np
from model import simulate,DEFAULT
from metrics import summarize
R=Path(__file__).parent;p=json.load(open(R/'configs/core-selected.json'));p['dt_ms']=.003125;W=np.load(R/'data/core.npz')['weights'];roles=['DN','E1','E2','I1','I2'];records=[]
for key in ['ge_nS_per_synapse','gi_nS_per_synapse','tau_e_decay_ms','tau_i_decay_ms','coupling_nS','c_soma_pF','gNa_nS','gK_nS']:
 for scale in [.9,1.1]:
  q={**p,key:p.get(key,DEFAULT[key])*scale};s=summarize(simulate(W,roles,q));records.append({'parameter':key,'factor':scale,'summary':s,'core_periodicity_preserved':all(s['cells'][j]['rhythmic'] for j in [1,2])})
(R/'results/fine-core-robustness.json').write_text(json.dumps({'dt_ms':p['dt_ms'],'tests':records,'passed':sum(x['core_periodicity_preserved'] for x in records),'total':16},indent=2));(R/'configs/core-fine-selected.json').write_text(json.dumps(p,indent=2));p=json.load(open(R/'configs/adult-network-selected.json'));p['dt_ms']=.003125;p['duration_ms']=1000.;(R/'configs/adult-network-fine.json').write_text(json.dumps(p,indent=2));print('Fine core robustness',sum(x['core_periodicity_preserved'] for x in records),'/16',flush=True)
cal=json.load(open(R/'results/adult-calibration.json'));profiles={'fast':cal['fast']['parameters'],'intermediate':json.load(open(R/'configs/intermediate-adult-selected.json'))['parameters'],'slow':json.load(open(R/'configs/slow-tonic-selected.json'))['parameters']};out={}
for kind,params in profiles.items():
 q={**params,'dt_ms':.003125};means=[];rates=[]
 for I in [-1.,0.,1.]:
  r=simulate(np.zeros((1,1)),['MN'],q,drive=[I]);means.append(float(r['voltage_first12'][1300:-1,0,0].mean()));rates.append(float(r['spike_counts_1ms'][650:].sum()/.35))
 out[kind]={'config':q,'mean_soma_mV':means[1],'differential_Rin_MOhm':(means[2]-means[0])*500.,'rest_rate_hz':rates[1]};print('Fine adult',kind,out[kind]['differential_Rin_MOhm'],rates[1],flush=True)
(R/'results/adult-fine-physiology.json').write_text(json.dumps(out,indent=2))
