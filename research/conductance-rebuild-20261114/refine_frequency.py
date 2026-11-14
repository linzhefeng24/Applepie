"""Explicit synaptic-integration trials for intact-network frequency failure.
Preserve area approximately when changing excitatory decay; no direct oscillator
frequency parameter or periodic drive is supplied. These amplitudes are TRAINING
conditions, so later full-network probes are separately labelled validation.
"""
from pathlib import Path
import json,numpy as np
from model import simulate
from network import load
from metrics import summarize
R=Path(__file__).parent;p=json.load(open(R/'configs/adult-network-selected.json'));w,roles,meta=load('onehop');records=[]
for tau in [3.,7.5,10.,15.]:
 q={**p,'tau_e_decay_ms':tau,'ge_nS_per_synapse':p['ge_nS_per_synapse']*5./tau,'duration_ms':1200.};conditions=[]
 for drive in [120.,160.,200.,240.]:
  z={**q,'drive_pA':drive};s=summarize(simulate(w,roles,z));conditions.append({'drive':drive,'summary':s});print('tau',tau,'drive',drive,'core f',[round(s['cells'][j]['burst_frequency_hz'],2) for j in [1,2]],flush=True)
 f=[np.mean([c['summary']['cells'][j]['burst_frequency_hz'] for j in [1,2]]) for c in conditions];valid=all(c['summary']['cells'][j]['rhythmic'] for c in conditions for j in [1,2]);positive=bool(np.all(np.diff(f)>0))
 records.append({'parameters':q,'conditions':conditions,'core_frequencies':f,'all_rhythmic':valid,'strictly_increasing':positive,'note':'induced onehop training graph; not intact-network proof'});(R/'results/frequency-refinement.json').write_text(json.dumps(records,indent=2))
