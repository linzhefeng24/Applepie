"""Explicit, recorded parameter trials. No fabricated/injected oscillator signal."""
from pathlib import Path
import json,time,itertools
import numpy as np
from model import simulate,DEFAULT
from metrics import summarize
ROOT=Path(__file__).parent;W=np.load(ROOT/'data/core.npz')['weights'];ROLES=['DN','E1','E2','I1','I2']
trials=[];start=time.time()
# A deliberate grid changes conductance gain and synaptic recovery time;
# every sampled value is a declared unknown, not an adult measurement.
for ge,gi,ti in itertools.product([.009,.012,.018,.027,.045,.075,.11],[.012,.025,.05,.10],[15.,30.,50.]):
 p=dict(ge_nS_per_synapse=ge,gi_nS_per_synapse=gi,tau_i_decay_ms=ti)
 r=simulate(W,ROLES,p);s=summarize(r);n=sum(s['cells'][j]['rhythmic'] for j in [1,2]);f=np.mean([s['cells'][j]['burst_frequency_hz'] for j in [1,2]])
 score=100*n-abs(f-11.)-sum(s['cells'][j]['interburst_cv'] for j in [1,2])*5
 trials.append({'trial':len(trials),'parameters':p,'summary':s,'score':score})
 if len(trials)%28==0:
  (ROOT/'results/core-grid-progress.json').write_text(json.dumps(trials,indent=2));print('Core trials',len(trials),'elapsed',round(time.time()-start,1),flush=True)
trials.sort(key=lambda x:-x['score']);evaluated=[]
for row in trials[:12]:
 p=row['parameters'];abl={};stable=0
 for name,cells in [('E1',[1]),('E2',[2]),('I1',[3]),('I2',[4]),('both_inhibitors',[3,4])]:
  s=summarize(simulate(W,ROLES,p,ablate=cells));abl[name]=s
 for key in ['ge_nS_per_synapse','gi_nS_per_synapse','tau_e_decay_ms','tau_i_decay_ms','coupling_nS','c_soma_pF','gNa_nS','gK_nS']:
  for scale in [.9,1.1]:
   q=p.copy();q[key]=q.get(key,DEFAULT[key])*scale;s=summarize(simulate(W,ROLES,q));stable+=all(s['cells'][j]['rhythmic'] for j in [1,2])
 necessity=not abl['E1']['cells'][2]['rhythmic'] and not abl['E2']['cells'][1]['rhythmic'];redundant=abl['I1']['cells'][1]['rhythmic'] and abl['I2']['cells'][1]['rhythmic']
 row={**row,'ablation':abl,'robustness_passed':int(stable),'robustness_total':16,'excitatory_necessity':bool(necessity),'single_inhibitor_redundancy':bool(redundant)};row['selection_score']=row['score']+stable*3+30*necessity+15*redundant;evaluated.append(row)
 print('Candidate',row['trial'],'robustness',stable,'necessity',necessity,'redundancy',redundant,flush=True)
 evaluated.sort(key=lambda x:-x['selection_score']);(ROOT/'results/core-selection-progress.json').write_text(json.dumps(evaluated,indent=2))
chosen=evaluated[0];p=DEFAULT.copy();p.update(chosen['parameters']);(ROOT/'configs/core-selected.json').write_text(json.dumps(p,indent=2));(ROOT/'results/core-grid.json').write_text(json.dumps(trials,indent=2));(ROOT/'results/core-selection.json').write_text(json.dumps(evaluated,indent=2));print('SELECTED',json.dumps(chosen['parameters']),chosen['robustness_passed'],flush=True)
