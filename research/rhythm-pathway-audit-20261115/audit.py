"""Descriptive audit of recorded DN/MN/muscle signals, not a causal CPG test."""
from pathlib import Path
import hashlib,json,sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parent;D=R.parent/'single-model-delivery-20261115';P=D/'build/UnifiedFlyModel'
sys.path.insert(0,str(D/'runtime/02_code'))
from flymodel import Model
m=Model(P/'01_model/model.yaml');path=P/'04_results/data/neural_state.npz'
with np.load(path,allow_pickle=False) as z:r={k:z[k] for k in z.files}
s=r['spikes'];u=m.muscle_excitation(r)
dn_times=np.flatnonzero(s[:,m.lookup['10045']]);starts=dn_times[np.r_[True,np.diff(dn_times)>50]]
period=float(np.median(np.diff(starts)))
selected=['RM:sternal_anterior_rotator','RF:FlyMimic:LFC_pleural_remotor_and_abductor','LM:tibia_extensor']
roots=m.neuron_ids(type='DNg100');details=[]
fig,ax=plt.subplots(3,1,figsize=(12,8),sharex=True,layout='constrained')
for k,b in enumerate(roots):
 i=m.lookup[b];tt=np.flatnonzero(s[:,i]);ax[0].scatter(tt,np.full(len(tt),k),s=12,marker='|',label=f'DNg100 {b}')
for j,name in enumerate(selected):
 mi=next(k for k,v in enumerate(m.mapping) if v['muscle_id']==name);entry=m.mapping[mi];edges=[]
 for i in entry['MN_indices']:
  tt=np.flatnonzero(s[:,i]);ax[1].scatter(tt,np.full(len(tt),j),s=12,marker='|',label=f'MN {m.ids[i]} -> {name}')
  for b in roots:
   mask=(m.pre==m.lookup[b])&(m.post==i)
   if np.any(mask):edges.append({'pre':b,'post':m.ids[i],'signed_count_times_efficacy':float(m.weight[mask].sum()),'structural_edge_only':True})
 ax[2].plot(np.arange(len(u)),u[:,mi],label=name)
 details.append({'muscle':name,'candidate_MN_ids':[m.ids[i] for i in entry['MN_indices']],'direct_DNg100_edges':edges,'mapping_status':entry['status']})
for a in ax:a.axvspan(200,1500,color='gold',alpha=.08);a.legend(fontsize=8,loc='upper right');a.grid(alpha=.2)
ax[0].set_ylabel('DN spikes');ax[1].set_ylabel('MN spikes');ax[2].set_ylabel('Muscle requested u');ax[2].set_xlabel('Neural time (ms)');ax[2].set_xlim(0,1600)
fig.suptitle('Recorded constant-DN-input run: descriptive activity, not proof of CPG causality')
fig.savefig(R/'signals.png',dpi=140);plt.close(fig)
d={'scope':'new descriptive audit of the actual delivered run; no parameters changed','model_sha256':m.sha256,'neural_input_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'neural_run_id':str(r['run_id']),'stimulus':m.config['experiments']['DN_drive'],'DN10045_burst_starts_ms_gap_rule_50ms':starts.tolist(),'descriptive_median_burst_interval_ms':period,'descriptive_envelope_frequency_Hz':1000/period,'active_requested_channels':int((u.max(0)>0).sum()),'examples':details,'observations':['Repeated bursts reach candidate MN pools and produce time-varying muscle excitation.','Several example muscles show coincident activity packets; coordinated six-leg phase relationships are not established.','The active graph contains direct excitatory DNg100-to-example-MN routes.'],'not_established':['Identity of a local CPG as the source of the activity packets.','Whether direct DN-to-MN input, intrinsic DN dynamics or intermediate recurrent circuitry is necessary.','Causal necessity of specific intermediate cells or E1/E2/I1/I2 in this model.'],'required_causal_tests':['Matched baseline versus selective removal of direct DN-to-MN transmission.','Selective silencing of identified rhythm intermediates while monitoring downstream currents, spikes and u.','Matched synaptic-path perturbations and phase/delay traces, retaining the same DN input and neuromuscular parameters.']}
(R/'report.json').write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(d,indent=2))
