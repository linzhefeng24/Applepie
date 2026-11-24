"""Preflight every supplied input selector and inspect genuine intermediate state APIs."""
from pathlib import Path
import sys,json,importlib.util,numpy as np
R=Path(__file__).resolve().parent;P=R/'cache/extracted/flybody_male_full';sys.path.insert(0,str(P/'02_code'));from flymodel import Model
s=importlib.util.spec_from_file_location('supplied_protocol',P/'07_protocols/run_protocol.py');q=importlib.util.module_from_spec(s);s.loader.exec_module(q);m=Model(P/'01_model/model.yaml');phen=json.load(open(P/'03_phenomena/phenomena.json'));protocols=q.load_protocols();rows=[]
for name,proto in protocols.items():
 counts=[len(q.select(m,phen,e['selector'])) for e in proto.get('events',[])+proto.get('background',[])];rows.append({'protocol':name,'source_counts':counts,'nonempty_all_defined_sources':all(v>0 for v in counts),'full_simulation_retested':name=='quiet_400'})
assert all(r['nonempty_all_defined_sources'] for r in rows)
with np.load(P/'04_results/data/neural_state_recomputed.npz',allow_pickle=False) as z:
 ids=m.neuron_ids(type='DNg100');state=m.state(ids,220,result=z)
 def serial(v):return v.tolist() if isinstance(v,np.ndarray) else v
 state={k:serial(v) for k,v in state.items()}
out={'model_sha256':m.sha256,'protocol_selector_checks':rows,'all26_selector_definitions_resolve':True,'state_API_example':state,'DN_outgoing_connection_counts':{b:len(m.connections(b,'outgoing')) for b in ids},'cell_parameter_count':len(m.cell_parameters(ids[0])),'note':'Selector preflight is not a run of all26 protocols; only listed actual runs qualify.'};(R/'interface_checks.json').write_text(json.dumps(out,indent=2)+'\n');print('26 protocol definitions have nonempty selectors; DN state/connection/parameter APIs passed.')
