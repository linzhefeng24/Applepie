"""Exact named-cell spike timelines for local rhythm and convergent inputs."""
from pathlib import Path
import json,os,numpy as np
os.environ.setdefault('MPLCONFIGDIR','/tmp/core-bypass-mpl')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parent
COLORS={'DNg100':'black','E1':'#cc3434','E2':'#e07020','E3':'#a438a4','I1':'#259245'}
def raster(ax,case,rows,xlim):
 z=np.load(R/'results'/f'{case}.npz');ids=z['body_ids'].tolist();ev=z['events_step_cell'];labels=[]
 for row,(bid,name) in enumerate(rows):
  t=(ev[ev[:,1]==ids.index(bid),0]+1)*.0125;t=t[(t>=xlim[0])&(t<=xlim[1])];ax.vlines(t,row-.25,row+.25,color=COLORS.get(name.split()[0],'#444'),lw=.65);labels.append(name+' '+bid)
 ax.set_yticks(range(len(rows)),labels,fontsize=8);ax.set_xlim(*xlim);ax.set_ylim(-.6,len(rows)-.4);ax.invert_yaxis();ax.set_xlabel('neural time (ms)');ax.set_title(case,fontsize=10)
rows=[('10056','DNg100'),('800173','E1'),('800863','E2'),('801884','I1')]
fig,ax=plt.subplots(3,1,figsize=(13,8.5));raster(ax[0],'T1L_core3_4s',rows,(200,3900));raster(ax[1],'T1L_core3',rows,(500,1500));raster(ax[2],'T1L_core3_cut_feedback',rows,(500,1500));fig.suptitle('Four-cell diagnostic: tonic fast DN spikes, feedback-dependent slow core activity\nBorrowed membrane priors; no MN/body simulation in these reduced conditions',fontsize=11);fig.tight_layout();fig.savefig(R/'local-core-rhythm.png',dpi=150);plt.close(fig)
rows=[('800863','E2 left'),('800216','E3 left'),('801884','I1 left'),('903216','E2 right'),('801061','E3 right'),('803183','I1 right')]
fig,ax=plt.subplots(4,1,figsize=(13,10));
for a,case in zip(ax,['baseline','cut_E2_I1','cut_E3_I1','cut_E2_E3_I1']):raster(a,case,rows,(200,1500))
fig.suptitle('Convergent E2 direct and IN19B012 relay inputs to I1\nCuts apply to the listed type pairs across the selected network, not just one T1 pair',fontsize=11);fig.tight_layout();fig.savefig(R/'I1-convergent-routes.png',dpi=150);plt.close(fig)
rows=[('10056','DNg100'),('800286','INXXX464'),('800061','left MN'),('10045','DNg100'),('11074','DNg13'),('802072','right MN')]
fig,ax=plt.subplots(3,1,figsize=(13,8));
for a,case in zip(ax,['E2_silenced','E2_silenced_cut_DN_MN','E2_silenced_cut_DN_and_right_DNs_MN']):raster(a,case,rows,(200,255))
fig.suptitle('Concrete parallel routes to promotor MN: initial response timeline',fontsize=11);fig.tight_layout();fig.savefig(R/'MN-bypass-timelines.png',dpi=150);plt.close(fig)
