"""Summarize saved independent simulations; never replace failed outcomes."""
from pathlib import Path
import json,numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parent;O=R/'results/asymmetry'
coarse=json.loads((O/'long-body-guarded-validation.json').read_text());fine=json.loads((O/'long-body-guarded-fine-validation.json').read_text())
s={'source':'independently rerun model experiments; not recovered historical parameters','minimum_single_leg_motion_supported':True,'six_leg_walking_validated':False,'all_130_trajectory_recovered':False,'precise_amplitude_convergence_established':False,'fine_E2_residual_periodic_MN':1,'analysis_window_s':[.4,1.0],'shared_neural_change':{'Ti flexor MN gate_speed_multiplier':.85},'readout':'20 ms causal filter and fixed fitted nonnegative channel gains; asymmetry is not attributable to connectivity alone','coarse':coarse,'fine':fine,'SK_hypothesis':'extensor SK_scale=0.5 failed to remove residual: E2=1, baseline=42 periodic MN'}
(O/'summary.json').write_text(json.dumps(s,indent=2))
fig,ax=plt.subplots(3,1,figsize=(10,9),layout='constrained')
for case,label in [('guarded','Rhythmic input'),('guarded_mean','Constant mean'),('guarded_E2','E2 ablated'),('guarded_fine','Rhythmic, finer neural step')]:
 z=np.load(O/f'long-body-{case}.npz');t=z['time_s'];x=np.rad2deg(z['tibia_angle_rad'][:,3]);ax[0].plot(t,x,label=label,linewidth=1);sel=t>=.4;ax[1].plot(t[sel],x[sel]-x[sel].mean(),label=label,linewidth=1)
ax[0].axvspan(.4,1,color='grey',alpha=.12);ax[0].set(ylabel='RF tibia angle (deg)',title='Actual free-body simulation: one-leg assay, not six-leg walking');ax[0].legend(fontsize=8);ax[1].set(ylabel='RF angle minus window mean (deg)',xlabel='Body time (s)')
z=np.load(O/'long-body-guarded.npz')
for j,l in [(38,'RF flexor'),(39,'RF extensor'),(13,'LF flexor'),(14,'LF extensor')]:ax[2].plot(z['time_s'],z['activation'][:,j],label=l,linewidth=1)
ax[2].set(xlabel='Body time (s)',ylabel='Actual muscle activation');ax[2].legend(fontsize=8);fig.savefig(O/'asymmetry-validation.png',dpi=160)
brain=json.loads((R/'brain.json').read_text());brain['grouped_motion_experiment_20261114']={'status':'partial model validation','summary':'results/asymmetry/summary.json','report':'ASYMMETRY.md','minimum_single_leg_motion_supported':True,'six_leg_walking_validated':False,'fine_E2_residual_periodic_MN':1};(R/'brain.json').write_text(json.dumps(brain,ensure_ascii=False,indent=2)+'\n')
