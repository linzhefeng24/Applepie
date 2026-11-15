"""Inspect measured BON1 fluorescence and fixed-observation-model predictions.
No optimizer or scalar loss. Peak normalization compares shape, not amplitude;
GCaMP binding and intracellular calcium removal remain non-identifiable here.
"""
from pathlib import Path
import json,hashlib,sys
import numpy as np
from scipy.signal import lfilter
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).parent;O=R/'results/bon1-timecourse';O.mkdir(exist_ok=True);csv=R/'data/experimental-source/BON1-ED5e.csv';raw=np.genfromtxt(csv,delimiter=',',names=True);t=raw['time_relative_stimulus_s'];brains=np.array([raw[n] for n in raw.dtype.names if n.startswith('BRK_')]).T;controls=np.array([raw[n] for n in raw.dtype.names if n.startswith('control_')]).T;mean=brains.mean(axis=1);sem=brains.std(axis=1,ddof=1)/np.sqrt(brains.shape[1]);observed=(mean-mean[t<0].mean());scale=observed.max();fig,axs=plt.subplots(3,1,figsize=(9,10));axs[0].plot(t,mean,label='Measured BRK brains n=6');axs[0].fill_between(t,mean-sem,mean+sem,alpha=.2);axs[0].plot(t,controls.mean(axis=1),label='Measured control brains n=5');axs[0].set_ylabel('Published fluorescence units');axs[1].plot(t,observed/scale,'k.-',label='Measured mean / peak');details=[];arrays={'measured_time_s':t,'measured_brains':brains,'measured_controls':controls}
folders=sys.argv[1:] or ['bon1-local-r5','bon1-local-BON1Ca3000']
for folder in folders:
 path=R/'results'/('frozen-neural-panel-'+folder)/'BRK2s.npz';d=np.load(path);cfg=json.load(open(path.with_name('BRK2s-config.json')));target=[list(d['record_body_ids']).index(b) for b in cfg['selected_body_ids']['BON1']];ca=d['calcium'][:,target].mean(axis=1);tm=(d['time_ms']-2000)/1000.;occupancy=ca**2/(.15**2+ca**2);a=np.exp(-np.median(np.diff(d['time_ms']))/600.);indicator=lfilter([1-a],[1,-a],occupancy);indicator-=indicator[tm<0].mean();peak=indicator.max();axs[1].plot(tm,indicator/max(peak,1e-12),label=folder+' fixed binding proxy');axs[2].plot(tm,ca,label=folder);arrays[folder+'_time_s']=tm;arrays[folder+'_calcium_uM']=ca;arrays[folder+'_indicator']=indicator;details.append({'result_folder':folder,'raw_result_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bank_sha256':cfg['bank_sha256'],'raw_Ca_peak_uM':float(ca.max()),'indicator_peak_arbitrary_units':float(peak)})
for ax in axs:
 ax.axvspan(0,2,color='red',alpha=.08);ax.set_xlim(-2,5);ax.grid(alpha=.15);ax.legend(fontsize=7)
axs[1].set_ylabel('Peak-normalized shape only');axs[2].set_ylabel('Actual model intracellular Ca (uM)');axs[2].set_xlabel('Seconds relative to BRK stimulus onset');fig.suptitle('Measured BON1 response and manual calcium hypothesis; no fitted indicator or loss');fig.tight_layout();fig.savefig(O/'manual-timecourse.png',dpi=150);plt.close(fig);np.savez_compressed(O/'manual-timecourse.npz',**arrays);(O/'manual-timecourse.json').write_text(json.dumps({'method':__doc__,'source_data_sha256':hashlib.sha256(csv.read_bytes()).hexdigest(),'source_DOI':'10.1038/s41586-024-07854-7','fixed_observation_prior':{'Kd_uM':.15,'Hill_coefficient':2.,'binding_tau_ms':600.,'status':'illustrative uncalibrated observation prior, not a measured indicator fit'},'runs':details,'interpretation':'Neither a quantitative calcium fit nor proof of a uniquely identified biological removal time. Compare full rise and after-stimulus trace manually.'},indent=2)+'\n');print('Saved manual timecourse comparison')
