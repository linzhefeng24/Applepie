"""Export explicitly indexed author connectivity, without cross-specimen ID mixing."""
from pathlib import Path
import csv,json,hashlib
import numpy as np
from scipy import sparse
ROOT=Path(__file__).parent
SOURCE=Path('/workspace/reproduction/neuromuscular/Pugliese_2026/data/manc t1 connectome data')
rows=list(csv.DictReader(open(SOURCE/'wTable_20250813_DNtoMN_unsorted_withModules.csv')))
raw=np.loadtxt(SOURCE/'W_20250813_DNtoMN_unsorted.csv',delimiter=',',skiprows=1)
assert np.array_equal(raw[:,0].astype(np.int64),np.array([int(x['bodyId']) for x in rows])), 'Row body IDs disagree with metadata'
W=raw[:,1:]
assert W.shape==(len(rows),len(rows));assert np.array_equal(np.arange(len(rows)),np.array([int(x['']) for x in rows]))
ids=np.array([int(x['bodyId']) for x in rows]);sparse.save_npz(ROOT/'data/t1-author-connectivity.npz',sparse.csr_matrix(W));(ROOT/'data/t1-neurons.json').write_text(json.dumps(rows,indent=2))
core_ids=[10093,10707,11751,13905,10242];core_idx=[int(np.where(ids==x)[0][0]) for x in core_ids]
np.savez_compressed(ROOT/'data/core.npz',body_ids=core_ids,weights=W[np.ix_(core_idx,core_idx)])
print('core body IDs',core_ids,'\n',W[np.ix_(core_idx,core_idx)])
manifest={'orientation':'row presynaptic, column postsynaptic; source wTable explicit index; CSV first column verified against wTable order','source_repository':'https://github.com/smpuglie/Pugliese_2026','source_files':{p.name:{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size} for p in SOURCE.iterdir() if p.is_file()},'neurons':len(rows),'MN':sum(x['class']=='motor neuron' for x in rows),'nonzero_directed_pairs':int(np.count_nonzero(W)),'core_ids':core_ids,'core_roles':['DNg100_L','E1_L','E2_L','I1_L','I2_L'],'sign_policy':'Preserve author-signed weights; not biological negative synapse counts. Glutamate interpreted per author sign, not automatically at NMJ.','I2_identity_scope':'MANC IN19A007 LHS; verify somaSide from source'}
(ROOT/'data/source-manifest.json').write_text(json.dumps(manifest,indent=2))
