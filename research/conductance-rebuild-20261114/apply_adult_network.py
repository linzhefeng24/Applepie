"""Transfer accepted adult intermediate exemplar to unknown-subtype MNs as
an explicit reference model, not a claimed cell-specific subtype assignment."""
from pathlib import Path
import json
from model import simulate
from network import load
from metrics import summarize
R=Path(__file__).parent;profile=json.load(open(R/'configs/intermediate-adult-selected.json'));p=json.load(open(R/'configs/necessity-selected.json'));p['mn_profile']={k:profile['parameters'][k] for k in ['leak_scale','mn_leak_mV','coupling_nS','gNaP_nS','axon_bias_pA','gate_speed']};p['mn_profile_scope']='Unknown EM MN subtype: use adult intermediate reference, not a verified assignment';w,roles,meta=load('onehop');abl=[j for j,x in enumerate(meta) if x['type']=='INXXX466'];rows=[]
for gain in [1.,3.,6.,12.,24.]:
 q={**p,'mn_gain':gain};a=summarize(simulate(w,roles,q));b=summarize(simulate(w,roles,q,ablate=abl));loss=a['rhythmic_MN']-5*b['rhythmic_MN'];rows.append({'parameters':q,'baseline':a,'E2_silenced':b,'selection_score':loss});print('Adult MN gain',gain,'MN',a['rhythmic_MN'],'E2 residual',b['rhythmic_MN'],flush=True);(R/'results/adult-network-gains.json').write_text(json.dumps(rows,indent=2))
rows.sort(key=lambda x:(x['E2_silenced']['rhythmic_MN']==0,all(x['baseline']['cells'][j]['rhythmic'] for j in [1,2]),x['baseline']['rhythmic_MN']),reverse=True);(R/'configs/adult-network-selected.json').write_text(json.dumps(rows[0]['parameters'],indent=2))
