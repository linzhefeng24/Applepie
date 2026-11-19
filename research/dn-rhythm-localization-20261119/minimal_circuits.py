"""Unfitted circuit reconstitution tests, preserving actual edge weights/cell rows."""
from pathlib import Path
import sys,json
import numpy as np
R=Path(__file__).resolve().parent;ROOT=R.parents[1];P=ROOT/'research/manual-full-rerun-20261119/cache/extracted/Manual_FreeBody';sys.path.insert(0,str(P/'02_code'));from flymodel import Model
from flymodel.dynamics import _kernel
from experiment import summary
m=Model(P/'01_model/model.yaml');s=m.config['neural']['solver'];proto=m.config['experiments']['DN_drive'];dn=['10045','10056'];groups={'DNge129':['11006','10856'],'GNG127':['11982','516820'],'GNG458':['26344']};cases={'DN_only':dn,'DN_DNge129':dn+groups['DNge129'],'DN_GNG127':dn+groups['GNG127'],'DN_top5':dn+sum(groups.values(),[]),'left_DN_one_DNge129':['10045','11006'],'left_DN_one_GNG127':['10045','11982']};reports=[]
for name,ids in cases.items():
 inds=np.array([m.lookup[x] for x in ids]);lookup={v:i for i,v in enumerate(inds)};sel=np.isin(m.pre,inds)&np.isin(m.post,inds);pre=np.array([lookup[i] for i in m.pre[sel]],np.int32);post=np.array([lookup[i] for i in m.post[sel]],np.int32);w=m.weight[sel];offset=np.r_[0,np.cumsum(np.bincount(pre,minlength=len(ids)))];wave=np.zeros((round(proto['duration_ms']/s['input_sample_ms'])+1,len(ids)))
 for e in proto['events']:
  for id in e['neuron_ids']:
   if id in ids:wave[round(e['on_ms']/s['input_sample_ms']):round(e['off_ms']/s['input_sample_ms']),ids.index(id)]=e['current_pA']
 n=len(ids);out=_kernel(n,pre,post,w,np.zeros(n),np.zeros(n),np.zeros(n,dtype=np.bool_),s['dt_ms'],round(proto['duration_ms']/s['dt_ms']),0,round(s['delay_ms']/s['dt_ms']),m.global_values,m.cells[inds],round(s['record_interval_ms']/s['dt_ms']),wave,s['input_sample_ms'],np.arange(n,dtype=np.int64),offset,m.kinetics,m.aux);assert not out[5]
 d={'case':name,'ids':ids,'neural_parameters_unchanged':True,'edges':len(w),'results':{id:summary(out[0],i,s['spike_bin_ms']) for i,id in enumerate(ids)}};reports.append(d);print(name,{id:{'count':v['spike_count'],'onsets':v['burst_onsets_ms']} for id,v in d['results'].items()},flush=True)
(R/'minimal-circuits.json').write_text(json.dumps({'scope':'candidate small-loop sufficiency; no fits; failure does not disprove necessity in whole network','cases':reports},ensure_ascii=False,indent=2)+'\n')
