"""Evidence and test inventory. A literature entry is NEVER an automatic pass."""
from pathlib import Path
import json,hashlib
R=Path(__file__).parent;b=json.load(open(R/'data/brain-before-rebuild.json'));claims=[]
for k,s in enumerate(b['key_structures']):
 for j,c in enumerate(s.get('confirmed',[])):
  claims.append({'id':f"structure:{s['id']}:{j}",'neurons':s['id'],'claim':c,'source_pointer':f'/key_structures/{k}/confirmed/{j}','status':'not_tested','policy':'Match stimulus, cell identity, dataset, assay and measured variable before fitting; no guessed Hz from calcium.'})
for k,e in enumerate(b['vnc_walking_evidence']['records']):
 claims.append({'id':'vnc:'+e['id'],'neurons':e.get('linked_structures',[]),'claim':e,'source_pointer':f'/vnc_walking_evidence/records/{k}','status':'not_tested','policy':'Do not substitute evoked calcium, anatomical sign or a surrogate MN rate for measured walking behavior.'})
# These were explicitly supplied from THIS chat. Source-reading scope is retained,
# and old pasted results are not represented as new simulations.
extra=[
 ('PFL3_steering','PFL3→DNa03 and via LAL010→DNa02 provide ipsilateral excitation; contralateral inhibitory branch is structural support, not proven direct mutual inhibition.','mixed_experiment_structure','whole_brain_and_turning'),
 ('DNa02_push_pull','Paired DNa02 responses can be push-pull; this does not establish direct mutual inhibitory synapses.','experiment','bilateral_recording'),
 ('PFL2_gain','PFL2 bilateral input can modulate steering gain separately from directional difference signals.','mixed','whole_brain_and_turning'),
 ('DNa02_DNg13_phase','DNa02 shows step-phase locking; DNg13 did not show the same pattern in the cited recordings.','experiment','closed_loop_step_phase'),
 ('DNg13_phase_gate','DNg13 promotes posterior movement in stance and anterior movement in swing; mechanism unresolved.','experiment','body_and_phase_feedback'),
 ('MDN_two_branches','MDN→LBL40→LUM9 contributes tibia flexion and stance; MDN→LUL130 contributes hindleg lift and swing. LBL40↔LUL130 inhibition is a hypothesis.','mixed','T3_identity_and_body'),
 ('DNg74_9A_hook','DNg74 inhibits 9A and 9A inhibits hook, a disinhibitory motif; distinguish structural upper pathway evidence and measured hook/claw gating.','mixed','sensory_feedback'),
 ('MDN_MF14_segment','MDN evokes net excitation in MF14 T1/T2, net inhibition in T3. Net response is not the sign of every direct edge.','experiment','cross_segment_identity'),
 ('P9_population','P9 recruits a broader DN population through feedforward and recurrent circuitry.','mixed','whole_brain'),
 ('BPN_P9_combination','Unilateral BPN remains mainly straight; P9 turns ipsilaterally; coactivation increases speed and adds turning.','experiment','whole_brain_and_body'),
 ('FG_BB_BRK_direction','FG/BB did not eliminate MDN backward walking, BRK did; FG+P9 may turn in place, BB+P9 suppresses both.','experiment','stop_circuit_identity_and_body'),
 ('FG_hunger','FG calcium response to sugar is stronger under starvation.','experiment','hunger_and_sensory'),
 ('coordination_speed','Coordination varies continuously with speed; contralateral homologues approximately antiphase; same-side adjacent legs approach .5 phase at fast tripod, not universally 1/3.','experiment','six_leg_body'),
 ('split_belt','40 percent split-belt speed difference induces leg-specific adjustments, notably middle-leg stance distance.','experiment','moving_ground_and_sensory'),
 ('grooming_13AB','13A/13B inhibition phenotypes from grooming are not unconditional walking constraints.','experiment','grooming_only'),
 ('turning_abstract','Shallow-turn posterior endpoint/stance changes and sharp-turn skipped/backward steps are abstract-only candidates.','preprint_abstract','body_candidate_only'),
 ('slow_MN_rest','Adult slow flexor MNs can fire approximately30Hz at rest; intermediate/fast silent. Rin150/300/700MOhm and RMP-68/-60/-48mV are class targets; no extra junction offset.','experiment','adult_single_cell'),
 ('core_vs_intact_frequency','Increasing DNg100 input increases frequency in the full author network; the minimum core need not show the same frequency modulation.','paper_model_prediction','configuration_specific'),
 ('I1_I2_redundancy','I1/I2 partial redundancy is a model-network statement; not proof either is necessary in every reduced circuit or in vivo.','paper_model_prediction','configuration_specific'),
 ('muscle_targets','Five130-channel model-derived trajectories constrain effective MN population timing, phase and amplitude; cannot uniquely recover absolute single-MN Hz.104 channels have candidate pools and26 lack them.','historical_model_inference','mapping_and_NMJ')]
for ident,text,tier,needs in extra:claims.append({'id':'chat:'+ident,'claim':text,'evidence_tier':tier,'required_scope':needs,'provenance':'User-pasted current-chat Monday record on2026-11-14; original files absent','status':'not_tested'})
provenance={'source_brain_sha256':hashlib.sha256((R/'data/brain-before-rebuild.json').read_bytes()).hexdigest(),'new_code_is_reimplementation':True,'old_checkpoints_recovered':False,'old_added_counts_as_reported':{'behavior':14,'rhythm':19,'specific_circuit':13},'coverage_warning':'Pasted record summarizes19 rhythm and13 circuit entries but does not enumerate every original row; no missing rows are invented.'}
b['conductance_rebuild_20261114']={'provenance':provenance,'phenomena_inventory':'data/phenomena-inventory.json','configuration':'configs/intact-frozen.json','results':'results/phenomena-audit.json','claim_policy':'UNTESTED is not PASS; morphology and many channel densities remain priors; neural surrogate changes do not establish turning, walking or stopping.'}
(R/'brain.json').write_text(json.dumps(b,ensure_ascii=False,indent=2));(R/'data/phenomena-inventory.json').write_text(json.dumps({'provenance':provenance,'claims':claims},ensure_ascii=False,indent=2));print('Evidence entries',len(claims),'structures',len(b['key_structures']),'VNC records',len(b['vnc_walking_evidence']['records']))
