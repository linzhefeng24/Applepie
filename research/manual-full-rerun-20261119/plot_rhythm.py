"""Scientific diagnostic plot in neural time; no model state is modified."""
from pathlib import Path
import sys,json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parent;P=R/'cache/extracted/Manual_FreeBody';sys.path.insert(0,str(P/'02_code'))
from flymodel import Model
m=Model(P/'01_model/model.yaml');z=np.load(P/'04_results/data/neural_state_recomputed.npz');t=z['time_ms'];curr=z['currents_pA'];sp=z['spikes'];cut=json.loads((R/'DN-feedback-cut.json').read_text())
fig,ax=plt.subplots(3,1,figsize=(11,8),sharex=True,layout='constrained')
i=m.lookup['10045'];ax[0].plot(t,curr[:,i,3],label='External tonic current');ax[0].plot(t,curr[:,i,0],label='Excitatory input',alpha=.8);ax[0].plot(t,curr[:,i,1],label='Inhibitory input',alpha=.8);ax[0].set_ylabel('DNg100 input (pA)');ax[0].legend(loc='upper right',ncol=3,fontsize=8)
ids=['10045','11006','11982','800009','800061'];labels=['DNg100 10045','DNge129 11006','GNG127 11982','IN17A001 800009','Promotor MN 800061']
for k,(id,label) in enumerate(zip(ids,labels)):
 times=np.where(sp[:,m.lookup[id]])[0];ax[1].vlines(times,k-.35,k+.35,linewidth=.8)
ax[1].set_yticks(range(len(ids)),labels);ax[1].set_title('Original manual full network')
for k,id in enumerate(['10045','800009','800061']):ax[2].vlines(cut['selected_neurons'][id]['spike_times_ms'],k-.35,k+.35,linewidth=.8)
ax[2].set_yticks(range(3),['DNg100 10045','IN17A001 800009','Promotor MN 800061']);ax[2].set_title('Only incoming DNg100 synapses removed; all other edges retained');ax[2].set_xlabel('Neural time (ms); not physical or playback time')
for a in ax:a.set_xlim(180,1420);a.grid(alpha=.2)
fig.savefig(R/'DN-rhythm-diagnostic.png',dpi=170)
