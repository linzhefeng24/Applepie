"""Causal localization of manual-model DN bursting, not a parameter optimizer.
Every case starts from the packaged initial neural state and same tonic input.
Route cuts change only specified directed edges; silencing clamps listed cells
using the unmodified kernel ablation interface. Original model is never written.
"""
from pathlib import Path
import argparse,hashlib,json,time,sys
import numpy as np
R=Path(__file__).resolve().parent;ROOT=R.parents[1]
P=ROOT/'research/manual-full-rerun-20261119/cache/extracted/Manual_FreeBody'
sys.path.insert(0,str(P/'02_code'))
from flymodel import Model
from flymodel.dynamics import _kernel
GROUPS={'DNge129':['11006','10856'],'GNG127':['11982','516820'],'GNG458':['26344']}
CASES={
 'cut_DNge129_DN':{'cut_to_DN':GROUPS['DNge129']},
 'cut_GNG127_DN':{'cut_to_DN':GROUPS['GNG127']},
 'cut_GNG458_DN':{'cut_to_DN':GROUPS['GNG458']},
 'cut_top5_DN':{'cut_to_DN':sum(GROUPS.values(),[])},
 'silence_DNge129':{'silence':GROUPS['DNge129']},
 'silence_GNG127':{'silence':GROUPS['GNG127']},
 'silence_GNG458':{'silence':GROUPS['GNG458']},
 'cut_all_inhibitory_DN':{'cut_all_inhibitory_DN':True},
}
# Single-cell cuts and constrained reconstitutions are available for adaptive follow-up.
for id in sum(GROUPS.values(),[]):CASES['cut_'+id+'_DN']={'cut_to_DN':[id]}
for name,ids in GROUPS.items():CASES['retain_'+name+'_inhibitory_DN']={'retain_inhibitory_DN':ids}
CASES['retain_top5_inhibitory_DN']={'retain_inhibitory_DN':sum(GROUPS.values(),[])}
for name,ids in GROUPS.items():CASES['retain_'+name+'_all_input_DN']={'retain_all_input_DN':ids}
CASES['retain_top5_all_input_DN']={'retain_all_input_DN':sum(GROUPS.values(),[])}
def summary(spikes,index,dt):
 ts=np.repeat(np.arange(len(spikes))*dt,spikes[:,index].astype(int));ts=ts[(ts>=200)&(ts<1400)];starts=ts[np.r_[True,np.diff(ts)>60]] if len(ts) else ts;interval=np.diff(starts)
 return {'spike_count':len(ts),'spike_times_ms':ts.tolist(),'burst_gap_definition_ms':60,'burst_onsets_ms':starts.tolist(),'burst_intervals_ms':interval.tolist(),'median_interval_ms':float(np.median(interval)) if len(interval) else None,'max_ISI_ms':float(np.diff(ts).max()) if len(ts)>1 else None}
def run(name):
 spec=CASES[name];m=Model(P/'01_model/model.yaml');assert m.sha256=='858d1818b8d8394c95bb62a6ce60474cb534a83b94265ef8615e367c110d262c';s=m.config['neural']['solver'];proto=m.config['experiments']['DN_drive'];n=len(m.ids);dn=np.array([m.lookup[x] for x in ['10045','10056']]);keep=np.ones(len(m.pre),bool);target=np.isin(m.post,dn)
 if 'cut_to_DN' in spec:keep&=~(np.isin(m.pre,[m.lookup[x] for x in spec['cut_to_DN']])&target)
 if spec.get('cut_all_inhibitory_DN'):keep&=~(target&(m.weight<0))
 if 'retain_inhibitory_DN' in spec:keep&=~(target&(m.weight<0)&~np.isin(m.pre,[m.lookup[x] for x in spec['retain_inhibitory_DN']]))
 if 'retain_all_input_DN' in spec:keep&=~(target&~np.isin(m.pre,[m.lookup[x] for x in spec['retain_all_input_DN']]))
 pre=m.pre[keep];post=m.post[keep];w=m.weight[keep];offset=np.r_[0,np.cumsum(np.bincount(pre,minlength=n))];abl=np.array([id in spec.get('silence',[]) for id in m.ids]);wave=np.zeros((round(proto['duration_ms']/s['input_sample_ms'])+1,n))
 for e in proto['events']:
  for id in e['neuron_ids']:wave[round(e['on_ms']/s['input_sample_ms']):round(e['off_ms']/s['input_sample_ms']),m.lookup[id]]=e['current_pA']
 ids=['10045','10056','11006','10856','11982','516820','26344','800003','800009','800114','800061','800072','800211'];rec=np.array([m.lookup[x] for x in ids]);start=time.monotonic()
 out=_kernel(n,pre,post,w,np.zeros(n),np.zeros(n),abl,s['dt_ms'],round(proto['duration_ms']/s['dt_ms']),0,round(s['delay_ms']/s['dt_ms']),m.global_values,m.cells,round(s['record_interval_ms']/s['dt_ms']),wave,s['input_sample_ms'],rec,offset,m.kinetics,m.aux)
 if out[5]:raise RuntimeError('Voltage guard tripped; not a valid ablation result')
 cache=R/'cache';cache.mkdir(exist_ok=True);raw=cache/(name+'.npz');np.savez_compressed(raw,spikes=out[0],voltage=out[1],currents_pA=out[7],record_indices=rec)
 report={'case':name,'intervention':spec,'model_sha256':m.sha256,'source_code_sha256':hashlib.sha256((P/'02_code/flymodel/dynamics.py').read_bytes()).hexdigest(),'original_directed_edges':len(m.pre),'removed_edges':int((~keep).sum()),'silenced_cells':spec.get('silence',[]),'physical_or_neural_parameters_optimized':False,'duration_ms':proto['duration_ms'],'input':proto['events'],'seconds':time.monotonic()-start,'neurons':{id:{'type':m.neurons[i]['type'],**summary(out[0],i,s['spike_bin_ms'])} for id,i in zip(ids,rec)},'output_npz':{'name':raw.name,'sha256':hashlib.sha256(raw.read_bytes()).hexdigest(),'bytes':raw.stat().st_size}}
 (R/(name+'.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(name,json.dumps({id:{'count':v['spike_count'],'onsets':v['burst_onsets_ms']} for id,v in report['neurons'].items() if id in ['10045','10056','800061']},ensure_ascii=False),flush=True);return report
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('case',choices=CASES);a=p.parse_args();run(a.case)
