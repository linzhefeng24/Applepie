"""Scope-aware report: qualitative agreement is not experimental reproduction."""
from pathlib import Path
import json,hashlib,sys,importlib.metadata as md
import numpy as np,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).parent;O=R/'results/experimental-panel';rows=json.load(open(O/'trials.json'));confirm=json.load(open(O/'confirmation.json'));configs={}
for a in ['BRK_BON1','MDN_LBL40']:
 p=dict(next(x['config'] for x in rows if x['assay']==a and x['target_excitatory_gain_multiplier']==1));p['dt_ms']=.003125;configs[a]=p
confirm['configs']=configs;confirm['config_metadata_note']='Reconstructed from saved baseline config with only dt changed, restoring both assay configs after writer accumulated results but overwrote the configs dictionary.';(O/'confirmation.json').write_text(json.dumps(confirm,indent=2))
fig,ax=plt.subplots(1,2,figsize=(10,4),layout='constrained');summary=[]
for j,a in enumerate(configs):
 r=next(x for x in rows if x['assay']==a and x['target_excitatory_gain_multiplier']==1);ns=len(json.load(open(O/(a+'-neurons.json'))));proto=next(x for x in json.load(open(O/'protocol.json'))['assays'] if x['id']==a);nt=len(proto['target_ids']);srcn=len(proto['source_ids'])
 for cond in ['control','stimulated']:
  z=np.load(O/f'{a}-gain1-{cond}.npz');v=z['voltage'];t=np.arange(len(v))*.5;ax[j].plot(t,v[:,srcn:srcn+nt,0].mean(axis=1),label=cond,linewidth=.6)
 ax[j].set(title=a,xlabel='Time (ms)',ylabel='Mean target soma voltage (mV)');ax[j].axvspan(400,2400,color='grey',alpha=.1);ax[j].legend()
 fine=[x for x in confirm['results'] if x['assay']==a];summary.append({'id':a,'status':'partial','baseline_delta_soma_mV':r['delta_soma_mV'],'finer_checks':fine,'selected_target_gain_multiplier':1.,'config_sha256':hashlib.sha256(json.dumps(configs[a],sort_keys=True).encode()).hexdigest(),'scope':'qualitative evoked response in path-focused HH circuit; not measured fluorescence or behavioral reproduction'})
fig.savefig(O/'neuronal-response.png',dpi=150)
result={'assays':summary,'full_experimental_phenomena_newly_passed':0,'partial_qualitative_matches':2,'selected_gain':'no extra target gain fitting; baseline sufficient','software':{'python':sys.version,**{p:md.version(p) for p in ['numpy','scipy','numba','matplotlib']}},'dose_policy':'80pA may be subthreshold; light-to-current calibration absent, no corresponding experimental dose-response claim','source':'new independent simulation, not historical checkpoint recovery'};(O/'summary.json').write_text(json.dumps(result,indent=2))
b=json.load(open(R/'brain.json'));b['experimental_neuronal_panel']={'report':'EXPERIMENTAL_CONSTRAINTS.md','results':'results/experimental-panel/summary.json','priority_policy':'measured neural responses/interventions before muscle trajectories and paper model predictions','status':'partial','new_full_experimental_passes':0,'new_qualitative_matches':2,'remaining_majority_unvalidated':True};(R/'brain.json').write_text(json.dumps(b,ensure_ascii=False,indent=2)+'\n')
