"""Recompute every packaged physical trajectory without any repository inputs."""
from pathlib import Path
import importlib.util,io,json,sys,tempfile,zipfile
import numpy as np

def module(path,name):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def arrays(z,name):
 with np.load(io.BytesIO(z.read(name)),allow_pickle=False) as a:return {k:a[k] for k in a.files}

bundle=Path(sys.argv[1]);rows=[]
with zipfile.ZipFile(bundle) as z,tempfile.TemporaryDirectory(prefix='ab-offline-') as temp:
 temp=Path(temp)
 for name in ['replay_compare.py','config.json','model/simulation.py','model/parameters.yaml','inputs/neural-u.npz']:
  p=temp/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(z.read(name))
 driver=module(temp/'replay_compare.py','packaged_ab_driver');source=module(temp/'model/simulation.py','packaged_ab_source');sim=source.Simulation(temp/'model/parameters.yaml');config=json.loads((temp/'config.json').read_text());base=sim.load_ab('A')['controls'];u=arrays(z,'inputs/neural-u.npz');timing=config['timing'];t=np.arange(len(base))*sim.model.opt.timestep;idx=np.floor((timing['neural_start_ms']+t*1000*timing['neural_ms_per_body_ms'])/timing['u_bin_ms']).astype(int)
 for name in ['A','B','Epoch123','Epoch1000']:
  controls=sim.load_ab(name)['controls'] if name in ['A','B'] else base.copy()
  if name in u:controls[:,sim.muscle_indices]=u[name][idx]
  expected=arrays(z,f'outputs/NativeAB_{name}_state.npz');assert np.array_equal(controls,expected['controls_all_141'])
  result,_=driver.integrate(sim,controls);delta=float(abs(result['full_state']-expected['full_state']).max());assert delta<1e-10
  rows.append({'condition':name,'all_controls_reconstructed_exactly':True,'full_state_max_abs_difference':delta,'full_state_elementwise_exact':bool(np.array_equal(result['full_state'],expected['full_state']))})
 report={'standalone_offline_physics_rerun':True,'repository_inputs_used':False,'network_used':False,'conditions':rows}
 bundle.with_name('offline-reproduction-check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
