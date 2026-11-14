"""Burst-envelope rhythm separated from tonic spike-train autocorrelation."""
import numpy as np
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks,periodogram

def rhythm(counts,start_ms=400,min_cycles=4):
 x=np.asarray(counts,dtype=float)[start_ms:];smooth=gaussian_filter1d(x,5.)*1000
 peaks,props=find_peaks(smooth,distance=35,prominence=max(3.,.15*np.ptp(smooth)))
 if len(peaks)>1:
  intervals=np.diff(peaks);freq=1000./np.median(intervals);cv=np.std(intervals)/np.mean(intervals)
 else:freq=0.;cv=1.
 f,p=periodogram(smooth,fs=1000.);band=(f>=3)&(f<=30);osc=(f>=3)&(f<=60);fraction=float(p[band].sum()/max(p[osc].sum(),1e-12))
 # A regular tonic train must not pass merely because it has spikes or harmonics.
 modulation=float((np.percentile(smooth,95)-np.percentile(smooth,10))/max(np.mean(smooth),1.))
 valid=bool(len(peaks)>=min_cycles and 5<=freq<=25 and cv<.30 and modulation>.75 and fraction>.55)
 return {'rhythmic':valid,'burst_frequency_hz':float(freq),'interburst_cv':float(cv),'envelope_modulation':modulation,'band_power_fraction':fraction,'envelope_peaks':len(peaks),'mean_spikes_per_s':float(x.sum()/max(len(x)*.001,1e-12))}

def summarize(result):
 c=result['spike_counts_1ms'];out=[rhythm(c[:,j],int(max(400,result['config']['onset_ms']+200))) for j in range(c.shape[1])]
 return {'numerical_failure':result['numerical_failure'],'cells':out,'rhythmic_cells':sum(x['rhythmic'] for x in out),'rhythmic_MN':sum(x['rhythmic'] and r=='MN' for x,r in zip(out,result['roles']))}
