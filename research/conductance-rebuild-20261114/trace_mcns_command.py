"""One named command/stop intervention with recorded real synaptic currents.
Manual inspection drives changes. No objective, automatic gain or output label.
"""
from pathlib import Path
import json,sys,numpy as np
from scipy import sparse
from network import simulate_network
R=Path(__file__).parent;O=R/'results/mcns-command';mode=sys.argv[1] if len(sys.argv)>1 else 'P9';condition=mode.removesuffix('-softI').removesuffix('-strong-drive').removesuffix('-K90').removesuffix('-K80');dose=200. if mode.endswith('-strong-drive') else 160.;m=json.load(open(O/'neurons.json'));W=sparse.load_npz(O/'signed-hypothesis-connectivity.npz').toarray();p=json.load(open(R/'results/mcns-steering/baseline-source-bias-config.json'))['parameters'];p={**p,'group_parameters':{}};p['duration_ms']=1400.;p['onset_ms']=200.;drive=np.zeros(len(m));groups={}
for i,x in enumerate(m):
 if x['type']=='DNp09':groups.setdefault('P9',[]).append(i)
 if x['type']=='DNg60':groups.setdefault('BB',[]).append(i)
 if x.get('flywireType')=='CB0890':groups.setdefault('FG',[]).append(i)
 if x.get('flywireType')=='CB0038':groups.setdefault('Fdg',[]).append(i)
 if x['type']=='AN19A018':groups.setdefault('BRK',[]).append(i)
 if x['type']=='DNp50' or x.get('mancType')=='MDN':groups.setdefault('MDN',[]).append(i)
 if x.get('mancBodyid') in [10441.,10348.]:groups.setdefault('BON1',[]).append(i)
for g,ii in groups.items():
 if g=='BON1':continue
 for i in ii:p['group_parameters'][m[i]['class']+'|type:'+m[i]['type']]={'axon_bias_pA':5.}
if '-K90' in mode or '-K80' in mode:
 for i in groups['P9']:p['group_parameters'][m[i]['class']+'|type:'+m[i]['type']]['K']=.8 if '-K80' in mode else .9
if mode.endswith('-softI'):p['gi_nS_per_synapse']=.006
# One unilateral P9 input; stop pathways/MDN/Fdg bilateral by published drivers.
for label in condition.split('+'):
 if label=='control':continue
 if label not in groups:raise KeyError('No verified command group: '+label)
 for i in groups[label]:
  if label=='P9' and m[i]['somaSide']!='L':continue
  drive[i]=dose
# Record all named populations plus important relay and VNC output cells.
rec=sorted(set(i for ii in groups.values() for i in ii)|{i for i,x in enumerate(m) if x['type'] in ['DNg100','DNg97','DNg75','DNg55','DNge053','DNa02','DNg13','LBL40']});(O/(mode+'-config.json')).write_text(json.dumps({'parameters':p,'stimulated_body_ids':[m[i]['bodyId'] for i in np.flatnonzero(drive)],'record_body_ids':[m[i]['bodyId'] for i in rec],'optogenetic_effective_current_pA':dose,'policy':'manual physiological prior; independent joint protocol, not tuned to endpoint scores'},indent=2));r=simulate_network(W,['other']*len(m),m,p,drive=drive,record_indices=rec);n=r['valid_record_count'];np.savez_compressed(O/(mode+'.npz'),body_ids=[x['bodyId'] for x in m],spikes=r['spike_counts_1ms'],record_body_ids=[m[i]['bodyId'] for i in rec],time_ms=r['record_time_ms'],voltage=r['voltage_first12'][:n],calcium=r['calcium_first12_uM'][:n],currents_pA=r['synaptic_currents_pA'][:n],conductances_nS=r['synaptic_conductances_nS'][:n]);cells=[]
for j,i in enumerate(rec):
 sel=r['record_time_ms']>=400;v=r['voltage_first12'][:n,j];cur=r['synaptic_currents_pA'][:n,j];cells.append({'body_id':m[i]['bodyId'],'type':m[i]['type'],'side':m[i]['somaSide'],'nt':m[i]['predictedNt'],'groups':[g for g,ii in groups.items() if i in ii],'mean_rate_hz':float(r['spike_counts_1ms'][400:,i].sum()),'mean_soma_mV':float(v[sel,0].mean()),'mean_exc_pA':float(cur[sel,0].mean()),'mean_inh_pA':float(cur[sel,1].mean())})
(O/(mode+'-diagnosis.json')).write_text(json.dumps({'condition':mode,'numerical_failure':r['numerical_failure'],'cells':cells,'scope':'neuronal pathways; no body phenotype claim'},indent=2));print(mode,[(x['type'],x['side'],x['mean_rate_hz']) for x in cells if x['type'] in ['DNg100','DNg97','LBL40','DNp09','GNG458']],flush=True)
