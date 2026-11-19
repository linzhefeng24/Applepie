"""Append official MaleCNS cells/incident edges to the frozen manual R2.
No original cell parameter, edge, muscle mapping or protocol is overwritten.
New membrane parameters are borrowed priors, not measured physiology.
The committed delta is sufficient to materialize the candidate without the large sources.
"""
from pathlib import Path
import argparse,base64,collections,csv,hashlib,io,json,re,sys
import numpy as np
import yaml
R=Path(__file__).resolve().parent
BASE_SHA='858d1818b8d8394c95bb62a6ce60474cb534a83b94265ef8615e367c110d262c'
DEFAULT=R.parents[1]/'research/manual-full-rerun-20261119/cache/extracted/Manual_FreeBody'
TYPES={'EPG','EPGt','Delta7','DNb05','DNb06','DNg11','IN17A001','INXXX466','IN16B036','IN19A007','IN19B012'}
def digest(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def encode(**arrays):
 b=io.BytesIO();np.savez_compressed(b,**arrays);raw=b.getvalue()
 return dict(encoding='base64_npz_no_pickle',sha256=hashlib.sha256(raw).hexdigest(),payload=base64.b64encode(raw).decode())
def save(name,obj): (R/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def build(package,sources=None):
 sys.path.insert(0,str(package/'02_code'));from flymodel import Model
 m=Model(package/'01_model/model.yaml');assert m.sha256==BASE_SHA
 if sources:
  import pyarrow.feather as feather
  ap=sources/'body-annotations-male-cns-v1.0-minconf-0.5.feather';wp=sources/'connectome-weights-male-cns-v1.0-minconf-0.5-significant-only.feather';npth=sources/'body-neurotransmitters-male-cns-v1.0.feather'
  ann=feather.read_table(ap).to_pylist();selected=sorted([a for a in ann if (a['type'] in TYPES or re.fullmatch(r'DNg12_[a-h]',a['type'] or '')) and str(a['bodyId']) not in m.lookup],key=lambda a:a['bodyId'])
  ntrows=feather.read_table(npth,columns=['body','consensus_nt','predicted_nt','predicted_nt_confidence']).to_pylist();wanted={a['bodyId'] for a in selected};nt={x['body']:x for x in ntrows if x['body'] in wanted}
  neurons=[];prior=[];rows=[];signs=[]
  for a in selected:
   t=a['type'];kind='PFL3' if t in {'EPG','EPGt','Delta7'} else 'DNb08' if t in {'DNb05','DNb06'} else 'IN17A001' if t in {'IN17A001','INXXX466','IN19B012'} else 'DNg13' if t.startswith('DNg') else None
   # Inhibitory VNC template is selected by explicit NT/class identity, not a sorted unique-row number.
   cand=[i for i,n in enumerate(m.neurons) if (n.get('type')==kind if kind else n.get('superclass')=='vnc_intrinsic' and n.get('predictedNt')=='glutamate')]
   if not cand:raise ValueError(('Missing semantic prior',t,kind))
   ref=min(cand,key=lambda i:int(m.ids[i]));q={k:a.get(k) for k in m.neurons[0] if k in a};q.update(bodyId=str(a['bodyId']),predictedNt=nt[a['bodyId']]['consensus_nt'] or nt[a['bodyId']]['predicted_nt'],nt_confidence=nt[a['bodyId']]['predicted_nt_confidence'],connectome_namespace='MaleCNS_v1.0')
   neurons.append(q);rows.append(m.cells[ref].copy());signs.append({'acetylcholine':1,'gaba':-1,'glutamate':-1}.get(q['predictedNt'],0))
   prior.append(dict(bodyId=q['bodyId'],type=t,template_bodyId=m.ids[ref],template_type=m.neurons[ref]['type'],origin='borrowed_manual_model_prior_not_measured',sign_status='receptor_assumption_test_with_sign_zero' if q['predictedNt']=='glutamate' else 'NT_prediction_not_receptor_measurement'))
  ids=m.ids+[x['bodyId'] for x in neurons];lookup={int(b):i for i,b in enumerate(ids)}
  tab=feather.read_table(wp,columns=['body_pre','body_post','weight']);a=tab['body_pre'].to_numpy();b=tab['body_post'].to_numpy();w=tab['weight'].to_numpy();allids=np.array(list(lookup),dtype=np.int64);newids=np.array([int(x['bodyId']) for x in neurons])
  keep=np.isin(a,allids)&np.isin(b,allids)&(np.isin(a,newids)|np.isin(b,newids));aa=a[keep];bb=b[keep]
  delta=dict(pre=np.array([lookup[int(v)] for v in aa],dtype=np.int32),post=np.array([lookup[int(v)] for v in bb],dtype=np.int32),synapse_count=w[keep],cells=np.array(rows),sign=np.array(signs,dtype=m.edges['transmitter_sign'].dtype))
  np.savez_compressed(R/'extension_delta.npz',**delta);save('new_neurons.json',neurons);save('parameter_priors.json',prior)
  core=[{k:a[k] for k in ['bodyId','type','mancBodyid','somaSide','somaNeuromere']}|{'present_in_original':str(a['bodyId']) in m.lookup} for a in ann if a['type'] in {'IN17A001','INXXX466','IN16B036','IN19A007','IN19B012'}];save('paper_core_crosswalk.json',core)
  save('source_manifest.json',{'base_model_sha256':BASE_SHA,'sources':[{'name':p.name,'bytes':p.stat().st_size,'sha256':digest(p),'url':'https://storage.googleapis.com/flyem-male-cns/v1.0/connectome-data/flat-connectome/'+p.name} for p in [ap,wp,npth]],'delta_sha256':digest(R/'extension_delta.npz'),'absence_scope':'significant-only minconf0.5; absence is not biological absence'})
 else:
  neurons=json.loads((R/'new_neurons.json').read_text());delta=dict(np.load(R/'extension_delta.npz',allow_pickle=False));assert digest(R/'extension_delta.npz')==json.loads((R/'source_manifest.json').read_text())['delta_sha256']
 oldn=len(m.ids);c=m.config;c['neural']['neurons']+=neurons;c['neural']['cell_parameters']=encode(values=np.r_[m.cells,delta['cells']]);edges={k:np.concatenate([v,delta['sign'] if k=='transmitter_sign' else delta[k]]) for k,v in m.edges.items()};c['neural']['connectivity']=encode(**edges)
 # Added coordinates are schematic display coordinates ONLY. They never enter neural integration.
 positions=m.layout['positions'];newpos=[]
 for j,n in enumerate(neurons):
  same=[i for i,x in enumerate(m.neurons[:oldn]) if x.get('superclass')==n.get('superclass')];center=positions[same].mean(axis=0) if same else positions.mean(axis=0);theta=2*np.pi*j/max(1,len(neurons));newpos.append(center+np.array([.08*np.cos(theta),.08*np.sin(theta),.02]))
 layout={**m.layout,'positions':np.r_[positions,np.array(newpos)]};c['render']['neural_layout']=encode(**layout)
 c['parameter_provenance']['extension']={'status':'candidate_not_validated_replacement','base_sha256':BASE_SHA,'priors_file':'parameter_priors.json','new_glutamate_sign':'inhibitory assumption inherited for comparability; zero-sign sensitivity required','layout':'schematic only; no EM morphology or angular compass inferred','unchanged':'all original cells, parameters, connections, protocols and muscle mapping'}
 cache=R/'cache';cache.mkdir(exist_ok=True);out=cache/'extended_model.yaml'
 with out.open('w') as f:yaml.dump(c,f,Dumper=yaml.CSafeDumper,sort_keys=False,allow_unicode=True)
 ext=Model(out);assert np.array_equal(ext.cells[:oldn],m.cells);assert np.array_equal(ext.layout['positions'][:oldn],positions)
 for k,v in m.edges.items(): assert np.array_equal(ext.edges[k][:len(v)],v)
 assert ext.mapping==m.mapping and len(set(ext.ids))==len(ext.ids)
 save('build_report.json',dict(base_sha256=BASE_SHA,extended_sha256=digest(out),original_cells=oldn,added_cells=len(neurons),added_types=dict(collections.Counter(x['type'] for x in neurons)),original_stored_edges=len(m.edges['pre']),added_stored_edges=len(delta['pre']),extended_effective_edges=len(ext.pre),original_effective_edges=len(m.pre),original_arrays_unchanged=True,render_positions=len(ext.layout['positions']),model_path='cache/extended_model.yaml',template_status='unmeasured borrowed priors',extension_status='built_not_functionally_validated'))
 print((R/'build_report.json').read_text())
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--package',type=Path,default=DEFAULT);p.add_argument('--sources',type=Path);a=p.parse_args();build(a.package,a.sources)
