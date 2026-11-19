"""Explicit stimulation/ablation probes. Electrical input is not a measured natural waveform."""
from pathlib import Path
import json
R=Path(__file__).resolve().parent;G=json.loads((R/'identity_registry.json').read_text());cases={}
def add(name,groups,**kw):
 cases[name]={'sources':groups,'kind':'neural_component_probe','scope':'No behavioral, calcium-indicator or gene-expression equivalence inferred from current injection.',**kw}
add('quiet',[])
for name in ['DNg100','DNb08','P9','MDN','BPN','BRK','FG','BB','LBL40','DNg75','DNg97','DNg55','DNg16','DNg74','DNg11']:add(name,[name])
add('BPN_P9',['BPN','P9'])
for dn in ['DNg75','DNg97','DNg55','DNg16','DNg74']:add('DNg100_'+dn,['DNg100',dn])
for source in ['MDN','P9']:
 for stop in ['BRK','FG','BB']:add(source+'_'+stop,[source],modulator=stop)
for role in ['PFL3','PFL2','DNa02','DNg13']:
 for side in ['L','R']:add(role+'_'+side,[role],source_soma_side=side,scope='Soma-side stimulation; not an inferred heading cue or behavioral turn direction.')
for role in ['E1','E2','I1','I2']:add('DNg100_'+role+'_off',['DNg100'],ablate_group=role)
add('DNg100_I1I2_off',['DNg100'],ablate_groups=['I1','I2'])
for role in ['E1','E2','E4','E5']:add('DNb08_'+role+'_off',['DNb08'],ablate_group=role)
for group in ['01A','09A','10B','13A','13B','19A','19B','21A','23B','chief_9A']:add('group_'+group,[group],scope='Listed annotated population; not assumed identical to a specific split-GAL4 alpha/beta driver.')
for sensor in ['hook','claw','club']:
 add(sensor+'_probe',[sensor],source_window='probe',scope='Direct current into explicitly annotated right-hindleg afferents; not a calibrated passive motion input.')
 add(sensor+'_chief',[sensor],source_window='probe',modulator='chief_9A',scope='Same afferent current with real chief9A activation; inspect terminal voltage/current and outputs.')
for sensor in ['hook','claw']:
 add(sensor+'_DNg100',['DNg100'],additional_probe=sensor)
 add(sensor+'_DNg100_chief_off',['DNg100'],additional_probe=sensor,ablate_group='chief_9A')
for amp in [80,240,320]:add('DNg100_'+str(amp),['DNg100'],amplitude_pA=amp)
for name,ids in [('DNge129',['11006','10856']),('GNG127',['11982','516820']),('GNG458',['26344']),('top5',['11006','10856','11982','516820','26344'])]:add('DNg100_cut_'+name,['DNg100'],cut_inhibitory_sources_to_DN=ids)
add('DNg100_cut_all_I_to_DN',['DNg100'],cut_all_inhibition_to_DN=True)
add('DNg100_MN_GABA_half',['DNg100'],motor_GABA_factor=0.5,scope='Unmeasured receptor efficacy sensitivity, not a calibrated Rdl genetic knockdown.')
plan={'model_sha256':json.loads((R/'component_manifest.json').read_text())['model_sha256'],'duration_ms':1600,'drive_on_ms':200,'drive_off_ms':1500,'current_pA':160,'modulator_on_ms':600,'modulator_off_ms':1100,'probe_on_ms':400,'probe_off_ms':1200,'record_interval_ms':1,'cases':cases};(R/'panel.json').write_text(json.dumps(plan,indent=2)+'\n');print(len(cases),'conditions')
