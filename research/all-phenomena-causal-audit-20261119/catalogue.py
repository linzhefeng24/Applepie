"""146 original claims, explicit identity coverage and test requirements.
Literature statements, anatomical support and independent simulations remain separate.
"""
from pathlib import Path
import json,hashlib,sys,os,csv
import numpy as np
R=Path(__file__).resolve().parent;ROOT=R.parents[1];P=ROOT/'research/manual-full-rerun-20261119/cache/extracted/Manual_FreeBody';sys.path.insert(0,str(P/'02_code'));from flymodel import Model
m=Model(R/'cache/component_model.yaml');old=Model(ROOT/'research/manual-extension-review-20261119/cache/selected_manual_model.yaml');src=P/'03_phenomena/phenomena.json';items=json.loads(src.read_text())['additional_literature_inventory'];assert len(items)==146
aliases={}
def group(name,types=None,prefix=None,ids=None,confidence='official_type',note='',source='MaleCNS v1.0 annotation'):
 sel=[n for n in m.neurons if (n.get('type') in (types or []) or (prefix and (n.get('type') or '').startswith(prefix)) or n['bodyId'] in (ids or []))];aliases[name]={'body_ids':[n['bodyId'] for n in sel],'original_count':sum(n['bodyId'] in old.lookup for n in sel),'expanded_count':len(sel),'identity_status':confidence,'note':note,'source':source};return aliases[name]
for typ in ['DNg100','DNb08','DNp09','MDN','DNa01','DNa02','DNa03','DNg13','DNb05','DNb06','DNg75','DNg97','DNg55','DNg16','DNg74','DNg11','PFL2','PFL3','EPG','Delta7','LAL010','LBL40']:group(typ,[typ])
group('P9',['DNp09'],source='Bidaye2020 P9=DNp09; MaleCNS exact type',note='Does not include DNp71 or pIP9/aSP9 names.');group('BPN',['CL210_a'],confidence='candidate_type_family',source='Prior source crosswalk; Bidaye2020/Sapkal2024 cell-type annotations',note='Male CL210_a candidate population, not exact female driver coverage.');group('FG',['GNG458'],source='Sapkal2024 SupplementaryTable3 CB0890→MaleCNS GNG458',note='type-level homolog');group('BB',['DNg60'],source='Sapkal2024 SupplementaryTable3');group('BRK',ids=[n['bodyId'] for n in m.neurons if n.get('type')=='AN19A018' and n.get('mancBodyid') in [10788,10564,10528,10449,10282,10351]],source='Sapkal2024 SupplementaryTable3; type-guarded MANC crosswalk');group('BON1',ids=[n['bodyId'] for n in m.neurons if n.get('type')=='IN27X001' and n.get('mancBodyid') in [10441,10348]],source='Sapkal2024 SupplementaryTable3; type-guarded MANC crosswalk')
for role,typ in [('E1','IN17A001'),('E2','INXXX466'),('I1','IN16B036'),('I2','IN19A007'),('E3','IN19B012'),('E4','IN03A006'),('E5','INXXX464'),('chief_9A','IN09A012')]:group(role,[typ],source='Pugliese2026 exact role type mapping' if role!='chief_9A' else 'Dallmann2025 author MANC code plus MaleCNS type-guarded crosswalk')
for fam in ['01A','09A','09B','10B','13A','13B','19A','19B','21A','23B']:group(fam,prefix='IN'+fam,confidence='hemilineage_population_not_identified_subtype')
for role,token in [('hook','FeCO hook'),('claw','FeCO claw'),('club','FeCO club')]:group(role,ids=[n['bodyId'] for n in m.neurons if token in (n.get('synonyms') or '') and n.get('class')=='mechanosensory_proprioceptive'],confidence='explicit_official_annotation_partial_coverage',note='Explicit cells are right hindleg only; no automatic transfer to all legs.')
group('LUL130',types=['INXXX468'],confidence='unresolved_candidate_family',note='Candidate family already present; exact experimental-driver identity not confirmed.');
for name in ['MF14','MAN','dMAN','CxHP8','DopaMeander','LUM9','13Balpha','10Balpha','9Ba_Chen2021','10Ba_Chen2021','13Bb_Chen2021','LAL_PS_ANcontra']:group(name,confidence='unresolved_exact_cell_identity',note='Missing identity cannot be repaired by arbitrary similarly named cell substitution.')
(R/'identity_registry.json').write_text(json.dumps(aliases,ensure_ascii=False,indent=2)+'\n')
rows=[]
for a in items:
 c=a['claim'];text=(c.get('fact') or c.get('observation') or c.get('activity_observation') or str(c)) if isinstance(c,dict) else str(c);tier=c.get('tier') if isinstance(c,dict) else None;source=c.get('source') if isinstance(c,dict) else None
 identity=[]
 for name,g in aliases.items():
  if name in a['id'] or name in str(a['neurons']) or (name in ['E1','E2','I1','I2','E3','E4','E5'] and name in text):identity.append(name)
 required=[]
 for words,label in [(['钙','calcium','GCaMP'],'indicator_calcium_measurement_model'),(['行走','步幅','步长','转向','turn','walking','stance','swing','kinematic','速度','后退','摆动','协调'],'body_behavior_or_limb_kinematics'),(['感觉','hook','claw','club','FeCO','CS','负载','sensory','vibrat'],'sensory_transduction_and_context'),(['饥饿','starv','sugar','reward'],'internal_state_and_modulation'),(['Rdl','MLA','picrotoxin','receptor'],'receptor_specific_mechanism'),(['HS','stride'],'ascending_readout_identity_and_voltage'),(['膜电','Hz','节律','oscillat','rhythm','spik'],'neural_dynamics'),(['突触','synap','input','connection','投射'],'anatomical_edges')]:
  if any(w.lower() in text.lower() for w in words):required.append(label)
 rows.append({'id':a['id'],'neurons':a['neurons'],'claim':c,'statement_summary':text,'literature_tier':tier,'source':source,'identity_groups':identity,'required_observables':required,'status':'pending_independent_audit','tested_components':[],'missing_structure':[],'remaining_requirements':[],'experimental_reproduction':False})
report={'schema':'all_phenomena_validation_v1','source_path':'published manual package/03_phenomena/phenomena.json','source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'original_model_sha256':old.sha256,'expanded_model_sha256':m.sha256,'count':len(rows),'count_interpretation':'Overlapping literature/model/behavior/structure records; not146 independent experiments.','items':rows};(R/'brain.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print('Catalogue',len(rows),'identity groups',len(aliases),'model neurons',len(m.ids))
