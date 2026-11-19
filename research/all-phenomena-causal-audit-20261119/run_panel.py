"""One fixed physiological model, explicit inputs, exact spikes and named intermediate states."""
from pathlib import Path
import argparse,hashlib,json,sys,time,numpy as np
from runtime import Model
R=Path(__file__).resolve().parent;PLAN=json.loads((R/'panel.json').read_text());GROUPS=json.loads((R/'identity_registry.json').read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
CODE_HASHES={p:sha(R/p) for p in ['run_panel.py','runtime.py','terminal_dynamics.py','panel.json']}
def run(case):
 spec=PLAN['cases'][case];m=Model(R/'cache/component_model.yaml');assert m.sha256==PLAN['model_sha256'];events=[];amp=spec.get('amplitude_pA',PLAN['current_pA']);groups={k:[b for b in v['body_ids'] if b in m.lookup] for k,v in GROUPS.items()};record=[]
 def put(group,on,off):
  ids=groups[group];side=spec.get('source_soma_side')
  if side:ids=[b for b in ids if m.neurons[m.lookup[b]].get('somaSide')==side]
  if not ids:raise ValueError('Unresolved source '+group)
  events.append({'neuron_ids':ids,'on_ms':on,'off_ms':off,'current_pA':amp})
 for g in spec['sources']:
  put(g,PLAN['probe_on_ms'] if spec.get('source_window')=='probe' else PLAN['drive_on_ms'],PLAN['probe_off_ms'] if spec.get('source_window')=='probe' else PLAN['drive_off_ms'])
 if spec.get('modulator'):put(spec['modulator'],PLAN['modulator_on_ms'],PLAN['modulator_off_ms'])
 if spec.get('additional_probe'):put(spec['additional_probe'],PLAN['probe_on_ms'],PLAN['probe_off_ms'])
 ablate=[]
 for g in spec.get('ablate_groups',[])+([spec['ablate_group']] if spec.get('ablate_group') else []):ablate+=groups[g]
 dn=np.array([m.lookup[b] for b in groups['DNg100']]);cut=np.zeros(len(m.pre),bool)
 if spec.get('cut_inhibitory_sources_to_DN'):cut=np.isin(m.pre,[m.lookup[b] for b in spec['cut_inhibitory_sources_to_DN']])&np.isin(m.post,dn)&(m.weight<0)
 if spec.get('cut_all_inhibition_to_DN'):cut=np.isin(m.post,dn)&(m.weight<0)
 m.weight[cut]=0
 if 'motor_GABA_factor' in spec:
  pre=np.array([n.get('predictedNt')=='gaba' for n in m.neurons]);post=np.array([n.get('superclass')=='vnc_motor' for n in m.neurons]);mask=pre[m.pre]&post[m.post];m.weight[mask]*=spec['motor_GABA_factor']
 for g in ['DNg100','DNb08','P9','MDN','BPN','FG','BB','BRK','BON1','DNa02','DNa03','DNg13','DNg97','DNg75','DNg55','DNg16','DNg74','LAL010','E1','E2','I1','I2','E3','E4','E5']:
  ids=groups[g];preferred=[b for b in ids if m.neurons[m.lookup[b]].get('somaNeuromere')=='T1'];record+=(preferred or ids)[:2]
 record+=groups['chief_9A']+groups['hook']+groups['claw'][:2]+groups['club'][:2]+['11006','10856','11982','516820','26344','800061','802072'];record=list(dict.fromkeys(b for b in record if b in m.lookup));start=time.monotonic();out=R/'results';out.mkdir(exist_ok=True)
 base={'case':case,'spec':spec,'events':events,'ablate_ids':ablate,'directed_edges_cut':int(cut.sum()),'model_sha256':m.sha256,'code_hashes_at_start':CODE_HASHES,'weights_sha256':hashlib.sha256(m.weight.tobytes()).hexdigest(),'cell_array_sha256':hashlib.sha256(m.cells.tobytes()).hexdigest(),'assay_scope':'neural component probe, not full experimental phenotype','duration_ms':PLAN['duration_ms'],'record_interval_ms':PLAN['record_interval_ms']}
 try:
  r=m.run_neural(events=events,record_ids=record,record_interval_ms=PLAN['record_interval_ms'],ablate_ids=ablate);u=m.muscle_excitation(r);raw=out/(case+'.npz');np.savez_compressed(raw,spikes=r['spikes'],events_step_cell=m.exact_events,voltage=r['voltage'],calcium=r['calcium'],currents_pA=r['currents_pA'],conductances_nS=r['conductances_nS'],time_ms=r['time_ms'],record_indices=r['record_indices'],body_ids=np.array(m.ids),u=u)
  data={};ev=m.exact_events
  for g,ids in groups.items():
   ii=[m.lookup[b] for b in ids];data[g]={'body_ids':ids,'spikes_200_600ms':r['spikes'][200:600,ii].sum(axis=0).tolist(),'spikes_600_1100ms':r['spikes'][600:1100,ii].sum(axis=0).tolist(),'spikes_1100_1500ms':r['spikes'][1100:1500,ii].sum(axis=0).tolist()}
  base.update(status='independently_run_component_probe',seconds=time.monotonic()-start,spikes_total=int(r['spikes'].sum()),groups=data,recorded_ids=record,raw={'name':raw.name,'bytes':raw.stat().st_size,'sha256':sha(raw)},u_nonzero_channels=int((u.max(axis=0)>0).sum()))
 except Exception as e:base.update(status='failed_not_a_pass',error=type(e).__name__+': '+str(e),seconds=time.monotonic()-start)
 (out/(case+'.json')).write_text(json.dumps(base,indent=2)+'\n');print(case,base['status'],base.get('spikes_total'),round(base['seconds'],1),flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('cases',nargs='+',choices=PLAN['cases']);a=p.parse_args()
 for case in a.cases:run(case)
