"""Manually motivated MN gain trials; original structural weights unchanged."""
from pathlib import Path
import json
import numpy as np
from network import load
from model import simulate
from metrics import summarize
R=Path(__file__).parent;p=json.load(open(R/'configs/core-selected.json'));w,roles,meta=load('motor');results=[]
for gain in [3.,6.,12.,24.,48.]:
 q={**p,'mn_gain':gain};r=simulate(w,roles,q);s=summarize(r);active=sum(x['mean_spikes_per_s']>0 and role=='MN' for x,role in zip(s['cells'],roles));rec={'mn_gain':gain,'active_MN':active,'rhythmic_MN':s['rhythmic_MN'],'summary':s};results.append(rec);print('Gain',gain,'active',active,'rhythmic',s['rhythmic_MN'],flush=True)
 (R/'results/motor-gain-trials.json').write_text(json.dumps(results,indent=2))
 # Retain every tested result so later selection is auditable.
 np.savez_compressed(R/'results'/f'motor-gain-{gain:g}.npz',spikes=r['spike_counts_1ms'],voltage=r['voltage_first12'],body_ids=[int(x['bodyId']) for x in meta])
# Favor recruitment, but do not assume more recruited cells proves correctness.
best=max(results,key=lambda r:(r['rhythmic_MN'],-r['mn_gain']));q={**p,'mn_gain':best['mn_gain']};(R/'configs/motor-selected.json').write_text(json.dumps(q,indent=2))
