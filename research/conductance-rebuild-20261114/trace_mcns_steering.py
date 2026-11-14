"""One manual intervention at a time; inspect neuronal response and currents.
No fitted behavioral labels, no reciprocal-inhibition edges added by hand.
"""
from pathlib import Path
import json,sys,hashlib
import numpy as np
from scipy import sparse
from network import simulate_network
R=Path(__file__).parent;O=R/'results/mcns-steering';mode=sys.argv[1] if len(sys.argv)>1 else 'baseline';condition=mode.removesuffix('-excDN').removesuffix('-adultDN').removesuffix('-softI').removesuffix('-fine').removesuffix('-source-bias');condition=condition.removesuffix('-restart');m=json.load(open(O/'neurons.json'));W=sparse.load_npz(O/'signed-hypothesis-connectivity.npz').toarray();p=json.load(open(R/'configs/adult-network-selected.json'));p.update(dt_ms=.0125,duration_ms=1400.,onset_ms=200.,group_parameters={},inhibitory_gain=1.,gi_nS_per_synapse=.012,background_exc_gain=1.);drive=np.zeros(len(m));src=[]
if condition!='control':
 for i,x in enumerate(m):
  if x['type']=='PFL3' and x.get('functional_output_side')=='L':src.append(i)
 drive[src]=160.
if condition=='stronger-inhibition':p['gi_nS_per_synapse']=.03
if condition=='PFL2-coactivation':
 drive[[i for i,x in enumerate(m) if x['type']=='PFL2']]=160.
if condition in ['PFL2-only','PFL2-relay-gain']:
 drive[:]=0;drive[[i for i,x in enumerate(m) if x['type']=='PFL2']]=160.
if condition=='right-PFL3':
 drive[:]=0;src=[i for i,x in enumerate(m) if x['type']=='PFL3' and x.get('functional_output_side')=='R'];drive[src]=160.
if condition in ['PFL2-relay-gain','PFL3-relay-gain']:
 p['group_parameters']={'descending_neuron|type:DNa03':{'excitatory_gain':1.25}}
if '-source-bias' in mode:
 p['group_parameters']={**p['group_parameters'],'cb_intrinsic|type:PFL2':{'axon_bias_pA':5.},'cb_intrinsic|type:PFL3':{'axon_bias_pA':5.}}
if '-fine' in mode:p['dt_ms']=.00625
if '-softI' in mode:p['gi_nS_per_synapse']=.006
if '-adultDN' in mode:p['class_parameters']={'descending neuron':{'K':.8,'axon_bias_pA':5.}}
if '-excDN' in mode:p['family_parameters']={'descending neuron|NT:acetylcholine':{'K':.8,'axon_bias_pA':5.}}
rec=[i for i,x in enumerate(m) if x['type'] in ['DNa02','DNa03','LAL010']]
# Include the strongest inhibitory source projections to DNa02 to locate an
# inactive relay rather than imposing the desired bilateral output pattern.
dn=[i for i,x in enumerate(m) if x['type']=='DNa02'];inh=np.where((W[:,dn]<0).any(axis=1))[0];rank=sorted(inh,key=lambda i:abs(W[i,dn]).sum(),reverse=True);rec+=rank[:10]+src[:4]+[i for i,x in enumerate(m) if x['type']=='PFL2'];rec=list(dict.fromkeys(rec));(O/(mode+'-config.json')).write_text(json.dumps({'parameters':p,'drive_nonzero_body_ids':[m[i]['bodyId'] for i in np.flatnonzero(drive)],'stimulated_output_side':'right' if condition=='right-PFL3' else 'left','record_body_ids':[m[i]['bodyId'] for i in rec],'unknowns':'all membrane/synaptic densities outside measured exemplars are priors; neuromodulatory fast edges omitted as documented'},indent=2));wave=None
if mode.endswith('-restart'):
 wave=np.zeros((1401,len(m)));wave[200:]=drive;wave[800:820,np.flatnonzero(drive)]=200.
r=simulate_network(W,['other']*len(m),m,p,drive=drive,record_indices=rec,drive_waveform=wave);n=r['valid_record_count'];np.savez_compressed(O/(mode+'.npz'),cell_parameters=r['cell_parameters'],spikes=r['spike_counts_1ms'],body_ids=[x['bodyId'] for x in m],voltage=r['voltage_first12'][:n],time_ms=r['record_time_ms'],currents_pA=r['synaptic_currents_pA'][:n],conductances_nS=r['synaptic_conductances_nS'][:n],calcium=r['calcium_first12_uM'][:n],record_body_ids=[m[i]['bodyId'] for i in rec]);out=[]
for j,i in enumerate(rec):
 sel=r['record_time_ms']>=400;v=r['voltage_first12'][:n,j];I=r['synaptic_currents_pA'][:n,j];out.append({'body_id':m[i]['bodyId'],'type':m[i]['type'],'side':m[i]['somaSide'],'nt':m[i]['predictedNt'],'rate_hz':float(r['spike_counts_1ms'][400:,i].sum()),'mean_soma_mV':float(v[sel,0].mean()),'mean_exc_pA':float(I[sel,0].mean()),'mean_inh_pA':float(I[sel,1].mean())})
(O/(mode+'-diagnosis.json')).write_text(json.dumps({'condition':mode,'numerical_failure':r['numerical_failure'],'cells':out,'status':'manual inspection; no behavioral or automatic loss-selected pass'},indent=2));print(mode,out[:6],flush=True)
