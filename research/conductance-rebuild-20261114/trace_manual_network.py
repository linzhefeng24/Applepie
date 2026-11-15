"""Manual circuit diagnosis. No score, fitted phase or endpoint selection.
Run one named intervention, inspect complete inputs/voltages/spikes/u before
choosing another. Statistics are descriptive, never an optimizer objective.
"""
from pathlib import Path
import csv,json,sys,hashlib
import numpy as np
from scipy import sparse
from scipy.ndimage import gaussian_filter1d
from network import simulate_network
R=Path(__file__).parent;O=R/'results/manual-mechanism';mode=sys.argv[1] if len(sys.argv)>1 else 'direct-baseline';meta=[{**x,'connectome_namespace':'MANC'} for x in json.load(open(O/'neurons.json'))];W=sparse.load_npz(O/'connectivity.npz');rtypes={'DNg100':'DN','IN17A001':'E1','INXXX466':'E2','IN16B036':'I1','IN19A007':'I2'};roles=[rtypes.get(x['type'],'MN' if x['class']=='motor neuron' else 'other') for x in meta]
if mode.startswith('direct'):
 keep=[i for i,r in enumerate(roles) if r!='other'];meta=[meta[i] for i in keep];roles=[roles[i] for i in keep];W=W[keep][:,keep]
p=json.load(open(R/'configs/asymmetry-guarded.json'));p.update(dt_ms=.0125,duration_ms=1600.,onset_ms=200.);drive=np.array([160. if r=='DN' else 0. for r in roles]);lookup={x['bodyId']:i for i,x in enumerate(meta)};cross=list(csv.DictReader((R/'data/model-130-channel-candidate-crosswalk.csv').open(encoding='utf-8-sig')));pools=[[lookup[b] for b in x['candidate_MANC_body_ids'].split(';') if b in lookup] for x in cross];record=list(range(26))
# Record verified example MNs from each leg/muscle category after all 26 core
# cells; every pool still remains represented in the complete spike array.
for leg in ['LF','LM','LH','RF','RM','RH']:
 for term in ['Ti flexor','Ti extensor']:
  hits=[i for i,x in enumerate(cross) if x['leg']==leg and term==x['candidate_target_labels']]
  for i in hits[:1]:
   if pools[i]:record.append(pools[i][0])
if mode.endswith('right-extensors-third'):
 p['cell_parameters']={'MANC:10461':{'excitatory_gain':.3},'MANC:10462':{'excitatory_gain':.3}}
if mode.endswith('RH-extensor-third'):
 p['cell_parameters']={'MANC:10462':{'excitatory_gain':.3}}
if mode.endswith('RH-extensor-half'):
 p['cell_parameters']={'MANC:10462':{'excitatory_gain':.5}}
if mode.endswith('extensor-gain'):
 p['group_parameters']={**p.get('group_parameters',{}),'motor neuron|type:Ti extensor MN':{'excitatory_gain':.5}}
if mode.endswith('premotor-inhibition'):
 p['inhibitory_gain']=.1
if mode.endswith('balanced-MN'):
 p['inhibitory_gain']=.1;p['mn_gain']=3.
if mode.endswith('weaker-I2'):
 p['I2_gain']=.75
if mode.endswith('stronger-E1'):
 p['group_parameters']={**p.get('group_parameters',{}),'intrinsic neuron|type:IN17A001':{'excitatory_gain':1.25}}
if mode.endswith('E2-silenced'):
 ablate=[i for i,r in enumerate(roles) if r=='E2']
else:ablate=[]
(O/(mode+'-config.json')).write_text(json.dumps({'parameters':p,'drive_pA':drive.tolist(),'body_ids':[x['bodyId'] for x in meta],'record_body_ids':[meta[i]['bodyId'] for i in record],'ablate_body_ids':[meta[i]['bodyId'] for i in ablate],'parameter_sha256':hashlib.sha256(json.dumps(p,sort_keys=True).encode()).hexdigest(),'purpose':'manual mechanism inspection, not automated optimization'},indent=2))
r=simulate_network(W.toarray(),roles,meta,p,drive=drive,ablate=ablate,record_indices=record);n=r['valid_record_count'];spikes=r['spike_counts_1ms'];rates=np.array([spikes[:,pool].mean(axis=1)*1000 if pool else np.zeros(len(spikes)) for pool in pools]).T
# One hand-set, shared 20ms NMJ filter and common gain, without fitted offsets.
filtered=np.empty_like(rates);state=np.zeros(len(pools));d=np.exp(-1/20)
for k in range(len(rates)):state=d*state+(1-d)*rates[k];filtered[k]=state
u=np.clip(filtered/50,0,1);np.savez_compressed(O/(mode+'.npz'),cell_parameters=r['cell_parameters'],spikes=spikes,body_ids=[x['bodyId'] for x in meta],roles=roles,record_body_ids=[meta[i]['bodyId'] for i in record],voltage=r['voltage_first12'][:n],calcium=r['calcium_first12_uM'][:n],currents_pA=r['synaptic_currents_pA'][:n],conductances_nS=r['synaptic_conductances_nS'][:n],time_ms=r['record_time_ms'],u=u,muscle_ids=[x['model_channel'] for x in cross],muscle_legs=[x['leg'] for x in cross]);desc=[]
for pos,i in enumerate(record):
 x=meta[i];sel=r['record_time_ms']>=400.;v=r['voltage_first12'][:n,pos];I=r['synaptic_currents_pA'][:n,pos];desc.append({'body_id':x['bodyId'],'type':x['type'],'leg':x.get('somaNeuromere','')+'_'+(x.get('somaSide') or x.get('rootSide','')),'rate_hz':float(spikes[400:,i].sum()/1.2),'mean_soma_mV':float(v[sel,0].mean()),'mean_exc_current_pA':float(I[sel,0].mean()),'mean_inh_current_pA':float(I[sel,1].mean()),'mean_coupling_current_pA':float(I[sel,2].mean())})
(O/(mode+'-diagnosis.json')).write_text(json.dumps({'numerical_failure':r['numerical_failure'],'nodes':len(meta),'cells':desc,'u_policy':'all candidate pools, common causal20ms filter /50Hz; zero for unmapped; no fitted time curves or per-leg phase','status':'requires manual trace inspection; no automatic pass or selection'},indent=2));print(mode,'finished','cells',len(meta),'rates',[round(x['rate_hz'],1) for x in desc[:26]],flush=True)
