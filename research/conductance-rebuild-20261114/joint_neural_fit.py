"""Measured BON1 waveform + independent MDN response, shared-type HH tuning.
No body/gait objective. All unsuccessful candidates remain in results.
"""
from pathlib import Path
import json,hashlib,sys,time
import numpy as np
from scipy import sparse
from scipy.optimize import least_squares
from scipy.signal import lfilter
from grouped_parameters import group_key
from network import simulate_network
if '--historical-method-only' not in sys.argv:
 raise SystemExit('Stopped by user method correction: use trace_manual_network.py and inspect mechanisms; this rejected loss-selection method is retained for provenance only.')
R=Path(__file__).parent;O=R/'results/joint-neural-fit';O.mkdir(exist_ok=True);P=R/'results/experimental-panel'
D=np.genfromtxt(R/'data/experimental-source/BON1-ED5e.csv',delimiter=',',names=True);data=np.column_stack([D[f'BRK_brain{i}'] for i in range(1,7)]);control=np.column_stack([D[f'control_brain{i}'] for i in range(1,6)]);relative=D['time_relative_stimulus_s'];sample_t=(relative+2)*1000
# Per-brain baseline removal uses only pre-stimulus samples. Mean control is a
# measured comparator, never converted to spike targets.
data=data-data[relative<0].mean(axis=0);control=control-control[relative<0].mean(axis=0);train=data[:,:4].mean(axis=1);held=data[:,4:].mean(axis=1);amp=max(np.ptp(train),1.);base=json.load(open(R/'configs/adult-network-selected.json'));base.update(dt_ms=.0125,duration_ms=7001.,onset_ms=2000.,group_parameters={});protocol=json.load(open(P/'protocol.json'));meta=json.load(open(P/'BRK_BON1-neurons.json'));W=sparse.load_npz(P/'BRK_BON1-connectivity.npz').toarray();roles=['MN' if x['class']=='motor neuron' else 'other' for x in meta];source=[i for i,x in enumerate(meta) if x['bodyId'] in ['10788','10564']];target=[i for i,x in enumerate(meta) if x['bodyId'] in ['10441','10348']];key=group_key(meta[target[0]])

def readout(ca,t,q):
 # Finite binding kinetics after saturating intracellular-Ca occupancy.
 # Gain/Kd/tau are fluorescence nuisance parameters, not arbitrary time traces.
 gain,kd,tau=np.exp(q);occupancy=ca/(kd+ca);alpha=np.exp(-.5/tau);filtered=lfilter([1-alpha],[1,-alpha],occupancy);pred=np.interp(sample_t,t,filtered);pred-=pred[relative<0].mean();return gain*pred

def fit_indicator(ca,t):
 residual=lambda q:(readout(ca,t,q)-train)/amp
 res=least_squares(residual,np.log([10.,.03,300.]),bounds=(np.log([.1,1e-6,10.]),np.log([100.,100.,3000.])),max_nfev=120)
 return res.x,readout(ca,t,res.x)

# Manual mechanistic candidates first: prolonged Ca retention, weaker SK,
# changing Ca influx and synaptic gain; all parameters share within type.
candidates=[('baseline',100.,1.,1.,1.,1.),('Ca300',300.,1.,1.,1.,1.),('Ca1000',1000.,1.,1.,1.,1.),('Ca2000',2000.,1.,1.,1.,1.),('Ca3000',3000.,1.,1.,1.,1.),('Ca1000_weakSK',1000.,.5,1.,1.,1.),('Ca2000_weakSK',2000.,.5,1.,1.,1.),('Ca2000_lessCa',2000.,1.,.5,1.,1.),('Ca3000_lessCa',3000.,1.,.5,1.,1.),('Ca2000_moreExc',2000.,1.,1.,1.5,1.),('Ca3000_lessExc',3000.,1.,1.,.75,1.),('Ca2000_slowerGates',2000.,1.,1.,1.,.85)]
records=[]
for name,ca_tau,sk,gca,exc,gate in candidates:
 p={**base,'group_parameters':{key:{'calcium_tau_ms':ca_tau,'SK_scale':sk,'gCa_nS':.3*gca,'excitatory_gain':exc,'gate_speed':gate}}};wave=np.zeros((7002,len(meta)));wave[2000:4000,source]=160.;r=simulate_network(W,roles,meta,p,drive_waveform=wave);n=r['valid_record_count'];t=r['record_time_ms'];ca=r['calcium_first12_uM'][:n,target].mean(axis=1);q,pred=fit_indicator(ca,t);score=float(np.sqrt(np.mean((pred-train)**2))/amp);ho=float(np.sqrt(np.mean((pred-held)**2))/max(np.ptp(held),1.));row={'name':name,'parameters':p,'parameter_sha256':hashlib.sha256(json.dumps(p,sort_keys=True).encode()).hexdigest(),'indicator_gain_Kd_uM_tau_ms':np.exp(q).tolist(),'train_NRMSE':score,'holdout_NRMSE':ho,'numerical_failure':r['numerical_failure'],'objective_for_selection':'train NRMSE only; held-out brains are reported, never used for selection','target_peak_mean_rate_hz':float(r['spike_counts_1ms'][2000:4000,target].sum()/4)};records.append(row);np.savez_compressed(O/(name+'.npz'),spikes=r['spike_counts_1ms'],calcium=ca,time_ms=t,predicted_dff=pred,target_train=train,target_heldout=held,data_time_relative_s=relative,voltage=r['voltage_first12']);(O/'trials.json').write_text(json.dumps(records,indent=2));print(name,'train',round(score,4),'held',round(ho,4),flush=True)
selected=min((x for x in records if not x['numerical_failure']),key=lambda x:x['train_NRMSE']);(O/'selected.json').write_text(json.dumps(selected,indent=2));(R/'configs/joint-neural-selected.json').write_text(json.dumps(selected['parameters'],indent=2));print('Selected',selected['name'],flush=True)
