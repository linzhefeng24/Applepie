"""Union two same-version MaleCNS contexts and re-extract their induced edges.
This is one shared graph for steering, commands and stop tests, not a block
matrix of isolated assays and not the entire brain/VNC connectome.
"""
from pathlib import Path
import json,hashlib
import numpy as np
import pyarrow.feather as ft
import pyarrow.compute as pc
import pyarrow as pa
from scipy import sparse
R=Path(__file__).parent;O=R/'results/mcns-unified';O.mkdir(exist_ok=True);contexts=['mcns-command-v2','mcns-steering'];meta={};sources={}
for context in contexts:
 p=R/'results'/context/'neurons.json';sources[context]=hashlib.sha256(p.read_bytes()).hexdigest()
 for row in json.loads(p.read_text()):
  b=row['bodyId']
  if b in meta:
   for k in ['type','class','predictedNt']:assert meta[b][k]==row[k],(b,k)
  meta[b]={**meta.get(b,{}),**row}
order=sorted(meta,key=int);rows=[meta[b] for b in order];idx={int(b):i for i,b in enumerate(order)};raw=Path('/workspace/exports/malecns-source/connectome-weights-male-cns-v1.0-minconf-0.5-significant-only.feather');w=ft.read_table(raw,columns=['body_pre','body_post','weight'],memory_map=True);ids=pa.array([int(b) for b in order],type=pa.int64());e=w.filter(pc.and_(pc.is_in(w['body_pre'],value_set=ids),pc.is_in(w['body_post'],value_set=ids)));pre=np.array([idx[b] for b in e['body_pre'].to_pylist()]);post=np.array([idx[b] for b in e['body_post'].to_pylist()]);weight=np.array(e['weight'],dtype=float);sign=np.array([1. if rows[i]['predictedNt']=='acetylcholine' else -1. if rows[i]['predictedNt'] in ['gaba','glutamate'] else 0. for i in pre]);U=sparse.csr_matrix((weight,(pre,post)),shape=(len(rows),len(rows)));W=sparse.csr_matrix((weight*sign,(pre,post)),shape=U.shape);W.eliminate_zeros();checks={}
for c in contexts:
 old=json.load(open(R/'results'/c/'neurons.json'));ii=[idx[int(x['bodyId'])] for x in old]
 for name,M in [('unsigned-connectivity.npz',U),('signed-hypothesis-connectivity.npz',W)]:
  original=sparse.load_npz(R/'results'/c/name);delta=M[ii][:,ii]-original;assert delta.nnz==0,(c,name,delta.nnz)
 checks[c]='Both signed and unsigned original induced submatrices exactly retained.'
sparse.save_npz(O/'unsigned-connectivity.npz',U);sparse.save_npz(O/'signed-hypothesis-connectivity.npz',W);(O/'neurons.json').write_text(json.dumps(rows,indent=2)+'\n');manifest={'dataset':'MaleCNS v1.0 minconf0.5 significant-only','nodes':len(rows),'unsigned_edges':U.nnz,'signed_edges':W.nnz,'input_metadata_sha256':sources,'raw_weights_sha256':hashlib.sha256(raw.read_bytes()).hexdigest(),'submatrix_regression':checks,'context':'Union of command and steering cells with every original induced edge re-extracted; includes true between-context edges. Not full brain/VNC.','sign_policy':'ACh+, GABA-, Glu- (receptor sign unverified); other transmitters omitted from fast conductance, retained unsigned','new_edges_relative_to_old_graph_union':'May include cross-context edges absent from both isolated subgraphs, never fabricated edges.'};(O/'source-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(manifest,flush=True)
