"""Restore actual BRK→premotor→MN anatomy in same MaleCNS v1.0 context.
Only this scope is extended; sensory feedback/strain models remain absent.
"""
from pathlib import Path
import csv,gzip,json,hashlib
import numpy as np
import pyarrow as pa,pyarrow.feather as ft,pyarrow.compute as pc
from scipy import sparse
R=Path(__file__).parent;N=R.parent/'conductance-rebuild-20261114';B=Path('/workspace/exports/malecns-source');old=N/'results/mcns-unified';O=N/'results/mcns-brake-extension';O.mkdir(exist_ok=True);previous=json.load(open(old/'neurons.json'));pm={int(x['bodyId']):x for x in previous};keep=set(pm)
for x in csv.DictReader(gzip.open(R/'routes/BRK-twohop-MN.csv.gz','rt')):keep.update(int(x[k]) for k in ['sensory_or_BRK','relay','MN'])
for x in csv.DictReader(open(R/'routes/leg-MN-identities.csv')):keep.add(int(x['bodyId']))
a={x['bodyId']:x for x in ft.read_table(B/'body-annotations-male-cns-v1.0-minconf-0.5.feather').to_pylist()};ids=pa.array(sorted(keep),type=pa.int64());nts=ft.read_table(B/'body-neurotransmitters-male-cns-v1.0.feather');nts={int(x['body']):x for x in nts.filter(pc.is_in(nts['body'],value_set=ids)).to_pylist()};rows=[]
for b in sorted(keep):
 if b in pm:x={**pm[b]}
 else:
  x={k:a[b].get(k) for k in ['bodyId','type','flywireType','hemibrainType','mancBodyid','mancType','synonyms','somaSide','rootSide','somaNeuromere','superclass','class','matchingNotes','instance','subclass','entryNerve']};x['bodyId']=str(b);x['class']=x['superclass'];x['predictedNt']=nts.get(b,{}).get('consensus_nt') or nts.get(b,{}).get('predicted_nt') or 'unknown'
 x['connectome_namespace']='MaleCNS_v1.0';rows.append(x)
idx={int(x['bodyId']):i for i,x in enumerate(rows)};raw=B/'connectome-weights-male-cns-v1.0-minconf-0.5-significant-only.feather';w=ft.read_table(raw,columns=['body_pre','body_post','weight'],memory_map=True);w=w.filter(pc.and_(pc.is_in(w['body_pre'],value_set=ids),pc.is_in(w['body_post'],value_set=ids)));pre=np.array([idx[x] for x in w['body_pre'].to_pylist()]);post=np.array([idx[x] for x in w['body_post'].to_pylist()]);counts=np.asarray(w['weight'],dtype=float);sign=np.array([1 if rows[i]['predictedNt']=='acetylcholine' else -1 if rows[i]['predictedNt'] in ['gaba','glutamate'] else 0 for i in pre]);U=sparse.csr_matrix((counts,(pre,post)),shape=(len(rows),len(rows)));W=sparse.csr_matrix((counts*sign,(pre,post)),shape=U.shape);W.eliminate_zeros();ii=[idx[int(x['bodyId'])] for x in previous]
for name,M in [('unsigned-connectivity.npz',U),('signed-hypothesis-connectivity.npz',W)]:
 assert (M[ii][:,ii]-sparse.load_npz(old/name)).nnz==0
 sparse.save_npz(O/name,M)
(O/'neurons.json').write_text(json.dumps(rows,indent=2)+'\n');manifest={'status':'new same-animal structural extension; no sensory-to-VNC physiological feedback implemented','nodes':len(rows),'signed_edges':W.nnz,'added_cells':len(rows)-len(previous),'old_submatrices':'signed and unsigned exactly preserved','leg_MNs':381,'sources':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [old/'neurons.json',raw,R/'routes/BRK-twohop-MN.csv.gz',Path(__file__)]},'sign_caution':'GABA negative, ACh positive, Glu negative receptor hypothesis; other transmitters only unsigned'};(O/'source-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(manifest)
