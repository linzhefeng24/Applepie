"""Extract real MANC DN→chief9A paths. No sensory EM identity is invented.
Sensory terminal prototypes are a separate mechanistic module until the hook
and claw annotation version crosswalk is recovered.
"""
from pathlib import Path
import csv,json,hashlib
import numpy as np
from scipy import sparse
R=Path(__file__).parent;B=Path('/workspace/reproduction/neuromuscular/available-chain');O=R/'results/sensory-command-context';O.mkdir(exist_ok=True);m=list(csv.DictReader((B/'neuron-metadata.csv').open()));axis=list(csv.DictReader((B/'matrix-neuron-IDs.csv').open()));assert [x['bodyId'] for x in m]==[x['MANC_body_id'] for x in axis];W=sparse.load_npz(B/'MANC-central-connections-20251006.npz').tocsr();lookup={x['bodyId']:i for i,x in enumerate(m)};source_ids=['10093','10339','10107','10103'];chief_ids=['100513','13157','14517','165560','12443','12804'];source=[lookup[b] for b in source_ids];chief=[lookup[b] for b in chief_ids];bridge=set(W[source].nonzero()[1])&set(W[:,chief].nonzero()[0]);keep=source+chief+sorted(bridge-set(source+chief));rows=[]
for i in keep:
 x={**m[i],'connectome_namespace':'MANC','source_class_original':m[i]['class']};x['class']=x['class'].replace(' ','_');rows.append(x)
sparse.save_npz(O/'connectivity.npz',W[keep][:,keep]);(O/'neurons.json').write_text(json.dumps(rows,indent=2)+'\n');manifest={'source':'author-signed MANC matrix20251006','nodes':len(rows),'edges':W[keep][:,keep].nnz,'source_matrix_sha256':hashlib.sha256((B/'MANC-central-connections-20251006.npz').read_bytes()).hexdigest(),'source_axis_sha256':hashlib.sha256((B/'matrix-neuron-IDs.csv').read_bytes()).hexdigest(),'source_ids':source_ids,'chief9A_ids':chief_ids,'identity_provenance':'Dallmann2025 SupplementaryTable4 and authors manc_9A_web_connectivity.ipynb; body IDs used, not obsolete SNpp38 labels.','boundary':'all direct/two-hop source→chief9A paths and induced edges, not full VNC. Sensory hook/claw terminal identities and per-contact conductances are not recovered.'};(O/'source-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(manifest)
