"""Full neuronal traces for manual assessment; no loss or selection score."""
from pathlib import Path
import json,numpy as np,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).parent;O=R/'results/mcns-steering';conditions=[('baseline-source-bias','Left-output PFL3'),('right-PFL3-source-bias','Right-output PFL3'),('PFL2-only-source-bias','Bilateral PFL2'),('PFL2-coactivation-source-bias','PFL2 + left-output PFL3')];fig,axes=plt.subplots(4,2,figsize=(13,11),layout='constrained')
for row,(case,label) in enumerate(conditions):
 z=np.load(O/(case+'.npz'));rec=list(z['record_body_ids']);t=z['time_ms']/1000
 for b,side,col in [('523769','L','tab:blue'),('10360','R','tab:orange')]:
  i=rec.index(b);axes[row,0].plot(t,z['voltage'][:,i,0],label='DNa02 '+side,color=col,linewidth=.6);axes[row,1].plot(t,z['currents_pA'][:,i,0],label=side+' excitatory',color=col,linewidth=.6);axes[row,1].plot(t,z['currents_pA'][:,i,1],label=side+' inhibitory',color=col,linestyle='--',linewidth=.6)
 axes[row,0].set(title=label,ylabel='Soma voltage (mV)',xlim=(0,1.4));axes[row,1].set(ylabel='Signed synaptic current (pA)',xlim=(0,1.4));axes[row,0].axvspan(.2,1.4,color='grey',alpha=.08);axes[row,0].legend(fontsize=8);axes[row,1].legend(fontsize=8,ncol=2)
axes[-1,0].set_xlabel('Time(s)');axes[-1,1].set_xlabel('Time(s)');fig.savefig(O/'manual-steering-traces.png',dpi=145);plt.close(fig)
fig,ax=plt.subplots(2,1,figsize=(11,7),layout='constrained')
for case,label in [('PFL2-coactivation','Before source adjustment'),('PFL2-coactivation-source-bias','After shared source bias +5pA')]:
 z=np.load(O/(case+'.npz'));i=list(z['record_body_ids']).index('18327');ax[0].plot(z['time_ms']/1000,z['voltage'][:,i,1],label=label,linewidth=.6)
 a=json.load(open(O/(case+'-diagnosis.json')));left=next(x for x in a['cells'] if x['type']=='DNa02' and x['side']=='L');ax[1].plot(z['time_ms']/1000,z['voltage'][:,list(z['record_body_ids']).index(left['body_id']),0],label=label,linewidth=.6)
ax[0].set(title='Locate failure at source before changing downstream readouts',ylabel='PFL3 axon voltage(mV)',xlim=(.4,1.0));ax[1].set(ylabel='Ipsilateral DNa02 soma(mV)',xlabel='Time(s)',xlim=(.4,1.0));ax[0].legend(fontsize=8);ax[1].legend(fontsize=8);fig.savefig(O/'source-adjustment-diagnosis.png',dpi=145)
