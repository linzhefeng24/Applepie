"""Descriptive environment perturbation review, without a scalar fitting score."""
from pathlib import Path
import hashlib,json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from body_sensory import transduce,LEGS
R=Path(__file__).parent;p=json.load(open(R/'parameters.json'));cases=['A-ground','B-ground','A-no-ground','A-gravity-1.5'];fig,axs=plt.subplots(4,3,figsize=(14,11),sharex=True);rows=[]
for row,case in enumerate(cases):
 z=np.load(R/'results'/case/'body-sensory.npz');s=transduce(z,p);t=z['time_s'];d=json.load(open(R/'results'/case/'manifest.json'))
 for i,leg in enumerate(LEGS):
  axs[row,0].plot(t,z['knee_deg'][:,i],label=leg);axs[row,1].plot(t,z['ground_normal_native'][:,i]);axs[row,2].plot(t,s['load_current_pA'][:,i])
 axs[row,0].set_ylabel(case);rows.append({'case':case,'mean_total_ground_force_native':float(z['ground_normal_native'].sum(1).mean()),'max_total_ground_force_native':float(z['ground_normal_native'].sum(1).max()),'per_leg_mean_load_current_pA':s['load_current_pA'].mean(0).tolist(),'per_leg_mean_touch_current_pA':s['touch_current_pA'].mean(0).tolist(),'max_load_bodyweights':z['load_bodyweights'].max(0).tolist(),'all_signals_finite':all(np.isfinite(z[k]).all() for k in z.files if k!='legs')})
for ax,title in zip(axs[0],['Actual knee coordinate (deg)','Ground normal force (native)','Functional load current (pA)']):ax.set_title(title)
axs[0,0].legend(ncol=3)
for ax in axs.flat:ax.grid(alpha=.2)
for ax in axs[-1]:ax.set_xlabel('Time (s)')
fig.suptitle('Archived muscle replay interacting with the simulated environment');fig.tight_layout();fig.savefig(R/'results/body-environment.png',dpi=150);(R/'results/environment-review.json').write_text(json.dumps({'status':'rerun mechanics; receptor currents uncalibrated; no implication of behavioral reproduction','parameter_sha256':hashlib.sha256((R/'parameters.json').read_bytes()).hexdigest(),'conditions':rows},indent=2)+'\n');print(rows)
