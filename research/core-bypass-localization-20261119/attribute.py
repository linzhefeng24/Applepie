"""Reconstruct source-resolved conductances at actual recorded integration steps.
Uses exact event steps, original dual-exponential normalization and model gains.
This gives input attribution; matched edge cuts remain necessary for causality.
"""
from pathlib import Path
import json,sys,os,numpy as np
R=Path(__file__).resolve().parent;ROOT=R.parents[1];P=Path(os.environ.get('MANUAL_R2_PACKAGE',str(ROOT/'research/manual-full-rerun-20261119/cache/extracted/Manual_FreeBody')));sys.path.insert(0,str(P/'02_code'));from flymodel import Model
PLAN=json.loads((R/'cases.json').read_text())
def model(case):
 m=Model(ROOT/'research/manual-extension-review-20261119/cache/selected_manual_model.yaml')
 for q in PLAN['cases'][case].get('terminal_gain',[]):
  src=np.array([all(n.get(k[7:])==v for k,v in q.items() if k.startswith('source_')) for n in m.neurons]);dst=np.array([all(n.get(k[7:])==v for k,v in q.items() if k.startswith('target_')) for n in m.neurons]);m.weight[src[m.pre]&dst[m.post]]*=q['factor']
 for q in PLAN['cases'][case].get('cell_set',[]):
  sel=np.array([all(n.get(k)==v for k,v in q.items() if k not in ['parameter','value']) for n in m.neurons]);m.cells[sel,m.config['neural']['cell_parameter_columns'].index(q['parameter'])]=q['value']
 return m

def compute(case):
 z=np.load(R/'results'/f'{case}.npz');m=model(case);ev=z['events_step_cell'];dt=m.config['neural']['solver']['dt_ms'];delay=round(m.config['neural']['solver']['delay_ms']/dt);times=(ev[:,0]+1)*dt;by=[[] for _ in m.ids]
 for step,i in ev:by[i].append(step)
 by=[np.asarray(q,dtype=np.int32) for q in by];out=[]
 for bid in ['800061','801173','802072','801884','803183']:
  j=m.lookup[bid];spec=PLAN['cases'][case];n=m.neurons[j];clamped=(n.get('type')==spec.get('ablate_type') or n.get('type') in spec.get('ablate_types',[]) or ('retain_superclasses' in spec and n.get('superclass') not in spec['retain_superclasses'] and bid not in spec.get('retain_ids',[])))
  if clamped:
   out.append({'target':bid,'clamped_by_diagnostic':True,'contributors':[],'first_spike_time_ms':None});continue
  ts=times[(ev[:,1]==j)&(times>=200)&(times<1500)];wanted=ts[0] if len(ts) else (218 if bid in {'801884','803183'} else 210);ridx=list(z['record_indices']).index(j);sample=int(np.argmin(abs(z['time_ms']-wanted)));t=float(z['time_ms'][sample]);step=round(t/dt)-1;rows=[]
  for k in np.flatnonzero(m.post==j):
   i=m.pre[k];w=m.weight[k]
   if w==0:continue
   arrivals=by[i]+delay;age=(step-arrivals[arrivals<=step])*dt
   if not len(age):continue
   idx=0 if w>0 else 1;tr,td=m.global_values[2*idx:2*idx+2];tp=np.log(td/tr)/(1/tr-1/td);norm=1/(np.exp(-tp/td)-np.exp(-tp/tr));scale=abs(w)*m.global_values[4+idx]*m.cells[i,12]*(m.cells[j,5] if w>0 else m.cells[i,6]);g=float(scale*norm*np.sum(np.exp(-age/td)-np.exp(-age/tr)))
   if g>1e-12:rows.append({'pre':m.ids[i],'type':m.neurons[i]['type'],'sign':'exc' if w>0 else 'inh','effective_signed_count':float(w),'conductance_nS':g,'last_arrival_ms':float((arrivals[arrivals<=step][-1]+1)*dt)})
  sums=[sum(q['conductance_nS'] for q in rows if q['sign']==s) for s in ['exc','inh']];actual=z['conductances_nS'][sample,ridx];assert np.allclose(sums,actual,rtol=1e-9,atol=1e-9),(case,bid,sums,actual.tolist());rows.sort(key=lambda q:-q['conductance_nS'])
  out.append({'target':bid,'type':m.neurons[j]['type'],'first_spike_time_ms':float(ts[0]) if len(ts) else None,'sample_ms':t,'sample_vs_first_ms':float(t-ts[0]) if len(ts) else None,'axon_mV':float(z['voltage'][sample,ridx,1]),'soma_mV':float(z['voltage'][sample,ridx,0]),'source_decomposition_sum_nS':sums,'recorded_conductances_nS':actual.tolist(),'validated_reconstruction':True,'contributors':rows,'limitation':'Attribution at the nearest recorded 0.1ms sample, not a claim that the largest source alone is sufficient.'})
 (R/(case+'_attribution.json')).write_text(json.dumps(out,indent=2)+'\n');print(case,[(q['target'],q['first_spike_time_ms'],[(x['pre'],round(x['conductance_nS'],3)) for x in q['contributors'][:3]]) for q in out])
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('cases',nargs='+',choices=PLAN['cases']);a=p.parse_args()
 for case in a.cases:compute(case)
