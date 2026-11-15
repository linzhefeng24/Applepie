"""Rerun the exact saved BRK protocol with additional voltage/current probes.
Recorded variables must not change network activity: full spike arrays are
checked byte-for-byte against the preceding simulation before interpretation.
"""
from pathlib import Path
import json,sys,hashlib,time
import numpy as np
from scipy import sparse
R=Path(__file__).parent;N=R.parent/'conductance-rebuild-20261114';sys.path.insert(0,str(N));from network import simulate_network
B=N/'results/mcns-brake-extension';O=R/'diagnostics';case='BRK';cfg=json.load(open(N/f'results/frozen-neural-panel-brake-extension-r9/{case}-config.json'));p=cfg['parameters'];m=json.load(open(B/'neurons.json'));W=sparse.load_npz(B/'signed-hypothesis-connectivity.npz');types=['IN07B001','IN18B011','IN19A001','IN03B019','IN03B032','IN21A017'];rec=[i for i,x in enumerate(m) if x['type'] in types];roles=['MN' if x['class']=='vnc_motor' else 'other' for x in m];wave=np.zeros((int(p['duration_ms'])+1,len(m)));lookup={x['bodyId']:i for i,x in enumerate(m)}
for event in cfg['protocol']:
 ids=[lookup[b] for b in cfg['selected_body_ids'][event['population']]];wave[event['on_ms']:event['off_ms'],ids]=event['current_pA']
start=time.perf_counter();r=simulate_network(W.toarray(),roles,m,p,drive_waveform=wave,record_indices=rec);original=N/f'results/frozen-neural-panel-brake-extension-r9/{case}.npz';old=np.load(original);assert np.array_equal(r['spike_counts_1ms'],old['spikes']),'probe changed dynamics';n=r['valid_record_count'];np.savez_compressed(O/'BRK-premotor-probes.npz',body_ids=[m[i]['bodyId'] for i in rec],types=[m[i]['type'] for i in rec],voltage=r['voltage_first12'][:n],currents_pA=r['synaptic_currents_pA'][:n],conductances_nS=r['synaptic_conductances_nS'][:n],time_ms=r['record_time_ms'],spikes=r['spike_counts_1ms'][:,rec]);rows=[]
for j,i in enumerate(rec):
 s=(r['record_time_ms']>=500)&(r['record_time_ms']<950);v=r['voltage_first12'][:n,j][s];cur=r['synaptic_currents_pA'][:n,j][s];g=r['synaptic_conductances_nS'][:n,j][s];rows.append({'body_id':m[i]['bodyId'],'type':m[i]['type'],'NT':m[i]['predictedNt'],'segment':m[i].get('somaNeuromere'),'side':m[i]['somaSide'],'spikes_500_950ms':int(r['spike_counts_1ms'][500:950,i].sum()),'mean_soma_mV':float(v[:,0].mean()),'max_soma_mV':float(v[:,0].max()),'mean_axon_mV':float(v[:,1].mean()),'max_axon_mV':float(v[:,1].max()),'mean_gE_nS':float(g[:,0].mean()),'mean_gI_nS':float(g[:,1].mean()),'mean_exc_pA':float(cur[:,0].mean()),'mean_inh_pA':float(cur[:,1].mean())})
report={'status':'independent exact-activity rerun with added probes','full_spike_array_identical_to_previous':True,'numerical_failure':r['numerical_failure'],'elapsed_s':time.perf_counter()-start,'source_config':cfg,'source_raw_sha256':hashlib.sha256(original.read_bytes()).hexdigest(),'code_sha256':{str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in [Path(__file__),N/'model.py',N/'network.py']},'observations':rows};(O/'BRK-premotor-probes.json').write_text(json.dumps(report,indent=2)+'\n');print(rows,flush=True)
