"""Extract a structural olfactory candidate network from official MaleCNS v1.0.
No synthetic edges, no transmitter-to-sign conversion, no physiological weights.
DAN membership uses direct anatomical contact with KC/MBON; this is a candidate
selector, not proof of modulatory release or functional learning involvement.
"""
from pathlib import Path
import argparse,hashlib,json,platform
import numpy as np
import pandas as pd
import pyarrow
import pyarrow.feather as feather
R=Path(__file__).resolve().parent
CLASSES={'olfactory':'ORN','ALLN':'LN','ALPN':'PN','ALIN':'ALIN','ALON':'ALON','Kenyon_Cell':'KC','MBON':'MBON'}
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('source_dir',type=Path);args=p.parse_args();source_manifest=json.loads((R/'sources.json').read_text());paths={}
 for x in source_manifest:
  path=args.source_dir/Path(x['source_url']).name;assert path.stat().st_size==x['bytes'] and sha(path)==x['sha256'];paths[x['role']]=path
 a=feather.read_table(paths['annotations']).to_pandas();w=feather.read_table(paths['weights'],columns=['body_pre','body_post','weight']).to_pandas();nt=feather.read_table(paths['transmitters'],columns=['body','consensus_nt']).to_pandas()
 assert not a.bodyId.duplicated().any();assert not nt.body.duplicated().any()
 core=a['class'].isin(CLASSES)|a['type'].eq('APL');mb=set(a.loc[a['class'].isin(['Kenyon_Cell','MBON']),'bodyId']);dan=set(a.loc[a['class'].eq('DAN'),'bodyId'])
 candidates=w.loc[(w.body_pre.isin(dan)&w.body_post.isin(mb))|(w.body_post.isin(dan)&w.body_pre.isin(mb)),['body_pre','body_post']];connected_dan=(set(candidates.body_pre)|set(candidates.body_post))&dan
 n=a.loc[core|a.bodyId.isin(connected_dan),['bodyId','type','class','superclass','somaSide','rootSide','flywireType','hemibrainType','receptorType']].copy();n['model_group']=n['class'].map(CLASSES);n.loc[n['type'].eq('APL'),'model_group']='APL';n.loc[n.bodyId.isin(connected_dan),'model_group']='DAN_candidate';n=n.merge(nt.rename(columns={'body':'bodyId'}),on='bodyId',how='left',validate='one_to_one').sort_values('bodyId');assert n.model_group.notna().all()
 e=w.loc[w.body_pre.isin(n.bodyId)&w.body_post.isin(n.bodyId)].copy();g=n.set_index('bodyId').model_group;e['pre_group']=e.body_pre.map(g);e['post_group']=e.body_post.map(g)
 matrix=e.groupby(['pre_group','post_group']).agg(directed_pairs=('weight','size'),anatomical_synapses=('weight','sum')).reset_index();matrix.to_csv(R/'group-connectivity.csv',index=False)
 n.to_csv(R/'neurons.csv',index=False)
 cache=R/'cache';cache.mkdir(exist_ok=True);np.savez_compressed(cache/'edges.npz',body_pre=e.body_pre.to_numpy(dtype=np.int64),body_post=e.body_post.to_numpy(dtype=np.int64),anatomical_synapses=e.weight.to_numpy(dtype=np.int64))
 report={'dataset':'MaleCNS v1.0 minconf0.5 significant-only','status':'structural candidate extraction; not physiological simulation','source_annotation_rows':len(a),'source_directed_pairs':len(w),'candidate_nodes':len(n),'candidate_directed_pairs':len(e),'candidate_anatomical_synapses':int(e.weight.sum()),'groups':{str(k):int(v) for k,v in n.model_group.value_counts().items()},'transmitter_counts':{str(k):int(v) for k,v in n.consensus_nt.fillna('unavailable').value_counts().items()},'APL_ids':list(map(int,n.loc[n.model_group.eq('APL'),'bodyId'])),'all_DAN_annotation_count':len(dan),'selected_DAN_count':len(connected_dan),'caveats':['annotations cover more bodies than the reconstructed connected network; source_annotation_rows is not validated whole-CNS neuron count','class olfactory, ALPN etc are annotation selectors, not a guarantee every neuron responds to our chosen odors','DAN candidates may include nonolfactory/multifunctional neurons','DAN anatomical synapses do not enumerate all volume transmission','significant-only missing edge is not confirmed biological absence','No synapse coordinates or morphology read in this step; compartment placement unresolved','No edge assigned a sign from glutamate or dopamine alone'],'outputs':{x.name:{'bytes':x.stat().st_size,'sha256':sha(x)} for x in [R/'neurons.csv',R/'group-connectivity.csv',cache/'edges.npz']},'software':{'python':platform.python_version(),'pandas':pd.__version__,'numpy':np.__version__,'pyarrow':pyarrow.__version__},'command':'PYTHONPATH=/tmp/olfactory-deps python research/malecns-olfactory-physiology-20261119/extract_network.py /workspace/exports/malecns-source'}
 (R/'network-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
