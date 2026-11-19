"""Compare an independent from-initial-state rerun with the delivered baseline.
Read reference arrays only after the packaged runner has produced new results.
Reports exact equality and numeric differences; no fitting or parameter changes.
"""
from pathlib import Path
import hashlib,json
import numpy as np
R=Path(__file__).resolve().parent;P=R/'cache/extracted/Manual_FreeBody';D=P/'04_results/data';B=R/'cache/baseline'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def compare_files(old,new):
 with np.load(old,allow_pickle=False) as a,np.load(new,allow_pickle=False) as b:
  assert set(a.files)==set(b.files),(old,new,a.files,b.files)
  out={}
  for k in a.files:
   x,y=a[k],b[k];assert x.shape==y.shape,(k,x.shape,y.shape)
   numeric=x.dtype.kind in 'biufc'
   out[k]={'shape':list(x.shape),'dtype':str(x.dtype),'exact_equal':bool(np.array_equal(x,y)),'different_elements':int(np.count_nonzero(x!=y))}
   if numeric:
    out[k].update(max_absolute_difference=float(np.max(np.abs(x.astype(float)-y.astype(float)),initial=0)),all_finite=bool(np.isfinite(x).all() and np.isfinite(y).all()))
  return out
neural=compare_files(D/'neural_state.npz',D/'neural_state_recomputed.npz');body=compare_files(B/'body_state.npz',D/'body_state.npz');physical=compare_files(B/'full_physical_rollout.npz',D/'full_physical_rollout.npz')
# The packaged runner already verifies the unchanged model and cell parameter bank.
report=json.loads((P/'04_results/report.json').read_text());assert report['neural_source']=='independently recomputed this run'
import sys
sys.path.insert(0,str(P/'02_code'));from flymodel import Model
model=Model(P/'01_model/model.yaml')
with np.load(D/'neural_state.npz',allow_pickle=False) as z:a={k:z[k] for k in z.files}
with np.load(D/'neural_state_recomputed.npz',allow_pickle=False) as z:b={k:z[k] for k in z.files}
u0=model.muscle_excitation(a);u1=model.muscle_excitation(b);udiff=float(np.max(abs(u1-u0)));np.savez_compressed(R/'cache/recomputed_muscle_u.npz',u=u1)
video=[]
for p in sorted((P/'04_results/videos').glob('*.mp4')):video.append({'name':p.name,'bytes':p.stat().st_size,'sha256':sha(p)})
summary={'status':'completed_from_scratch_and_compared','neural_neurons':len(model.ids),'neural_duration_ms':float(b['time_ms'][-1]),'neural_spike_bins':int(len(b['spikes'])),'recorded_spikes':int(b['spikes'].sum()),'neural_spikes_exact':neural['spikes']['exact_equal'],'all_neural_arrays_exact':all(v['exact_equal'] for v in neural.values()),'all_recorded_body_arrays_exact':all(v['exact_equal'] for v in body.values()),'all_full_physics_arrays_exact':all(v['exact_equal'] for v in physical.values()),'muscle_u_exact':bool(np.array_equal(u0,u1)),'muscle_u_max_absolute_difference':udiff,'manual_model_sha256':model.sha256,'neural':neural,'recorded_body':body,'full_physics':physical,'fresh_replay_report':report,'new_neural_archive':{'bytes':(D/'neural_state_recomputed.npz').stat().st_size,'sha256':sha(D/'neural_state_recomputed.npz')},'videos':video,'scope':'Single unchanged software environment and one DN_drive trial; not validation of all brain.json phenomena or long-term walking','optimization':'No BPTT or tuning performed'}
(R/'comparison.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in summary.items() if k not in ['neural','recorded_body','full_physics','fresh_replay_report']},ensure_ascii=False,indent=2))
assert summary['neural_spikes_exact'] and summary['muscle_u_exact'] and summary['all_full_physics_arrays_exact'],'Rerun differs: inspect full comparison before claiming reproduction'
