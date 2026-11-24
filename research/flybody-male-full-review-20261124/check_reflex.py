"""Matched rerun of the package's #99 proxy, using its actual selectors and parameters.
Artificial held-MN current is not natural active movement; report exact named readout.
"""
from pathlib import Path
import argparse,sys,hashlib,json,time,importlib.util,numpy as np
R=Path(__file__).resolve().parent;P=R/'cache/extracted/flybody_male_full';sys.path.insert(0,str(P/'02_code'));from flymodel import Model
spec=importlib.util.spec_from_file_location('supplied_protocol',P/'07_protocols/run_protocol.py');protocol=importlib.util.module_from_spec(spec);spec.loader.exec_module(protocol)
def run(name):
 m=Model(P/'01_model/model.yaml');phen=json.load(open(P/'03_phenomena/phenomena.json'));p=json.load(open(P/'07_protocols/protocols.json'))['protocols']['chord_plus_tiflex_bg'];parts=p['background']+(p['events'] if name=='sensory_plus_background' else []);events=[]
 for e in parts:
  ii=protocol.select(m,phen,e['selector']);assert ii;events.append({k:e[k] for k in ['current_pA','on_ms','off_ms']}|{'neuron_ids':[m.ids[i] for i in ii]})
 target=protocol.select(m,phen,p['background'][0]['selector'])[0];bid=m.ids[target];m.config['experiments']['quiet']['duration_ms']=p['duration_ms'];start=time.monotonic();r=m.run_neural('quiet',events=events,record_ids=[bid],record_interval_ms=1);raw=R/'cache'/f'{name}.npz';np.savez_compressed(raw,spikes=r['spikes'],voltage=r['voltage'],calcium=r['calcium'],currents_pA=r['currents_pA'],conductances_nS=r['conductances_nS'],time_ms=r['time_ms'],record_indices=r['record_indices'])
 tf=[i for i,n in enumerate(m.neurons) if n.get('type')=='Ti flexor MN'];report={'case':name,'model_sha256':m.sha256,'events':events,'target_body_id':bid,'target_type':m.neurons[target]['type'],'target_rate_300_1100ms_Hz':float(r['spikes'][300:1100,target].sum()/.8),'target_rate_300_1200ms_Hz':float(r['spikes'][300:1200,target].sum()/.9),'TiFlex_mean_rate_300_1100ms_Hz':float(r['spikes'][300:1100,tf].mean()*1000),'spikes_total':int(r['spikes'].sum()),'seconds':time.monotonic()-start,'raw':{'name':raw.name,'sha256':hashlib.sha256(raw.read_bytes()).hexdigest(),'bytes':raw.stat().st_size},'interpretation':'Artificial current-context neuronal component test; no natural movement or reflex biomechanics equivalence.'};(R/(name+'.json')).write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='events'}),flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('cases',nargs='+',choices=['background_only','sensory_plus_background']);a=p.parse_args()
 for case in a.cases:run(case)
