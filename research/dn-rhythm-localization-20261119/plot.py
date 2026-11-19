from pathlib import Path
import json,sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parent;P=R.parents[1]/'research/manual-full-rerun-20261119/cache/extracted/Manual_FreeBody';sys.path.insert(0,str(P/'02_code'));from flymodel import Model
m=Model(P/'01_model/model.yaml');z=np.load(P/'04_results/data/neural_state_recomputed.npz');sp=z['spikes'];fig,axes=plt.subplots(3,1,figsize=(12,10),layout='constrained')
ids=['10045','11982','516820','10856','11006','26344','800061'];names=['DNg100 10045','GNG127 11982','GNG127 516820','DNge129 10856','DNge129 11006','GNG458 26344','MN 800061']
for k,id in enumerate(ids):axes[0].vlines(np.where(sp[:,m.lookup[id]])[0],k-.35,k+.35)
axes[0].set_yticks(range(len(ids)),names);axes[0].set_xlim(195,420);axes[0].set_title('Original manual network: first burst and delayed feedback')
cases=['baseline','cut_DNge129_DN','cut_GNG127_DN','cut_GNG458_DN','cut_top5_DN','cut_all_inhibitory_DN']
for k,name in enumerate(cases):
 ts=np.where(sp[:,m.lookup['10045']])[0] if name=='baseline' else json.loads((R/(name+'.json')).read_text())['neurons']['10045']['spike_times_ms'];axes[1].vlines(ts,k-.35,k+.35)
axes[1].set_yticks(range(len(cases)),cases);axes[1].set_xlim(195,1400);axes[1].set_title('DNg100 10045: route cuts')
for k,name in enumerate(['i_decay_15ms','baseline','i_decay_60ms']):
 ts=np.where(sp[:,m.lookup['10045']])[0] if name=='baseline' else json.loads((R/(name+'.json')).read_text())['neurons']['10045']['spike_times_ms'];axes[2].vlines(ts,k-.35,k+.35)
axes[2].set_yticks(range(3),['Global inhibitory decay15ms','Original30ms','Global inhibitory decay60ms']);axes[2].set_xlim(195,1400);axes[2].set_title('DNg100: temporal-scale perturbation, not optimization');axes[2].set_xlabel('Neural time (ms); physical clock and video playback differ')
for a in axes:a.grid(alpha=.2)
fig.savefig(R/'localization.png',dpi=160)
