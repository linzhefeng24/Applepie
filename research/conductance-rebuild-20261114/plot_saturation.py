"""Compare actual saved poses; no pose correction or interpolation."""
from pathlib import Path
import numpy as np,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
O=Path(__file__).parent/'results/asymmetry';fig,ax=plt.subplots(2,1,figsize=(10,6),layout='constrained')
z=np.load(O/'long-body-guarded.npz');ax[0].plot(z['time_s'],np.rad2deg(z['tibia_angle_rad'][:,3]),label='Original fixed readout');ax[1].plot(z['time_s'],z['upright'],label='Original fixed readout')
for filename,label in [('saturation-scale-0.75.npz','Gain x0.75'),('saturation-scale-0.5.npz','Gain x0.5'),('saturation-mean-scale-0.5.npz','Gain x0.5, constant mean input')]:
 if not (O/filename).exists():continue
 z=np.load(O/filename);ax[0].plot(z['time_s'],np.rad2deg(z['RF_angle_rad']),label=label);ax[1].plot(z['time_s'],z['upright'],label=label)
ax[0].axvspan(.4,1,color='grey',alpha=.1);ax[0].set(ylabel='RF tibia angle (deg)',title='Uniform gain reduction: actual single-leg movement, not six-leg walking');ax[0].legend(fontsize=8);ax[1].axhline(.8,color='grey',linestyle='--');ax[1].set(xlabel='Body time (s)',ylabel='Body up z');fig.savefig(O/'saturation-comparison.png',dpi=150)
