"""Descriptive source/relay/MN checks in the newly extended brake circuit.
No LBL40-silence requirement, no arbitrary brake mask or score optimization.
"""
from pathlib import Path
import csv,json,hashlib,collections
import numpy as np
from scipy import sparse
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).parent;N=R.parent/'conductance-rebuild-20261114';B=N/'results/mcns-brake-extension';O=N/'results/frozen-neural-panel-brake-extension-r9';m=json.load(open(B/'neurons.json'));mn_ids={int(x['bodyId']) for x in csv.DictReader(open(R/'routes/leg-MN-identities.csv'))};mn=[i for i,x in enumerate(m) if int(x['bodyId']) in mn_ids];cases=['control','MDN','BRK','MDN+BRK'];rows=[];fig,axs=plt.subplots(3,2,figsize=(14,11),sharex=True);families=['Ti extensor MN','Ti flexor MN','Acc. ti flexor MN'];relaytypes=['IN07B001','IN18B011','IN19A001','IN03B019','IN03B032','IN21A017']
for case in cases:
 p=O/(case+'.npz');z=np.load(p);t=z['time_ms'];r=z['spikes'][500:950].sum(0)/.45;recorded={str(b):j for j,b in enumerate(z['record_body_ids'])};sel=(t>=500)&(t<950);groups=[];relay=[]
 for typ in families:
  ii=[i for i in mn if m[i]['type']==typ];jj=[recorded[m[i]['bodyId']] for i in ii if m[i]['bodyId'] in recorded];groups.append({'type':typ,'cells':len(ii),'mean_rate_hz':float(r[ii].mean()),'active':int((r[ii]>0).sum()),'mean_gE_nS':float(z['conductances_nS'][sel][:,jj,0].mean()),'mean_gI_nS':float(z['conductances_nS'][sel][:,jj,1].mean())})
  row=families.index(typ);sp=z['spikes'][:,ii].mean(1);axs[row,0].plot(np.arange(len(sp)),np.convolve(sp,np.ones(50)/.05,mode='same'),label=case);axs[row,1].plot(t,z['conductances_nS'][:,jj,0].mean(1),label=case+' gE');axs[row,1].plot(t,z['conductances_nS'][:,jj,1].mean(1),ls=':',label=case+' gI')
 for typ in relaytypes:
  ii=[i for i,x in enumerate(m) if x['type']==typ];relay.append({'type':typ,'cells':len(ii),'predicted_transmitters':sorted({m[i]['predictedNt'] for i in ii}),'rates_hz':r[ii].tolist()})
 rows.append({'condition':case,'raw_trace_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'leg_MNs_in_assay':len(mn),'active_leg_MNs':int((r[mn]>0).sum()),'groups':groups,'premotor_relays':relay,'numerical_failure':json.load(open(O/(case+'-diagnosis.json')))['numerical_failure']})
for row,typ in enumerate(families):
 axs[row,0].set_ylabel(typ+' meanHz');axs[row,1].set_ylabel('Input conductance(nS)')
for a in axs.flat:a.grid(alpha=.2);a.legend(fontsize=6);a.axvspan(450,950,color='orange',alpha=.08)
for a in axs[-1]:a.set_xlabel('Time(ms)')
fig.suptitle('New actual BRK→premotor→leg MN extension; no body/contact feedback');fig.tight_layout();fig.savefig(R/'diagnostics/extended-brake-traces.png',dpi=150)
report={'status':'new independently rerun model test, not behavior replication','graph':'3988-cell same MaleCNS version; former signed and unsigned submatrices exactly retained','MN_scope':'381 legMN IDs from original annotations, not inferred from incomplete copied subclass fields','time_window_ms':[500,950],'role_policy':'all annotated vnc_motor use adult300MOhm prior, other cells use previous policy; these MNs are not individually calibrated','critical_caution':'BRK behavioral stopping does not require LBL40 silence; reduced MN rate is not sufficient for joint resistance','conditions':rows};(R/'diagnostics/extended-brake-review.json').write_text(json.dumps(report,indent=2)+'\n')
for x in rows:print(x['condition'],x['active_leg_MNs'],x['groups'])
