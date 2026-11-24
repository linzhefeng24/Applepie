"""Compare independent neural integration with the supplied archive, and save exact XOR deltas.
Large existing baseline state is referenced rather than duplicated into Git history.
"""
from pathlib import Path
import hashlib,json,zipfile,numpy as np
R=Path(__file__).resolve().parent;P=R/'cache/extracted/flybody_male_full';base=P/'04_results/data/neural_state.npz';new=P/'04_results/data/neural_state_recomputed.npz';out=R/'cache/neural_rerun_delta.npz'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
rows={}
with np.load(base,allow_pickle=False) as b,np.load(new,allow_pickle=False) as n,zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 assert b.files==n.files
 for k in n.files:
  a=n[k];old=b[k];assert a.dtype==old.dtype and a.shape==old.shape
  x=np.bitwise_xor(a.reshape(-1).view(np.uint8),old.reshape(-1).view(np.uint8));same=bool(np.array_equal(a,old));row={'dtype':a.dtype.str,'shape':list(a.shape),'array_equal':same,'new_array_bytes_sha256':hashlib.sha256(a.tobytes()).hexdigest(),'different_bytes':int(np.count_nonzero(x))}
  if np.issubdtype(a.dtype,np.number):row.update(max_abs_error=float(np.max(abs(a-old))) if a.size else 0,all_finite=bool(np.isfinite(a).all()))
  with z.open(k+'.npy','w',force_zip64=True) as f:np.lib.format.write_array(f,x,allow_pickle=False)
  assert np.array_equal(np.bitwise_xor(x,old.reshape(-1).view(np.uint8)).view(a.dtype).reshape(a.shape),a)
  rows[k]=row
report={'source_asset_url':'https://github.com/linzhefeng24/Applepie/releases/download/new/flybody_male_full.zip','base_state_member':'flybody_male_full/04_results/data/neural_state.npz','base_state_sha256':sha(base),'independent_state_sha256':sha(new),'arrays':rows,'spikes_total':int(np.load(new,allow_pickle=False)['spikes'].sum()),'delta':{'name':out.name,'bytes':out.stat().st_size,'sha256':sha(out)},'all_exact_delta_roundtrips_verified':True,'meaning':'A zero delta means the independent rerun reproduced that array exactly; restore with restore_neural_delta.py using the original base archive.'};(R/'neural_comparison.json').write_text(json.dumps(report,indent=2)+'\n');print('spikes',report['spikes_total'],'spike_equal',rows['spikes']['array_equal'],'all_array_equal',all(x['array_equal'] for x in rows.values()),'delta_bytes',out.stat().st_size)
log=(R/'cache/recomputed-render.log').read_text();r=next(json.loads(s) for s in log.splitlines() if s.startswith('{'));(R/'fresh_run.json').write_text(json.dumps(r,indent=2)+'\n')
