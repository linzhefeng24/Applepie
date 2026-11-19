"""Named core-to-MN routes with actual spike times and candidate muscle mappings."""
from pathlib import Path
import json,sys,numpy as np
R=Path(__file__).resolve().parent;P=R.parents[1]/'research/manual-full-rerun-20261119/cache/extracted/Manual_FreeBody';sys.path.insert(0,str(P/'02_code'));from flymodel import Model
m=Model(R/'cache/extended_model.yaml');s=np.load(R/'results/DN_drive.npz')['spikes'];mapping={}
for q in m.mapping:
 for i in q['MN_indices']:mapping.setdefault(i,[]).append(q['muscle_id'])
rows=[]
for bid in ['800173','800288','800863','903216','801884','803183']:
 i=m.lookup[bid];mask=(m.pre==i)&np.array([m.neurons[j].get('superclass')=='vnc_motor' for j in m.post]);ix=np.flatnonzero(mask);ix=ix[np.argsort(-np.abs(m.weight[ix]))]
 for k in ix[:12]:
  j=m.post[k];rows.append({'source':bid,'source_type':m.neurons[i]['type'],'MN':m.ids[j],'MN_type':m.neurons[j]['type'],'signed_effective_count':float(m.weight[k]),'source_spike_times_ms':np.flatnonzero(s[:,i]).tolist(),'target_spike_times_ms':np.flatnonzero(s[:,j]).tolist(),'candidate_muscles':mapping.get(int(j),[]),'interpretation':'structural direct route with observed coactivity; timing alone does not prove this edge caused spikes'})
(R/'core_to_MN_observations.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n');print('direct routes',len(rows),'with candidate muscles',sum(bool(x['candidate_muscles']) for x in rows))
