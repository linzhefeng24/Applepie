"""Manually chosen pathway candidates, full traces and unchanged controls.
No optimizer, arbitrary tonic drive, forced firing or output mask.
"""
from pathlib import Path
import json,hashlib,sys,time,platform,argparse
from importlib.metadata import version
import numpy as np
from scipy import sparse
R=Path(__file__).parent;N=R.parent/'conductance-rebuild-20261114';sys.path.insert(0,str(N));from network import simulate_network
a=argparse.ArgumentParser();a.add_argument('case');a.add_argument('bankfile');a.add_argument('tag');a.add_argument('--duration-ms',type=float,default=1600.);a.add_argument('--ablate-type',action='append',default=[]);args=a.parse_args();case,bankfile,tag=args.case,args.bankfile,args.tag;
if not np.isfinite(args.duration_ms) or args.duration_ms<1600:raise ValueError('Duration must cover unchanged original stimulus protocol')
bankfile=R/bankfile;bank=json.load(open(bankfile));p=bank['parameters'];B=N/'results/mcns-brake-extension';m=json.load(open(B/'neurons.json'));old=N/f'results/frozen-neural-panel-brake-extension-r9/{case}-config.json';old=old if old.exists() else N/f'results/frozen-neural-panel-unified-r9/{case}-config.json';cfg=json.load(open(old));p={**p,'duration_ms':args.duration_ms,'onset_ms':200.,'dt_ms':.0125};lookup={x['bodyId']:i for i,x in enumerate(m)};wave=np.zeros((int(args.duration_ms)+1,len(m)))
for e in cfg['protocol']:
 ids=[lookup[b] for b in cfg['selected_body_ids'][e['population']]];wave[e['on_ms']:e['off_ms'],ids]=e['current_pA']
roles=['MN' if x['class']=='vnc_motor' else 'other' for x in m];types=['AN19A018','IN27X001','MDN','DNp50','IN07B001','IN18B011','IN21A017','IN17A001','DNa02','DNa03','LAL010','DNg100','DNg97'];rec={i for i,x in enumerate(m) if x['type'] in types};seen=set()
for i,x in enumerate(m):
 key=(x['type'],x.get('somaNeuromere'),x.get('somaSide'))
 if x['type'] in ['Ti extensor MN','Ti flexor MN','Acc. ti flexor MN'] and key not in seen:rec.add(i);seen.add(key)
rec=sorted(rec);ablate=[i for i,x in enumerate(m) if x['type'] in args.ablate_type];
if set(args.ablate_type)-{x['type'] for x in m}:raise ValueError('Ablation type not in this graph')
O=R/'results'/tag;O.mkdir(parents=True,exist_ok=True);sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();config={'case':case,'status':'started','parameters':p,'parameter_sha256':hashlib.sha256(json.dumps(p,sort_keys=True).encode()).hexdigest(),'source_bank_sha256':sha(bankfile),'input_hashes':{str(f):sha(f) for f in [B/'neurons.json',B/'signed-hypothesis-connectivity.npz',old]},'code_hashes':{str(f):sha(f) for f in [Path(__file__),N/'model.py',N/'network.py',N/'grouped_parameters.py']},'protocol':cfg['protocol'],'ablate_body_ids':[m[i]['bodyId'] for i in ablate],'record_body_ids':[m[i]['bodyId'] for i in rec],'roles':'annotated vnc_motor=MN, existing shared adult-profile prior retained','versions':{n:version(n) for n in ['numpy','scipy','numba']},'python':platform.python_version(),'command':[sys.executable,*sys.argv],'randomness':'deterministic, no random draws'};(O/(case+'-config.json')).write_text(json.dumps(config,indent=2)+'\n');start=time.perf_counter();r=simulate_network(sparse.load_npz(B/'signed-hypothesis-connectivity.npz').toarray(),roles,m,p,drive_waveform=wave,ablate=ablate,record_indices=rec);n=r['valid_record_count'];temp=O/(case+'.npz.tmp')
with temp.open('wb') as f:np.savez_compressed(f,spikes=r['spike_counts_1ms'],body_ids=[x['bodyId'] for x in m],record_body_ids=[m[i]['bodyId'] for i in rec],voltage=r['voltage_first12'][:n],calcium=r['calcium_first12_uM'][:n],currents_pA=r['synaptic_currents_pA'][:n],conductances_nS=r['synaptic_conductances_nS'][:n],time_ms=r['record_time_ms'],cell_parameters=r['cell_parameters'])
temp.replace(O/(case+'.npz'));rows=[]
for j,i in enumerate(rec):
 item={'body_id':m[i]['bodyId'],'type':m[i]['type'],'segment':m[i].get('somaNeuromere'),'side':m[i].get('somaSide'),'windows':{}}
 for a,b in [(0,200),(200,450),(500,950),(1000,1450)]:
  sel=(r['record_time_ms']>=a)&(r['record_time_ms']<b);item['windows'][str(a)+'_'+str(b)]={'rate_Hz':float(r['spike_counts_1ms'][a:b,i].sum()/((b-a)/1000)),'soma_mV':float(r['voltage_first12'][:n,j,0][sel].mean()),'gE_nS':float(r['synaptic_conductances_nS'][:n,j,0][sel].mean()),'gI_nS':float(r['synaptic_conductances_nS'][:n,j,1][sel].mean()),'Ca_uM':float(r['calcium_first12_uM'][:n,j][sel].mean())}
 rows.append(item)
control_equal=None
if case=='control':control_equal=bool(np.array_equal(r['spike_counts_1ms'][:1600],np.load(N/'results/frozen-neural-panel-brake-extension-r9/control.npz')['spikes']))
report={'status':'complete','case':case,'numerical_failure':r['numerical_failure'],'elapsed_s':time.perf_counter()-start,'control_full_spike_array_identical_to_previous':control_equal,'pair_interventions':r.get('type_pair_interventions',[]),'cells':rows};(O/(case+'-diagnosis.json')).write_text(json.dumps(report,indent=2)+'\n');print(case,tag,[(x['type'],x['body_id'],{k:round(v['rate_Hz'],1) for k,v in x['windows'].items()}) for x in rows if x['type'] in ['IN07B001','IN18B011','IN21A017']],flush=True)
