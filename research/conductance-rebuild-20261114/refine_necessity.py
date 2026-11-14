"""Manual diagnostic grid: reject candidates that merely recruit more MNs
while retaining autonomous oscillatory outputs after E2 silencing.
Explicit held-out intact-network tests remain required.
"""
from pathlib import Path
import json,itertools
import numpy as np
from model import simulate
from network import load
from metrics import summarize
R=Path(__file__).parent;p=json.load(open(R/'configs/downstream-selected.json'));w,roles,meta=load('onehop');records=[];abl=[i for i,x in enumerate(meta) if x['type']=='INXXX466'];p['duration_ms']=1200.
for bg,gain,sk in itertools.product([.1,.25,.5],[12.,24.],[.1,1.]):
 q={**p,'background_exc_gain':bg,'mn_gain':gain,'mn_SK_scale':sk};a=summarize(simulate(w,roles,q));b=summarize(simulate(w,roles,q,ablate=abl));rec={'parameters':q,'baseline':a,'E2_silenced':b,'score':a['rhythmic_MN']-5*b['rhythmic_MN']+30*all(a['cells'][j]['rhythmic'] for j in [1,2])};records.append(rec)
 (R/'results/necessity-refinement.json').write_text(json.dumps(records,indent=2));print('bg,gain,SK',bg,gain,sk,'MN',a['rhythmic_MN'],'E2 residual',b['rhythmic_MN'],'core',[a['cells'][j]['rhythmic'] for j in [1,2]],flush=True)
records.sort(key=lambda x:-x['score']);(R/'configs/necessity-selected.json').write_text(json.dumps(records[0]['parameters'],indent=2))
