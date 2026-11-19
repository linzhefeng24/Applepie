"""Same selected model, observational exact-step logger, explicit interventions.
All physiological parameters come from the selected model and cases.json.
"""
from pathlib import Path
import argparse,hashlib,json,os,sys,time
import numpy as np
R=Path(__file__).resolve().parent;ROOT=R.parents[1];P=Path(os.environ.get('MANUAL_R2_PACKAGE',str(ROOT/'research/manual-full-rerun-20261119/cache/extracted/Manual_FreeBody')));sys.path.insert(0,str(P/'02_code'))
from flymodel import Model
import flymodel.simulator as simulator
from instrumented_dynamics import _kernel
PLAN=json.loads((R/'cases.json').read_text())
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def match(neurons,q):return np.array([all(n.get(k)==v for k,v in q.items()) for n in neurons])
def run(name):
 spec=PLAN['cases'][name];m=Model(Path(os.environ.get('CORE_MODEL_PATH',str(ROOT/'research/manual-extension-review-20261119/cache/selected_manual_model.yaml'))));assert m.sha256==PLAN['model_sha256'];changes=[]
 if 'duration_ms' in spec:
  m.config['experiments']['DN_drive']['duration_ms']=spec['duration_ms']
  for event in m.config['experiments']['DN_drive']['events']:event['off_ms']=spec['drive_off_ms']
 for q in spec.get('terminal_gain',[]):
  src=match(m.neurons,{k[7:]:v for k,v in q.items() if k.startswith('source_')});dst=match(m.neurons,{k[7:]:v for k,v in q.items() if k.startswith('target_')});mask=src[m.pre]&dst[m.post];assert mask.any();m.weight[mask]*=q['factor'];changes.append({**q,'edges':int(mask.sum())})
 for q in spec.get('cell_set',[]):
  mask=match(m.neurons,{k:v for k,v in q.items() if k not in ['parameter','value']});assert mask.any();j=m.config['neural']['cell_parameter_columns'].index(q['parameter']);m.cells[mask,j]=q['value'];changes.append({**q,'cells':int(mask.sum())})
 ablate=m.neuron_ids(type=spec['ablate_type']) if 'ablate_type' in spec else [];saved={}
 for typ in spec.get('ablate_types',[]):ablate+=m.neuron_ids(type=typ)
 if 'retain_superclasses' in spec:
  ablate=list(set(ablate)|{n['bodyId'] for n in m.neurons if n.get('superclass') not in spec['retain_superclasses'] and n['bodyId'] not in spec.get('retain_ids',[])})
 def logger(*args):
  output=_kernel(*args);assert not output[14],'Exact spike log overflow';saved['events']=output[13];return output[:13]
 simulator._kernel=logger
 record=['10045','10056','800173','800288','800863','903216','801884','803183','800061','801173','802072']
 record+=spec.get('record_additional_ids',[])
 start=time.monotonic();r=m.run_neural(record_ids=record,record_interval_ms=0.1,ablate_ids=ablate);u=m.muscle_excitation(r);elapsed=time.monotonic()-start
 out=R/'results';out.mkdir(exist_ok=True);raw=out/(name+'.npz');np.savez_compressed(raw,spikes=r['spikes'],events_step_cell=saved['events'],voltage=r['voltage'],time_ms=r['time_ms'],currents_pA=r['currents_pA'],conductances_nS=r['conductances_nS'],record_indices=r['record_indices'],body_ids=np.array(m.ids),u=u)
 if name in {'baseline','E2_silenced'}:
  ref='I1_exc_x2' if name=='baseline' else 'I1_exc_x2_E2_silenced';z=np.load(Path(os.environ.get('CORE_REFERENCE_RESULTS',str(ROOT/'research/manual-extension-review-20261119/results')))/f'{ref}.npz');assert np.array_equal(r['spikes'],z['spikes']) and np.array_equal(u,z['u']), 'Observational logger changed dynamics';validation={'previous_condition':ref,'spikes_array_equal':True,'u_array_equal':True}
 else:validation=None
 ev=saved['events'];dt=m.config['neural']['solver']['dt_ms'];summ={}
 for bid in record:
  i=m.lookup[bid];t=(ev[ev[:,1]==i,0]+1)*dt;t=t[(t>=m.config['experiments']['DN_drive']['events'][0]['on_ms'])&(t<m.config['experiments']['DN_drive']['events'][0]['off_ms'])];summ[bid]={'type':m.neurons[i]['type'],'spike_times_ms':t.tolist(),'count':len(t),'first_ms':float(t[0]) if len(t) else None}
 report={'case':name,'spec':spec,'applied_changes':changes,'model_sha256':m.sha256,'cell_array_sha256':hashlib.sha256(m.cells.tobytes()).hexdigest(),'effective_weights_sha256':hashlib.sha256(m.weight.tobytes()).hexdigest(),'logger_source_sha256':digest(R/'instrumented_dynamics.py'),'runner_sha256':digest(__file__),'cases_sha256':digest(R/'cases.json'),'seconds':elapsed,'spikes_total':int(r['spikes'].sum()),'neurons':summ,'anatomical_counts_changed':False,'actual_protocol':m.config['experiments']['DN_drive'],'validation':validation,'raw':{'name':raw.name,'bytes':raw.stat().st_size,'sha256':digest(raw)},'scope':'model-only causal/parameter experiment; no physical body or laboratory behavior validation'}
 (out/(name+'.json')).write_text(json.dumps(report,indent=2)+'\n');print(name,report['spikes_total'],{b:(summ[b]['count'],summ[b]['first_ms']) for b in ['801884','803183','800061','802072']},round(elapsed,1),flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('cases',nargs='+',choices=PLAN['cases']);a=p.parse_args()
 for case in a.cases:run(case)
