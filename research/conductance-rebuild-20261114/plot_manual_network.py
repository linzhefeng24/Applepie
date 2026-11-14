"""Inspect actual circuit traces; no automated fit or pass/fail score."""
from pathlib import Path
import csv,json,sys
import numpy as np,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).parent;O=R/'results/manual-mechanism';mode=sys.argv[1] if len(sys.argv)>1 else 'direct-baseline';z=np.load(O/(mode+'.npz'));meta={x['bodyId']:x for x in json.load(open(O/'neurons.json'))};idx={str(b):i for i,b in enumerate(z['body_ids'])};legs=['LF','LM','LH','RF','RM','RH'];sides=['LHS']*3+['RHS']*3;segments=['T1','T2','T3']*2;types=['IN17A001','INXXX466','IN16B036','IN19A007'];cols=['tab:red','tab:orange','tab:blue','tab:purple'];cross=list(csv.DictReader((R/'data/model-130-channel-candidate-crosswalk.csv').open(encoding='utf-8-sig')));T=np.load(R/'data/old-A-muscle-targets.npz');targidx={str(x):i for i,x in enumerate(T['muscle_ids'])};fig,ax=plt.subplots(6,2,figsize=(13,13),layout='constrained')
for n,(leg,side,seg) in enumerate(zip(legs,sides,segments)):
 for j,(typ,col) in enumerate(zip(types,cols)):
  bids=[b for b,x in meta.items() if x['type']==typ and x['somaSide']==side and x['somaNeuromere']==seg]
  for b in bids:
   if b not in idx:continue
   counts=z['spikes'][:,idx[b]];times=np.repeat(np.arange(len(counts)),counts.astype(int));ax[n,0].vlines(times/1000,j,j+.7,color=col,linewidth=.7)
 ax[n,0].set(yticks=np.arange(4)+.35,yticklabels=['E1','E2','I1','I2'],ylabel=leg,xlim=(.2,1.6))
 for term,col in [('Ti flexor','tab:red'),('Ti extensor','tab:blue')]:
  channels=[i for i,x in enumerate(cross) if x['leg']==leg and x['candidate_target_labels']==term]
  if channels:
   ax[n,1].plot(np.arange(len(z['u']))/1000,z['u'][:,channels].mean(axis=1),color=col,label=term)
   jj=[targidx[cross[i]['model_channel']] for i in channels if cross[i]['model_channel'] in targidx]
   if jj:ax[n,1].plot(.4+T['time_s']*3,T['target_u'][:len(T['time_s']),jj].mean(axis=1) if len(T['target_u'])==len(T['time_s']) else np.interp(T['time_s'],np.arange(len(T['target_u']))*float(T['dt_s']),T['target_u'][:,jj].mean(axis=1)),color=col,alpha=.25,linestyle='--')
 ax[n,1].set(xlim=(.2,1.6),ylim=(-.02,1.02),ylabel=leg+' u')
ax[0,0].set_title('Real six-leg core spikes; no imposed phases');ax[0,1].set_title('Causal MN→u; faint target is globally stretched x3');ax[0,1].legend(fontsize=8);ax[-1,0].set_xlabel('Neural time (s)');ax[-1,1].set_xlabel('Neural time (s)');fig.savefig(O/(mode+'-routes.png'),dpi=145);plt.close(fig)
record=[str(b) for b in z['record_body_ids']];fig,ax=plt.subplots(4,1,figsize=(12,10),layout='constrained');j=record.index('10707');k=record.index('11751');t=z['time_ms']/1000
for i,l in [(j,'LF E1'),(k,'LF E2')]:ax[0].plot(t,z['voltage'][:,i,0],label=l,linewidth=.6)
ax[0].set(ylabel='Soma mV',xlim=(.4,.9));ax[0].legend()
for i,label in [(j,'E1'),(k,'E2')]:
 ax[1].plot(t,z['currents_pA'][:,i,0],label=label+' excitatory',linewidth=.6);ax[1].plot(t,z['currents_pA'][:,i,1],label=label+' inhibitory',linewidth=.6)
ax[1].set(ylabel='Signed synaptic pA',xlim=(.4,.9));ax[1].legend(fontsize=8)
for i,l in [(j,'E1'),(k,'E2')]:ax[2].plot(t,z['conductances_nS'][:,i,0],label=l+' exc');ax[2].plot(t,z['conductances_nS'][:,i,1],label=l+' inh')
ax[2].set(ylabel='Synaptic nS',xlim=(.4,.9));ax[2].legend(fontsize=8)
for i,l in [(j,'E1'),(k,'E2')]:ax[3].plot(t,z['calcium'][:,i],label=l)
ax[3].set(ylabel='Model Ca uM',xlabel='Time(s)',xlim=(.4,.9));ax[3].legend();fig.savefig(O/(mode+'-currents.png'),dpi=145)
