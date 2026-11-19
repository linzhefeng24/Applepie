"""Diagnose tonic-current versus DN output bursting in the reproduced manual model.
Use exactly the packaged kernel and selected manual cell rows. Isolate the two
DNg100 cells by removing all network edges; optionally remove their SK current
only for a clearly labelled acute mechanistic perturbation, not optimization.
"""
from pathlib import Path
import sys,json
import numpy as np
R=Path(__file__).resolve().parent;P=R/'cache/extracted/Manual_FreeBody';sys.path.insert(0,str(P/'02_code'))
from flymodel import Model
from flymodel.dynamics import _kernel
m=Model(P/'01_model/model.yaml');s=m.config['neural']['solver'];events=m.config['experiments']['DN_drive'];ids=['10045','10056'];ii=np.asarray([m.lookup[x] for x in ids]);wave=np.zeros((round(events['duration_ms']/s['input_sample_ms'])+1,len(ids)))
for e in events['events']:
 for id in e['neuron_ids']:
  wave[round(e['on_ms']/s['input_sample_ms']):round(e['off_ms']/s['input_sample_ms']),ids.index(id)]=e['current_pA']
with np.load(P/'04_results/data/neural_state_recomputed.npz') as z:full=z['spikes'].copy()
def summarize(spikes,index):
 times=np.repeat(np.arange(len(spikes))*s['spike_bin_ms'],spikes[:,index].astype(int));times=times[(times>=200)&(times<1400)];onsets=times[np.r_[True,np.diff(times)>60]] if len(times) else times
 return {'spike_times_ms':times.tolist(),'burst_grouping_gap_ms':60,'burst_onsets_ms':onsets.tolist(),'burst_start_intervals_ms':np.diff(onsets).tolist(),'note':'60ms only separates observed short intraburst and long interburst gaps; not a fitted or training parameter'}
out={'input_protocol':events,'full_network':{id:summarize(full,i) for id,i in zip(ids,ii)},'conditions':{},'candidate_downstream':{}}
for name,sk in [('isolated_DN_manual',None),('isolated_DN_SK_removed',0.0)]:
 cells=m.cells[ii].copy()
 if sk is not None:cells[:,8]=sk
 n=len(ii);emptyi=np.empty(0,np.int32);emptyf=np.empty(0,float)
 result=_kernel(n,emptyi,emptyi,emptyf,np.zeros(n),np.zeros(n),np.zeros(n,dtype=np.bool_),s['dt_ms'],round(events['duration_ms']/s['dt_ms']),0,round(s['delay_ms']/s['dt_ms']),m.global_values,cells,round(s['record_interval_ms']/s['dt_ms']),wave,s['input_sample_ms'],np.arange(n,dtype=np.int64),np.zeros(n+1,dtype=np.int64),m.kinetics,m.aux)
 assert not result[5]
 out['conditions'][name]={id:summarize(result[0],i) for i,id in enumerate(ids)}
for id in ['800003','800009','800114','800061','800072','800211']:
 i=m.lookup[id];out['candidate_downstream'][id]={'type':m.neurons[i]['type'],**summarize(full,i)}
out['video_sampling']={'physical_duration_ms':400,'physical_record_ms':5,'neural_clock_scale':3,'neural_step_ms':s['dt_ms'],'neural_current_record_ms':s['record_interval_ms'],'video_frames':80,'video_fps':m.config['render']['fps'],'neural_ms_between_body_samples':15,'display_only_rate_filter_tau_ms':m.config['render']['rate_filter_tau_ms'],'node_colour':'instantaneously sampled excitatory+inhibitory+external current; not voltage or spike','edge_colour':'fixed model excitatory/inhibitory sign; activity controls visibility','muscle_colour':'activation/red or decreasing activation/green, not inhibitory NMJ'}
out['limitations']=['Acute SK removal diagnostic does not refit or replace manual parameters','No full-network DN-clamp or VNC cell ablation performed here','These are model dynamics, not physiological validation of DNg100 autonomous bursting']
(R/'DN-rhythm-diagnosis.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
for group in ['full_network']:
 print(group,{id:d['burst_onsets_ms'] for id,d in out[group].items()})
for name,case in out['conditions'].items():print(name,{id:{'onsets':d['burst_onsets_ms'],'spikes':len(d['spike_times_ms'])} for id,d in case.items()})
