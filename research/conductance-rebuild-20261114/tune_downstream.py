"""Guided adjustment after diagnosing intact-network feedforward inhibition.
Keeps all source edges; fits only shared conductance per inhibitory population.
A missing physiological gain is not a license to relabel an anatomical sign.
"""
from pathlib import Path
import json,time
import numpy as np
from network import load
from model import simulate
from metrics import summarize
R=Path(__file__).parent;p=json.load(open(R/'configs/motor-selected.json'));p['I1_gain']=1.;w,roles,meta=load('onehop');records=[]
for inh in [.03,.06,.12,.25,.5]:
 q={**p,'inhibitory_gain':inh};r=simulate(w,roles,q);s=summarize(r);rec={'parameters':q,'summary':s,'rhythmic_core':sum(s['cells'][j]['rhythmic'] for j in [1,2]),'scope':'onehop','neurons':len(w)};records.append(rec);print('Other inhibition',inh,'core',rec['rhythmic_core'],'rhythmic MN',s['rhythmic_MN'],flush=True)
 (R/'results/downstream-tuning.json').write_text(json.dumps(records,indent=2));np.savez_compressed(R/'results'/f'onehop-inh-{inh:g}.npz',spikes=r['spike_counts_1ms'],voltage=r['voltage_first12'],body_ids=[int(x['bodyId']) for x in meta])
best=max(records,key=lambda r:(r['rhythmic_core'],r['summary']['rhythmic_MN']));(R/'configs/downstream-selected.json').write_text(json.dumps(best['parameters'],indent=2))
