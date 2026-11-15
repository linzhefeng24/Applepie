"""Frozen shared parameters, actual pulse and recovery traces, no optimizer.
This experiment varies only which published populations receive input and when.
"""
from pathlib import Path
import json,sys,hashlib,platform,time
import numpy as np
from scipy import sparse
from grouped_parameters import group_key
from network import simulate_network
R=Path(__file__).parent;O=R/'results'/('frozen-neural-panel-'+(sys.argv[3] if len(sys.argv)>3 else 'r4'));O.mkdir(exist_ok=True);mode=sys.argv[1] if len(sys.argv)>1 else 'control';B=R/(sys.argv[4] if len(sys.argv)>4 else ('results/mcns-steering' if mode.startswith('PFL') else 'results/mcns-command-v2'));meta=[{**x,'connectome_namespace':'MaleCNS_v1.0'} for x in json.load(open(B/'neurons.json'))];W=sparse.load_npz(B/'signed-hypothesis-connectivity.npz');bank=json.load(open(R/(sys.argv[2] if len(sys.argv)>2 else 'configs/manual-neural-bank-r4.json')));p=json.loads(json.dumps(bank['parameters']));available={group_key(x) for x in meta};unused=sorted(set(p['group_parameters'])-available);p['group_parameters']={k:v for k,v in p['group_parameters'].items() if k in available};p.update(duration_ms=1600.,onset_ms=200.,dt_ms=.0125);groups={}
for i,x in enumerate(meta):
 if x['type']=='PFL2':groups.setdefault('PFL2',[]).append(i)
 if x['type']=='PFL3' and x.get('functional_output_side') in ['L','R']:groups.setdefault('PFL3'+x['functional_output_side'],[]).append(i)
 if x['type']=='DNp09':groups.setdefault('P9',[]).append(i)
 if x['type']=='DNg60':groups.setdefault('BB',[]).append(i)
 if x.get('flywireType')=='CB0890':groups.setdefault('FG',[]).append(i)
 if x.get('flywireType')=='CB0038':groups.setdefault('Fdg',[]).append(i)
 if (x.get('type') or '').startswith('CL210_'):groups.setdefault('BPN',[]).append(i)
 if x['type']=='AN19A018' and x.get('mancBodyid') in [10788.,10564.,10528.,10449.,10282.,10351.]:groups.setdefault('BRK',[]).append(i)
 if x['type']=='MDN' or x['type']=='DNp50' or x.get('mancType')=='MDN':groups.setdefault('MDN',[]).append(i)
 if x.get('mancBodyid') in [10441.,10348.]:groups.setdefault('BON1',[]).append(i)
long=mode=='BRK2s';p['duration_ms']=7001. if long else 1600.;wave=np.zeros((int(p['duration_ms'])+1,len(meta)));protocol=[]
if long:
 wave[2000:4000,groups['BRK']]=160.;protocol.append({'population':'BRK','on_ms':2000,'off_ms':4000,'current_pA':160.})
elif mode!='control':
 labels=mode.split('+')
 for k,label in enumerate(labels):
  if label not in groups:raise KeyError(label)
  start,end=(200,1500) if k==0 else (450,950)
  if label=='Fdg':end=1200
  wave[start:end,groups[label]]=160.;protocol.append({'population':label,'on_ms':start,'off_ms':end,'current_pA':160.})
rec=sorted(set(i for ids in groups.values() for i in ids)|{i for i,x in enumerate(meta) if x['type'] in ['DNg100','DNg97','DNg75','DNg55','DNge053','DNa02','DNa03','LAL010','DNg13','LBL40','INXXX468'] or x.get('mancType')=='INXXX468'});config={'bank_sha256':bank['parameter_sha256'],'parameters':p,'protocol':protocol,'selected_body_ids':{g:[meta[i]['bodyId'] for i in ii] for g,ii in groups.items()},'unused_bank_groups':unused,'dataset':'MaleCNS_v1.0','graph_directory':str(B.relative_to(R)),'randomness':'deterministic; no stochastic draws','numpy_version':np.__version__,'source_input_files':{n:hashlib.sha256((B/n).read_bytes()).hexdigest() for n in ['neurons.json','signed-hypothesis-connectivity.npz']},'code_hashes_at_start':{n:hashlib.sha256((R/n).read_bytes()).hexdigest() for n in ['model.py','network.py','grouped_parameters.py','pulse_neural_panel.py']},'python':platform.python_version(),'interpretation':'physiological changes fixed across conditions; observations and traces, no scalar optimization score'};(O/(mode+'-config.json')).write_text(json.dumps(config,indent=2));start=time.perf_counter();r=simulate_network(W.toarray(),['other']*len(meta),meta,p,drive_waveform=wave,record_indices=rec);n=r['valid_record_count'];tmp=O/(mode+'.npz.tmp')
with tmp.open('wb') as f:np.savez_compressed(f,spikes=r['spike_counts_1ms'],body_ids=[x['bodyId'] for x in meta],record_body_ids=[meta[i]['bodyId'] for i in rec],cell_parameters=r['cell_parameters'],voltage=r['voltage_first12'][:n],calcium=r['calcium_first12_uM'][:n],currents_pA=r['synaptic_currents_pA'][:n],conductances_nS=r['synaptic_conductances_nS'][:n],time_ms=r['record_time_ms'])
tmp.replace(O/(mode+'.npz'));windows={'baseline':(0,200),'command':(250,450),'halt_on':(500,950),'recovery':(1050,1500)} if not long else {'baseline':(0,2000),'BRK_on':(2000,4000),'after':(4000,7000)};cells=[]
for j,i in enumerate(rec):
 row={'body_id':meta[i]['bodyId'],'type':meta[i]['type'],'side':meta[i]['somaSide'],'segment':meta[i].get('somaNeuromere'),'groups':[g for g,ii in groups.items() if i in ii],'windows':{}}
 for label,(a,b) in windows.items():
  sel=(r['record_time_ms']>=a)&(r['record_time_ms']<b);row['windows'][label]={'rate_hz':float(r['spike_counts_1ms'][a:b,i].sum()/((b-a)/1000)),'soma_mV':float(r['voltage_first12'][:n,j,0][sel].mean()),'model_Ca_uM':float(r['calcium_first12_uM'][:n,j][sel].mean()),'exc_pA':float(r['synaptic_currents_pA'][:n,j,0][sel].mean()),'inh_pA':float(r['synaptic_currents_pA'][:n,j,1][sel].mean())}
 cells.append(row)
report={'condition':mode,'bank_sha256':bank['parameter_sha256'],'numerical_failure':r['numerical_failure'],'elapsed_s':time.perf_counter()-start,'cells':cells,'status':'complete simulation; inspect full traces before judging phenomena, no endpoint pass/fail threshold'};(O/(mode+'-diagnosis.json')).write_text(json.dumps(report,indent=2));print(mode,[(x['type'],x['side'],{k:round(v['rate_hz'],1) for k,v in x['windows'].items()}) for x in cells if x['type'] in ['DNg100','DNg97','LBL40']],flush=True)
