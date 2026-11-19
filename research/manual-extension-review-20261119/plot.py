"""Direct core voltage/current traces and actual muscle excitation, no behavioral proxy."""
from pathlib import Path
import json,numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parent
names=[x for x in ['DN_drive','core_release_x2','E1_silenced','E2_silenced'] if (R/'results'/f'{x}.npz').exists()]
fig,ax=plt.subplots(len(names),3,figsize=(16,3.3*len(names)),squeeze=False)
for row,name in enumerate(names):
 z=np.load(R/'results'/f'{name}.npz');ids=z['body_ids'].tolist();rec=z['record_indices'].tolist();t=z['time_ms'];colors=['tab:blue','tab:orange','tab:green']
 for bid,c in zip(['800173','800863','801884'],colors):
  j=rec.index(ids.index(bid));ax[row,0].plot(t,z['voltage'][:,j,0],label=bid,color=c,lw=.7)
 j=rec.index(ids.index('800173'));ax[row,1].plot(t,z['currents_pA'][:,j,0],label='E1 excitatory synaptic',color='red',lw=.6);ax[row,1].plot(t,z['currents_pA'][:,j,1],label='E1 inhibitory synaptic',color='green',lw=.6)
 ax[row,2].imshow(z['u'].T,aspect='auto',origin='lower',extent=[0,1600,0,130],vmin=0,vmax=1,cmap='magma');ax[row,0].set_ylabel(name+'\nsoma mV');ax[row,1].set_ylabel('pA');ax[row,2].set_ylabel('muscle channel');ax[row,0].legend(fontsize=7);ax[row,1].legend(fontsize=7)
 for a in ax[row]:a.set_xlabel('neural time (ms)')
fig.suptitle('Candidate extension; borrowed priors; not experimental validation');fig.tight_layout();fig.savefig(R/'core-and-muscle-traces.png',dpi=150)
