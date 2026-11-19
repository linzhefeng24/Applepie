"""CNS input to peripheral afferents targets their axon-terminal compartment.
This is an explicit reduced-compartment assumption, not recovered EM morphology.
All non-afferent equations and all original parameter values are preserved.
"""
from pathlib import Path
import json,hashlib,sys,yaml,numpy as np
R=Path(__file__).resolve().parent;ROOT=R.parents[1];P=ROOT/'research/manual-full-rerun-20261119/cache/extracted/Manual_FreeBody';sys.path.insert(0,str(P/'02_code'));from flymodel import Model
m=Model(R/'cache/expanded_model.yaml');pns=[n['bodyId'] for n in m.neurons if n.get('class')=='mechanosensory_proprioceptive' and n.get('entryNerve') in {'ProLN','ProCN','MesoLN','MetaLN','PrN','VProN'} and n.get('subclass') in {'chordotonal organ','leg','hair plate','campaniform sensilla'}]
m.config['neural']['synaptic_target_compartment']={'axon_terminal_body_ids':pns,'otherwise':'soma','evidence':'Peripheral proprioceptive sensory somata are outside CNS; incoming central synapses are onto their axons. Dallmann2025 doi10.1038/s41586-025-09554-2 supports hook presynaptic inhibition.','assumptions':'Two compartments stand for peripheral transduction membrane and terminal spike/voltage compartment, not full morphology; reversal potentials and channel priors inherited, unmeasured for these cells. No calibrated mechanical tuning or release-probability law inferred.'}
with (R/'cache/component_model.yaml').open('w') as f:yaml.dump(m.config,f,Dumper=yaml.CSafeDumper,sort_keys=False,allow_unicode=True)
s=(ROOT/'research/core-bypass-localization-20261119/instrumented_dynamics.py').read_text();s=s.replace('    aux,\n):','    aux,\n    terminal_targets,\n):')
needle='            den = A * B - gc * gc\n';assert s.count(needle)==1
s=s.replace(needle,'''            if terminal_targets[j]:
                # Incoming CNS synapses on peripheral afferents are axonal.
                # The injected sensory current still enters the peripheral compartment.
                A = Cs / dt + gLs + gc + gNaP
                B = Ca / dt + gLa + gc + gNa + gK + gCa + gSK + excit + inhib
                rhs1 = Cs / dt * vs[j] + gLs * EL + gNaP * ena + inj
                rhs2 = (Ca / dt * v + gLa * aux[0] + gNa * ena
                        + (gK + gSK) * ek + gCa * eca + cell[j, 10]
                        + excit * ee + inhib * ei)
'''+needle)
s=s.replace('gej * (ee - vs[j])','gej * (ee - (va[j] if terminal_targets[j] else vs[j]))').replace('gij * (ei - vs[j])','gij * (ei - (va[j] if terminal_targets[j] else vs[j]))').replace('finalg[j, 0] * (ee - vs[j])','finalg[j, 0] * (ee - (va[j] if terminal_targets[j] else vs[j]))').replace('finalg[j, 1] * (ei - vs[j])','finalg[j, 1] * (ei - (va[j] if terminal_targets[j] else vs[j]))')
(R/'terminal_dynamics.py').write_text(s);report={'model_sha256':hashlib.sha256((R/'cache/component_model.yaml').read_bytes()).hexdigest(),'neurons':len(m.ids),'afferents_with_axon_terminal_inputs':len(pns),'source_kernel_sha256':hashlib.sha256((ROOT/'research/core-bypass-localization-20261119/instrumented_dynamics.py').read_bytes()).hexdigest(),'runtime_kernel_sha256':hashlib.sha256(s.encode()).hexdigest(),'legacy_compatibility_required':'With terminal_targets allFalse, spikes andu must match prior selected model bitwise.','new_model_validation':'Must be independently rerun; no old pass inherited.'};(R/'component_manifest.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
