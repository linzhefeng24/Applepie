"""Observe homologous muscle outputs and test two single-cell interventions.
Frozen physical parameters; no fitting, optimization or imposed phase waveform.
Silencing a whole neuron tests its network contribution, not one isolated edge.
"""
from pathlib import Path
import sys,json,hashlib
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parent;D=R.parent/'single-model-delivery-20261115';P=D/'build/UnifiedFlyModel'
sys.path.insert(0,str(D/'runtime/02_code'))
from flymodel import Model
m=Model(P/'01_model/model.yaml');src=P/'04_results/data/neural_state.npz'
with np.load(src,allow_pickle=False) as z:baseline={k:z[k] for k in z.files}
assert str(baseline['model_sha256'])==m.sha256
paths={'left':['10056','800003','929612','800621'],'right':['10045','800114','902520','800158']}
pairs=[('LH:tibia_extensor','RH:tibia_extensor'),('LH:pleural_remotor_and_abductor','RH:pleural_remotor_and_abductor')]
indices={v['muscle_id']:i for i,v in enumerate(m.mapping)}
record=list(dict.fromkeys([*sum(paths.values(),[]),'812953','809935']))
window=slice(400,1450)
def summarize(r):
 u=m.muscle_excitation(r);rows=[]
 for a,b in pairs:
  i,j=indices[a],indices[b];x,y=u[window,i],u[window,j]
  rows.append({'left_muscle':a,'right_muscle':b,'left_MN_ids':[m.ids[k] for k in m.mapping[i]['MN_indices']],'right_MN_ids':[m.ids[k] for k in m.mapping[j]['MN_indices']],'left_mean_u':float(x.mean()),'right_mean_u':float(y.mean()),'mean_abs_difference':float(abs(x-y).mean()),'zero_lag_correlation':float(np.corrcoef(x,y)[0,1]) if x.std()>0 and y.std()>0 else None,'MN_counts':{m.ids[k]:int(r['spikes'][window,k].sum()) for k in m.mapping[i]['MN_indices']+m.mapping[j]['MN_indices']}})
 return {'pairs':rows,'DN_spike_array_equal_baseline':bool(np.array_equal(r['spikes'][:,[m.lookup['10045'],m.lookup['10056']]],baseline['spikes'][:,[m.lookup['10045'],m.lookup['10056']]])),'run_id':str(r['run_id'])}
structure={side:[{'pre':a,'post':b,'effective_signed_count':float(m.weight[(m.pre==m.lookup[a])&(m.post==m.lookup[b])].sum())} for a,b in zip(ids[:-1],ids[1:])] for side,ids in paths.items()}
results={'baseline':summarize(baseline)}
report={'model_sha256':m.sha256,'baseline_neural_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'window_ms':[400,1450],'paths':structure,'interpretation':'Candidate active routes, not uniquely identified rhythm generator or dominant causal pathway. Amplitude asymmetry differs from anti-phase alternation. Whole-cell silencing affects all inputs/outputs and recurrent routes.','conditions':results}
(R/'report.json').write_text(json.dumps(report,indent=2)+'\n')
fig,ax=plt.subplots(4,1,figsize=(12,10),sharex=True,layout='constrained')
for side,ids in paths.items():
 for k,b in enumerate(ids):
  tt=np.flatnonzero(baseline['spikes'][:,m.lookup[b]]);ax[0 if side=='left' else 1].scatter(tt,np.full(len(tt),k),marker='|',label=b+' '+m.neurons[m.lookup[b]]['type'])
u=m.muscle_excitation(baseline)
for a in pairs[0]:ax[2].plot(np.arange(len(u)),u[:,indices[a]],label=a+' requested u')
body_path=P/'04_results/data/body_state.npz'
with np.load(body_path,allow_pickle=False) as z:
 for a in pairs[0]:ax[3].plot(z['neural_time_ms'],z['muscle_activation'][:,indices[a]],label=a+' native a')
 mask=(z['neural_time_ms']>=400)&(z['neural_time_ms']<1450)
 report['baseline_actual_activation_means']={a:float(z['muscle_activation'][mask,indices[a]].mean()) for a in pairs[0]}
for a in ax:a.legend(fontsize=8,loc='upper right');a.grid(alpha=.2);a.set_xlim(200,1500)
ax[0].set_ylabel('Left route spikes');ax[1].set_ylabel('Right route spikes');ax[2].set_ylabel('Excitation u');ax[3].set_ylabel('Native activation a');ax[3].set_xlabel('Neural time (ms)')
fig.suptitle('Existing bilateral-drive run: active candidate paths and amplitude asymmetry')
fig.savefig(R/'baseline_paths.png',dpi=140);plt.close(fig)
(R/'report.json').write_text(json.dumps(report,indent=2)+'\n')
for name,b in [('silence_left_INXXX464','929612'),('silence_right_INXXX464','902520')]:
 print('Running',name,flush=True)
 r=m.run_neural('DN_drive',record_ids=record,ablate_ids=[b]);np.savez_compressed(R/(name+'.npz'),**r)
 results[name]=summarize(r);results[name]['ablate_ids']=[b]
 (R/'report.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps(results[name],indent=2),flush=True)
print('Complete',flush=True)
