"""One manual intervention at a time; inspect neuronal response and currents.
No fitted behavioral labels, no reciprocal-inhibition edges added by hand.
"""
from pathlib import Path
import json,sys,hashlib
import numpy as np
from scipy import sparse
from network import simulate_network
R=Path(__file__).parent;O=R/'results/mcns-steering';mode=sys.argv[1] if len(sys.argv)>1 else 'baseline';m=json.load(open(O/'neurons.json'));W=sparse.load_npz(O/'signed-hypothesis-connectivity.npz').toarray();p=json.load(open(R/'configs/adult-network-selected.json'));p.update(dt_ms=.0125,duration_ms=1400.,onset_ms=200.,group_parameters={},inhibitory_gain=1.,gi_nS_per_synapse=.012,background_exc_gain=1.);drive=np.zeros(len(m));src=[]
if mode!='control':
 for i,x in enumerate(m):
  if x['type']=='PFL3' and x.get('functional_output_side')=='L':src.append(i)
 drive[src]=160.
if mode=='stronger-inhibition':p['gi_nS_per_synapse']=.03
if mode=='PFL2-coactivation':
 drive[[i for i,x in enumerate(m) if x['type']=='PFL2']]=160.
if mode=='PFL2-only':
 drive[:]=0;drive[[i for i,x in enumerate(m) if x['type']=='PFL2']]=160.
if mode=='right-PFL3':
 drive[:]=0;src=[i for i,x in enumerate(m) if x['type']=='PFL3' and x.get('functional_output_side')=='R'];drive[src]=160.
rec=[i for i,x in enumerate(m) if x['type'] in ['DNa02','DNa03','LAL010']]
# Include the strongest inhibitory source projections to DNa02 to locate an
# inactive relay rather than imposing the desired bilateral output pattern.
dn=[i for i,x in enumerate(m) if x['type']=='DNa02'];inh=np.where((W[:,dn]<0).any(axis=1))[0];rank=sorted(inh,key=lambda i:abs(W[i,dn]).sum(),reverse=True);rec+=rank[:10]+src[:4];rec=list(dict.fromkeys(rec));(O/(mode+'-config.json')).write_text(json.dumps({'parameters':p,'drive_nonzero_body_ids':[m[i]['bodyId'] for i in np.flatnonzero(drive)],'stimulated_output_side':'right' if mode=='right-PFL3' else 'left','record_body_ids':[m[i]['bodyId'] for i in rec],'unknowns':'all membrane/synaptic densities outside measured exemplars are priors; neuromodulatory fast edges omitted as documented'},indent=2));r=simulate_network(W,['other']*len(m),m,p,drive=drive,record_indices=rec);n=r['valid_record_count'];np.savez_compressed(O/(mode+'.npz'),spikes=r['spike_counts_1ms'],body_ids=[x['bodyId'] for x in m],voltage=r['voltage_first12'][:n],time_ms=r['record_time_ms'],currents_pA=r['synaptic_currents_pA'][:n],conductances_nS=r['synaptic_conductances_nS'][:n],calcium=r['calcium_first12_uM'][:n],record_body_ids=[m[i]['bodyId'] for i in rec]);out=[]
for j,i in enumerate(rec):
 sel=r['record_time_ms']>=400;v=r['voltage_first12'][:n,j];I=r['synaptic_currents_pA'][:n,j];out.append({'body_id':m[i]['bodyId'],'type':m[i]['type'],'side':m[i]['somaSide'],'nt':m[i]['predictedNt'],'rate_hz':float(r['spike_counts_1ms'][400:,i].sum()),'mean_soma_mV':float(v[sel,0].mean()),'mean_exc_pA':float(I[sel,0].mean()),'mean_inh_pA':float(I[sel,1].mean())})
(O/(mode+'-diagnosis.json')).write_text(json.dumps({'condition':mode,'numerical_failure':r['numerical_failure'],'cells':out,'status':'manual inspection; no behavioral or automatic loss-selected pass'},indent=2));print(mode,out[:6],flush=True)
