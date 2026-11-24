"""Restore independently rerun arrays exactly from the original supplied state + XOR delta."""
from pathlib import Path
import argparse,hashlib,json,numpy as np
p=argparse.ArgumentParser();p.add_argument('base',type=Path);p.add_argument('delta',type=Path);p.add_argument('comparison',type=Path);p.add_argument('output',type=Path);a=p.parse_args();report=json.loads(a.comparison.read_text());assert hashlib.sha256(a.base.read_bytes()).hexdigest()==report['base_state_sha256'];assert hashlib.sha256(a.delta.read_bytes()).hexdigest()==report['delta']['sha256'];arrays={}
with np.load(a.base,allow_pickle=False) as b,np.load(a.delta,allow_pickle=False) as d:
 for k,v in report['arrays'].items():
  old=b[k];raw=np.bitwise_xor(old.reshape(-1).view(np.uint8),d[k]);new=raw.view(np.dtype(v['dtype'])).reshape(v['shape']);assert hashlib.sha256(new.tobytes()).hexdigest()==v['new_array_bytes_sha256'],k;arrays[k]=new
np.savez_compressed(a.output,**arrays);print(json.dumps({'all_arrays_restored_exactly':True,'output':str(a.output),'npz_container_sha256':hashlib.sha256(a.output.read_bytes()).hexdigest(),'reference_container_sha256':report['independent_state_sha256'],'note':'NPZ compression metadata can vary across Python/NumPy/zlib versions; every restored array is individually hash-verified.'}))
