"""Inspect actual remaining inhibitory presynaptic cells after route cuts.
Ranking is a conductance-impulse proxy (counts times event peak), not measured
current contribution; necessity is assessed only by separate perturbation runs.
"""
from pathlib import Path
import sys,json
import numpy as np
R=Path(__file__).resolve().parent;P=R.parents[1]/'research/manual-full-rerun-20261119/cache/extracted/Manual_FreeBody';sys.path.insert(0,str(P/'02_code'));from flymodel import Model
m=Model(P/'01_model/model.yaml');dni=np.array([m.lookup['10045'],m.lookup['10056']]);base=np.load(P/'04_results/data/neural_state_recomputed.npz')['spikes'];result={}
for case in ['silence_GNG458','cut_top5_DN']:
 sp=np.load(R/'cache'/(case+'.npz'))['spikes'];rows=[]
 for id in m.ids:
  if id in ['26344','11006','10856','11982','516820']:continue
  i=m.lookup[id];sel=(m.pre==i)&np.isin(m.post,dni)&(m.weight<0)
  if not sel.any():continue
  g=float(-m.weight[sel].sum())*m.global_values[5]*m.cells[i,6]*m.cells[i,12];n=int(sp[200:1400,i].sum());b=int(base[200:1400,i].sum());rows.append({'id':id,'type':m.neurons[i]['type'],'predicted_nt':m.neurons[i].get('predictedNt'),'spikes':n,'baseline_spikes':b,'conductance_impulse_proxy_nS':float(g*n)})
 result[case]=sorted(rows,key=lambda x:x['conductance_impulse_proxy_nS'],reverse=True)[:15]
(R/'compensation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
