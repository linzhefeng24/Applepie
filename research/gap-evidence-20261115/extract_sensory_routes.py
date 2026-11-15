"""Same-animal MaleCNS v1.0 anatomical paths; no functional ID fabrication.

Only annotations explicitly marked leg entry nerves are selected. Chordotonal
subtype annotations do NOT establish hook/claw/club tuning. Campaniform cells
are NOT assigned a force direction or strain transfer function from their name.
Paths are structural, not proof of physiological transmission or recruitment.
"""
from pathlib import Path
import csv,json,hashlib,collections,platform,gzip
import pyarrow as pa,pyarrow.feather as ft,pyarrow.compute as pc
R=Path(__file__).parent;B=Path('/workspace/exports/malecns-source');O=R/'routes';O.mkdir(exist_ok=True);ann=B/'body-annotations-male-cns-v1.0-minconf-0.5.feather';raw=B/'connectome-weights-male-cns-v1.0-minconf-0.5-significant-only.feather';meta={x['bodyId']:x for x in ft.read_table(ann).to_pylist()};nerves={'ProLN','ProCN','MesoLN','MetaLN'};sens={b:x for b,x in meta.items() if x['superclass']=='vnc_sensory' and x['entryNerve'] in nerves and x['subclass'] in ['chordotonal organ','campaniform sensilla']};mn={b:x for b,x in meta.items() if x['superclass']=='vnc_motor' and x['subclass'] in ['fl','ml','hl']};brk={b:x for b,x in meta.items() if x['type']=='AN19A018' and x['mancBodyid'] in [10788.,10564.,10528.,10449.,10282.,10351.]};w=ft.read_table(raw,columns=['body_pre','body_post','weight'],memory_map=True)
def ids(s):return pa.array(sorted(s),type=pa.int64())
def write(name,rows):
 rows=list(rows)
 if not rows:return
 opener=gzip.open(O/(name+'.gz'),'wt',newline='') if 'twohop' in name else (O/name).open('w',newline='')
 with opener as f:
  wr=csv.DictWriter(f,fieldnames=list(rows[0]));wr.writeheader();wr.writerows(rows)
def annotation(b):
 x=meta[b];return {k:x[k] for k in ['bodyId','type','superclass','subclass','somaNeuromere','somaSide','rootSide','entryNerve','mancBodyid','mancType','vfbId']}
write('sensory-identities.csv',[annotation(b) for b in sorted(sens)]);write('leg-MN-identities.csv',[annotation(b) for b in sorted(mn)]);write('BRK-identities.csv',[annotation(b) for b in sorted(brk)])
all_out=w.filter(pc.is_in(w['body_pre'],value_set=ids(set(sens)|set(brk))));motor_in=w.filter(pc.is_in(w['body_post'],value_set=ids(mn)));rows=all_out.to_pylist();incoming=motor_in.to_pylist();mid_out=collections.defaultdict(list)
for x in incoming:mid_out[x['body_pre']].append(x)
summary=[];all_relays=set()
for kind,sources in [('leg_campaniform',{b for b in sens if sens[b]['subclass']=='campaniform sensilla'}),('leg_chordotonal',{b for b in sens if sens[b]['subclass']=='chordotonal organ'}),('BRK',set(brk))]:
 direct=[];paths=[];relay_edges={};relays=set();reached=set();active_sources=set()
 for x in rows:
  a,b,c=x['body_pre'],x['body_post'],x['weight']
  if a not in sources:continue
  if b in mn:direct.append({'pre':a,'post':b,'count':c,'pre_type':meta[a]['type'],'post_type':meta[b]['type']});reached.add(b);active_sources.add(a)
  if b in meta and meta[b]['superclass']=='vnc_intrinsic':
   for y in mid_out[b]:
    target=y['body_post'];paths.append({'sensory_or_BRK':a,'relay':b,'MN':target,'first_count':c,'second_count':y['weight'],'relay_type':meta[b]['type'],'MN_type':meta[target]['type']});relays.add(b);reached.add(target);active_sources.add(a);relay_edges[(a,b)]=c;relay_edges[(b,target)]=y['weight']
 all_relays.update(relays);write(kind+'-direct-MN.csv',direct);write(kind+'-twohop-MN.csv',paths);summary.append({'source_class':kind,'annotated_sources':len(sources),'sources_reaching_MN_within2edges':len(active_sources),'direct_edges_to_MN':len(direct),'two_edge_paths_via_vnc_intrinsic':len(paths),'intermediate_neurons':len(relays),'leg_MNs_reached':len(reached)})
write('relay-identities.csv',[annotation(b) for b in sorted(all_relays)])
U=R.parent/'conductance-rebuild-20261114/results/mcns-unified/neurons.json';u=json.load(open(U));ub={int(x['bodyId']) for x in u};coverage={'full_annotation_leg_MN_count':len(mn),'leg_MNs_in_current3474graph':len(ub&set(mn)),'annotated_sensory_in_current_graph':len(ub&set(sens)),'BRK_present':len(ub&set(brk)),'note':'graph inclusion alone does not provide sensory transduction or body feedback'}
for item in summary:
 kind=item['source_class'];direct=list(csv.DictReader(open(O/(kind+'-direct-MN.csv'))));paths=list(csv.DictReader(gzip.open(O/(kind+'-twohop-MN.csv.gz'),'rt')));item['direct_edges_retained_in3474graph']=sum(int(x['pre']) in ub and int(x['post']) in ub for x in direct);item['twohop_paths_retained_in3474graph']=sum(all(int(x[k]) in ub for k in ['sensory_or_BRK','relay','MN']) for x in paths)
source_manifest={'namespace':'MaleCNS_v1.0','query':'explicit vnc_sensory, leg entry nerve; no hook/claw subclass inference; positive significant structural synapse counts only','source_hashes':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ann,raw,U,Path(__file__)]},'source_archive':'../conductance-rebuild-20261114/data/public-input-release-verified.json','python':platform.python_version(),'pyarrow':pa.__version__,'summary':summary,'current_model_coverage':coverage,'count_caution':'traced significant-edge subset; not all biological receptors; shortest paths restricted to0/1 intrinsic relay; no rates inferred'};(O/'manifest.json').write_text(json.dumps(source_manifest,indent=2)+'\n');print(summary,coverage)
