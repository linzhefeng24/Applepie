"""Trace observed source→target transmission and whole-cell input balance.

Event loads are descriptive approximations from real saved spikes/counts, not
causal attribution. Saved total conductances/currents provide actual integration
outputs; a smaller inhibitory current need not mean less inhibition because
hyperpolarization reduces chloride driving force. No score or automatic fit.
"""
from pathlib import Path
import json,csv,hashlib
import numpy as np
from scipy import sparse
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).parent;N=R.parent/'conductance-rebuild-20261114';B=N/'results/mcns-unified';m=json.load(open(B/'neurons.json'));W=sparse.load_npz(B/'signed-hypothesis-connectivity.npz').tocsc();O=R/'diagnostics';O.mkdir(exist_ok=True);rows=[];fig,axs=plt.subplots(4,3,figsize=(15,12),sharex=True)
for row,(base,case,target,side) in enumerate([('P9','P9+BB','DNg97','L'),('P9','P9+BB','DNg97','R'),('MDN','MDN+BRK','LBL40','L'),('MDN','MDN+BRK','IN27X001','L')]):
 item={'baseline':base,'case':case,'target_type':target,'side':side,'conditions':[]};target_i=next(i for i,x in enumerate(m) if x['type']==target and x['somaSide']==side);item['target_body_id']=m[target_i]['bodyId'];edge_rows=[]
 for c in [base,case]:
  path=N/f'results/frozen-neural-panel-unified-r9/{c}.npz';z=np.load(path);assert list(map(str,z['body_ids']))==[str(x['bodyId']) for x in m];rec=list(map(str,z['record_body_ids'])).index(str(m[target_i]['bodyId']));t=z['time_ms'];sel=(t>=500)&(t<950);rates=z['spikes'][500:950].sum(0)/.45;v=z['voltage'][sel,rec];cond=z['conductances_nS'][sel,rec];cur=z['currents_pA'][sel,rec];d={'condition':c,'target_rate_hz':float(rates[target_i]),'mean_soma_mV':float(v[:,0].mean()),'mean_axon_mV':float(v[:,1].mean()),'mean_ge_nS':float(cond[:,0].mean()),'mean_gi_nS':float(cond[:,1].mean()),'mean_exc_current_pA':float(cur[:,0].mean()),'mean_inh_current_pA':float(cur[:,1].mean()),'mean_axon_to_soma_coupling_current_pA':float(cur[:,2].mean()),'input_sha256':hashlib.sha256(path.read_bytes()).hexdigest()};item['conditions'].append(d)
  column=W[:,target_i].tocoo();cp=z['cell_parameters']
  for i,w in zip(column.row,column.data):
   ge=.012 if w>0 else .006;gain=cp[target_i,5] if w>0 else cp[i,6];event=abs(w)*ge*gain*cp[i,12]*rates[i];edge_rows.append({'condition':c,'pre':m[i]['bodyId'],'pre_type':m[i]['type'],'pre_NT':m[i]['predictedNt'],'post':m[target_i]['bodyId'],'signed_synapse_count':float(w),'pre_rate_hz':float(rates[i]),'peak_conductance_event_load_nS_per_s':float(event)})
  axs[row,0].plot(t,z['voltage'][:,rec,0],lw=.65,label=c+' soma');axs[row,0].plot(t,z['voltage'][:,rec,1],lw=.4,alpha=.55,label=c+' axon');axs[row,1].plot(t,z['conductances_nS'][:,rec,0],label=c+' gE');axs[row,1].plot(t,z['conductances_nS'][:,rec,1],label=c+' gI');axs[row,2].plot(np.arange(1600),np.convolve(z['spikes'][:,target_i],np.ones(50)/.05,mode='same'),label=c)
 file=O/(target+'-'+side+'-incoming-events.csv')
 with file.open('w',newline='') as f:wr=csv.DictWriter(f,fieldnames=list(edge_rows[0]));wr.writeheader();wr.writerows(edge_rows)
 edge_rows.sort(key=lambda x:x['peak_conductance_event_load_nS_per_s'],reverse=True);item['largest_case_inputs']=[x for x in edge_rows if x['condition']==case][:15];item['direct_stimulated_source_inputs']=[x for x in edge_rows if x['condition']==case and x['pre_type'] in ['DNg60','AN19A018','MDN','DNp50']];rows.append(item)
 for ax in axs[row]:ax.grid(alpha=.2);ax.set_xlim(150,1550)
 axs[row,0].set_ylabel(target+' '+side)
for ax,title in zip(axs[0],['Soma/axon voltage (mV)','Actual input conductance (nS)','Target rate,50ms smoothing(Hz)']):ax.set_title(title)
for ax in axs[-1]:ax.set_xlabel('Time (ms)')
for ax in axs[:,1: ].flat:ax.legend(fontsize=6)
fig.tight_layout();fig.savefig(O/'key-route-traces.png',dpi=150)
(O/'route-diagnosis.json').write_text(json.dumps({'method':__doc__,'scope':'existing saved r9 runs independently inspected; no new experiment claimed for these four conditions','graph_sha256':hashlib.sha256((B/'signed-hypothesis-connectivity.npz').read_bytes()).hexdigest(),'targets':rows},indent=2)+'\n')
for x in rows:print(x['target_type'],x['side'],x['conditions'])
