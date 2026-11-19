"""Targeted full HH network experiments; every run starts from initial state.
No body motion or experimental phenomenon is declared reproduced by firing alone.
"""
from pathlib import Path
import argparse,hashlib,json,sys,time,os
import numpy as np
R=Path(__file__).resolve().parent
P=Path(os.environ.get('MANUAL_R2_PACKAGE',str(R.parents[1]/'research/manual-full-rerun-20261119/cache/extracted/Manual_FreeBody'))))
sys.path.insert(0,str(P/'02_code'))
from flymodel import Model
CASES=['quiet','DN_drive','core_silenced','new_glutamate_zero','core_release_x2','EPG_left','DN_plus_9A','DN_plus_Delta7']
def run(case):
 m=Model(R/'cache/extended_model.yaml');oldn=3988;new=np.arange(len(m.ids))>=oldn;core=np.array([(n.get('type') in {'IN17A001','INXXX466','IN16B036'}) for n in m.neurons]);events=list(m.config['experiments']['DN_drive']['events']);silenced=[];changes=[]
 if case=='quiet':events=[]
 if case=='core_silenced':silenced=[m.ids[i] for i in np.flatnonzero(core)];changes.append({'ablate_ids':silenced})
 if case=='new_glutamate_zero':
  mask=new&np.array([n.get('predictedNt')=='glutamate' for n in m.neurons]);m.weight[mask[m.pre]]=0;changes.append({'new_glutamate_outgoing_sign':0,'note':'uncertainty sensitivity, not presumed correct receptor'})
 if case=='core_release_x2':
  # Manual trial suggested by absent/subthreshold newly added core output, to be assessed against baseline.
  m.cells[core,12]*=2;changes.append({'cell_types':['IN17A001','INXXX466','IN16B036'],'parameter':'source_release_gain','multiplier':2,'origin':'manual_trial_not_measured'})
 if case in ['EPG_left','DN_plus_9A','DN_plus_Delta7']:
  if case=='EPG_left':ix=[i for i,n in enumerate(m.neurons) if n.get('type')=='EPG' and n.get('somaSide')=='L'];events=[]
  elif case=='DN_plus_9A':ix=[i for i,n in enumerate(m.neurons) if (n.get('type') or '').startswith('IN09A') and n.get('predictedNt')=='gaba']
  else:ix=[i for i,n in enumerate(m.neurons) if n.get('type')=='Delta7']
  assert ix,case
  events=events+[dict(neuron_ids=[m.ids[i] for i in ix],current_pA=160,on_ms=600,off_ms=1100)]
 recids=list(dict.fromkeys(['10045','10056','11006','10856','11982','516820','26344','800173','800288','800863','903216','801884','803183']+[m.ids[i] for i in np.flatnonzero(new)[:10]]))
 start=time.monotonic();r=m.run_neural(events=events,record_ids=recids,record_interval_ms=1,ablate_ids=silenced);elapsed=time.monotonic()-start;sp=r['spikes'];u=m.muscle_excitation(r)
 out=R/'results';out.mkdir(exist_ok=True);raw=out/(case+'.npz');np.savez_compressed(raw,spikes=sp,voltage=r['voltage'],time_ms=r['time_ms'],conductances_nS=r['conductances_nS'],currents_pA=r['currents_pA'],record_indices=r['record_indices'],body_ids=np.array(m.ids),u=u)
 groups={}
 for typ in sorted({n.get('type') for n in m.neurons if n.get('type') in {'DNg100','IN17A001','INXXX466','IN16B036','EPG','EPGt','Delta7','DNb05','DNb06','DNg11','DNg13'} or (n.get('type') or '').startswith('DNg12_')}):
  ix=[i for i,n in enumerate(m.neurons) if n.get('type')==typ];groups[typ]={'ids':[m.ids[i] for i in ix],'spike_counts_200_600ms':sp[200:600,ix].sum(axis=0).tolist(),'spike_counts_600_1100ms':sp[600:1100,ix].sum(axis=0).tolist(),'spike_counts_1100_1500ms':sp[1100:1500,ix].sum(axis=0).tolist()}
 # Exact directed motif edges are read from effective graph; zeros from sensitivity are retained explicitly.
 ids=['10045','10056','800173','800288','800863','903216','801884','803183'];idx=np.array([m.lookup[b] for b in ids]);sel=np.isin(m.pre,idx)&np.isin(m.post,idx)
 edges=[{'pre':m.ids[a],'post':m.ids[b],'effective_signed_count':float(w)} for a,b,w in zip(m.pre[sel],m.post[sel],m.weight[sel])]
 mn=np.array([n.get('superclass')=='motor_neuron' for n in m.neurons]);report={'case':case,'events':events,'changes':changes,'model_sha256':m.sha256,'cell_parameters_sha256':hashlib.sha256(m.cells.tobytes()).hexdigest(),'effective_weights_sha256':hashlib.sha256(m.weight.tobytes()).hexdigest(),'elapsed_seconds':elapsed,'spikes_total':int(sp.sum()),'MN_count':int(mn.sum()),'active_MN':int((sp[200:1500,mn].sum(axis=0)>0).sum()),'MN_spikes_before_during_after':[int(sp[a:b,mn].sum()) for a,b in [(200,600),(600,1100),(1100,1500)]],'groups':groups,'core_direct_edges':edges,'raw_output':{'name':raw.name,'sha256':hashlib.sha256(raw.read_bytes()).hexdigest(),'bytes':raw.stat().st_size},'scope':'model mechanistic test; no experimental behavior validation; no sensory/body closed loop'}
 (out/(case+'.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(case,report['spikes_total'],report['active_MN'],round(elapsed,1),flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('cases',nargs='+',choices=CASES);a=p.parse_args()
 for case in a.cases:run(case)
