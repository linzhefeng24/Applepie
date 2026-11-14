"""Build plots and evidence audit from actual saved runs, never placeholders."""
from pathlib import Path
import json,hashlib
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
from metrics import burst_envelope
R=Path(__file__).parent;OUT=R/'results';plt.rcParams.update({'font.size':9})
def read(n):return json.loads((OUT/n).read_text())
adult=read('adult-intact-suite.json');old=read('intact-suite.json');meta=read('adult-intact-metadata.json');cases={x['condition']:x for x in adult};mn=np.array([i for i,x in enumerate(meta) if x['class']=='motor neuron']);baseline=cases['baseline'];f0=np.mean([baseline['summary']['cells'][j]['burst_frequency_hz'] for j in [1,2]])
classification={}
for row in adult:
 n=row['condition'];z=np.load(OUT/f'adult-intact-{n}.npz');counts=z['spikes'];bursts=[burst_envelope(counts[:,j]) for j in mn]
 classification[n]={'periodic_spiking_MN':row['summary']['rhythmic_MN'],'multispike_burst_MN':sum(x['bursting'] for x in bursts),'core_mean_peak_frequency_hz':float(np.mean([row['summary']['cells'][j]['burst_frequency_hz'] for j in [1,2]])),'core_periodic':all(row['summary']['cells'][j]['rhythmic'] for j in [1,2]),'MN_with_any_spikes':sum(row['summary']['cells'][j]['mean_spikes_per_s']>0 for j in mn)}
(OUT/'spiking-vs-burst-classification.json').write_text(json.dumps(classification,indent=2))
# Figure1: full-network raw voltages/spikes + frequency and ablation outcomes.
z=np.load(OUT/'adult-intact-baseline.npz');fig,ax=plt.subplots(2,2,figsize=(12,7));t=np.arange(len(z['voltage'])-1)*.5
for j,label in [(1,'E1'),(2,'E2'),(4,'I2')]:ax[0,0].plot(t,z['voltage'][:-1,j,1],label=label,lw=.6)
ax[0,0].set(xlabel='time (ms)',ylabel='axon V (mV)',xlim=(300,1100),title='Full 4,604-cell T1 network: actual HH voltages');ax[0,0].legend(loc='upper right')
for k,j in enumerate(mn):
 times=np.where(z['spikes'][:,j]>0)[0];ax[0,1].scatter(times,np.full(len(times),k),s=.5,color='black')
ax[0,1].set(xlabel='time (ms)',ylabel='front-leg MN index',title='All 144 front-leg MNs; periodicity ≠ burst envelope')
labels=['drive_120','baseline','drive_200','drive_240'];amps=[120,160,200,240];ax[1,0].plot(amps,[classification[n]['core_mean_peak_frequency_hz'] for n in labels],'o-');ax[1,0].set(xlabel='DNg100 injected current (pA)',ylabel='core output frequency (Hz)',title='Frequency remains nonmonotonic (FAILED target)')
labels=['baseline','E1_silenced','E2_silenced','I1_silenced','I2_silenced'];x=np.arange(len(labels));ax[1,1].bar(x-.18,[classification[n]['periodic_spiking_MN'] for n in labels],.36,label='periodic spikes');ax[1,1].bar(x+.18,[classification[n]['multispike_burst_MN'] for n in labels],.36,label='multispike bursts');ax[1,1].set_xticks(x,['base','-E1','-E2','-I1','-I2']);ax[1,1].set(ylabel='MN count',title='Ablation with adult-reference MN physiology');ax[1,1].legend();fig.tight_layout();fig.savefig(OUT/'network-validation.png',dpi=170);plt.close(fig)
# Figure2: adult class fits and current recruitment.
fi=read('adult-fI.json');cal=read('adult-calibration.json');mid=read('intermediate-refinement.json');slow=read('slow-rest-grid.json')[0];targets=[150,300,700];measured=[cal['fast']['measured_model']['rin_MOhm'],min(mid,key=lambda x:x['loss'])['measured_model']['rin_MOhm'],slow['measured_model']['differential_Rin_MOhm']]
fig,ax=plt.subplots(1,3,figsize=(12,3.3));x=np.arange(3);ax[0].bar(x-.18,targets,.36,label='adult target');ax[0].bar(x+.18,measured,.36,label='model');ax[0].set_xticks(x,['fast','intermediate','slow']);ax[0].set(ylabel='input resistance (MOhm)',title='Class exemplars; EM subtypes unassigned');ax[0].legend()
for kind,row in fi.items():ax[1].plot([q['current_pA'] for q in row['fI']],[q['rate_hz'] for q in row['fI']],'o-',label=kind)
ax[1].set(xlabel='injected current (pA)',ylabel='spikes / s',title='Slow → intermediate → fast recruitment');ax[1].legend();ax[2].bar(x,[fi[k]['fI'][0]['rate_hz'] for k in ['fast','intermediate','slow']]);ax[2].axhline(30,color='gray',ls='--');ax[2].set_xticks(x,['fast','intermediate','slow']);ax[2].set(ylabel='rest spikes / s',title='Slow tonic rest restored (~31 Hz)');fig.tight_layout();fig.savefig(OUT/'adult-MN-calibration.png',dpi=170);plt.close(fig)
# Figure3: actual held-out muscle readout, including explicit missing-map mask.
z=np.load(OUT/'adult-muscle-readout.npz');mask=z['mapped'];t=z['time_s'];order=np.concatenate([np.where(np.char.startswith(z['muscle_ids'],leg+':'))[0] for leg in ['LF','LM','LH','RF','RM','RH']]);fig,ax=plt.subplots(2,2,figsize=(12,7));v0=ax[0,0].imshow(z['target_a'][:,order].T,aspect='auto',origin='lower',extent=(0,.4,0,130),vmin=0,vmax=1);ax[0,0].set(title='Old A target activation (130 channels)',ylabel='channel, reordered by leg')
ax[0,1].imshow(z['predicted_a'][:,order].T,aspect='auto',origin='lower',extent=(0,.4,0,130),vmin=0,vmax=1);ax[0,1].set(title='HH → candidate MN pool → u → native a')
err=np.sqrt(np.mean((z['predicted_a'][1200:]-z['target_a'][1200:])**2,axis=0));ax[1,0].bar(np.arange(130),err,color=np.where(mask,'steelblue','tomato'));ax[1,0].set(xlabel='original channel index',ylabel='holdout activation RMSE',title='Red = no candidate anatomical mapping (26)')
for j in [0,1,14]:ax[1,1].plot(t,z['target_a'][:,j],lw=1,label=f'target {j}');ax[1,1].plot(t,z['predicted_a'][:,j],ls='--',lw=1,label=f'prediction {j}')
ax[1,1].axvline(.24,color='black',ls=':');ax[1,1].set(xlabel='time (s)',ylabel='activation',title='Fixed example channels; last40% held out');ax[1,1].legend(ncol=2,fontsize=7);fig.colorbar(v0,ax=ax[0,:].tolist(),fraction=.025);fig.subplots_adjust(hspace=.35,wspace=.25,right=.92);fig.savefig(OUT/'muscle-activation-fit.png',dpi=170);plt.close(fig)
# Machine-readable test audit; whole-body statements remain untested.
items=[]
def add(id,status,observation,scope):items.append({'id':id,'status':status,'observed':observation,'scope':scope})
add('E1_necessity','pass' if classification['E1_silenced']['periodic_spiking_MN']==0 else 'fail',classification['E1_silenced'],'fixed adult-reference config, full T1 graph, current timestep')
add('E2_necessity','pass' if classification['E2_silenced']['periodic_spiking_MN']==0 else 'fail',classification['E2_silenced'],'same config; cancels periodicity, does not imply every MN silent')
add('I2_connected_rhythm','pass' if classification['baseline']['core_periodic'] else 'fail',classification['baseline'],'I2 actual edges included, not deleted')
add('I1_I2_single_ablation_redundancy','pass' if classification['I1_silenced']['core_periodic'] and classification['I2_silenced']['core_periodic'] else 'fail',{n:classification[n] for n in ['I1_silenced','I2_silenced']},'full T1 network; does not assert individual redundancy in minimum core')
f=[classification[n]['core_mean_peak_frequency_hz'] for n in ['drive_120','baseline','drive_200','drive_240']];add('intact_stimulus_frequency_monotonic','pass' if np.all(np.diff(f)>0) else 'fail',{'pA':amps,'Hz':f},'model prediction; no biological absolute current equivalence')
add('adult_recruitment_order','pass' if fi['slow']['first_tested_current_with_rate_ge5Hz']<fi['intermediate']['first_tested_current_with_rate_ge5Hz']<fi['fast']['first_tested_current_with_rate_ge5Hz'] else 'fail',{k:v['first_tested_current_with_rate_ge5Hz'] for k,v in fi.items()},'independent adult class exemplars, not mapped EM identities')
add('adult_Rin_and_rest','partial',{'target_Rin_MOhm':targets,'model_Rin_MOhm':measured,'slow_rest_hz':fi['slow']['fI'][0]['rate_hz']},'Fitted class exemplars; slow differential Rin within8%, mean potential vs experimental RMP caution')
for typ in ['DNg75','DNg97','DNg55','DNg16']:
 obs=classification[typ+'_coactivation'];add(typ+'_behavior','not_tested',{'baseline_neural_Hz':f0,'coactivation_neural_Hz':obs['core_mean_peak_frequency_hz'],'MN_classification':obs},'Only neural surrogate computed; no physical velocity, tripod coordination or step-length test')
add('DNb08_MN_periodicity','partial',classification['DNb08_alone'],'Periodic MN output exists; expected5-cell circuit attribution not established')
readout=read('adult-muscle-readout.json');add('all130_muscle_target_reproduction','fail',readout['selected'],'104 candidate mappings;59 signal channels;26 missing; high held-out error; old0.446 three-channel score not directly comparable')
add('native_muscle_interface','pass',{'derivative_error':readout['native_derivative_max_error'],'native_activation_error':readout['native_activation_replay_max_error'],'body_bridge':read('body-bridge.json')},'Matches original MuJoCo3.3.2 activation law; interface agreement is not walking success')
for name in ['PFL3_DNa03_LAL010_pushpull','DNa02_DNg13_phase_specific_turning','MDN_LBL40_LUM9_LUL130','MDN_MF14_T1T2_vsT3','DNg74_9A_hook_and_claw','BPN_P9_combo','FG_BB_BRK_direction_selective_stop','hunger_FG','load_and_split_belt_adaptation','six_leg_coordination']:
 add(name,'not_tested','No fabricated cells, edges, calcium-to-Hz targets or behavioral passes','Needs verified identity/version mapping and/or brain, sensory state and full body loop absent here')
fine=[]
for p in sorted(OUT.glob('fine-full-*.json')):fine.append({'file':p.name,**json.loads(p.read_text())})
if fine:add('fine_network_confirmation','partial',[{'file':x['file'],'dt_ms':x['config']['dt_ms'],'condition':x['condition'],'periodic_MN':x['summary']['rhythmic_MN'],'core_Hz':x['summary']['cells'][1]['burst_frequency_hz']} for x in fine],'Coarse-step failed check retained; compare fine-grid results, do not claim all full-network conditions converged')
audit={'tests':items,'evidence_entries':len(json.load(open(R/'data/phenomena-inventory.json'))['claims']),'literature_entries_are_not_test_passes':True,'classification':classification,'configuration_sha256':hashlib.sha256(json.dumps(baseline['parameters'],sort_keys=True).encode()).hexdigest(),'unmodeled':'real EM geometry; measured adult per-cell ionic densities; full brain; receptor-specific peripheral NMJs; body-to-brain sensory feedback; electrical coupling','numerics':'Backward-Euler voltage/Rush-Larsen gates; coarse dt0.025ms exploratory; fine-grid checks separately reported'}
(OUT/'phenomena-audit.json').write_text(json.dumps(audit,indent=2));print('Audit',[(x['id'],x['status']) for x in items],flush=True)
