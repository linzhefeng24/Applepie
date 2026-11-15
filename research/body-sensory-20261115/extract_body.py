"""Replay archived motor inputs, reading mechanics at each physics state.
Use --model-directory extracted from the pinned legacy two-file archive.
The clone used for mj_forward prevents observation from altering the replay.
"""
from pathlib import Path
import argparse,copy,hashlib,json,sys,platform
import numpy as np
import mujoco
from body_sensory import sample_mechanics,transduce,LEGS
P=Path(__file__).parent

def main():
 a=argparse.ArgumentParser();a.add_argument('--model-directory',type=Path,required=True);a.add_argument('--case',choices=['A','B'],default='A');a.add_argument('--environment',choices=['ground','no-ground','gravity-1.5'],default='ground');args=a.parse_args();sys.path.insert(0,str(args.model_directory.resolve()));from simulation import Simulation
 s=Simulation(args.model_directory/'parameters.yaml',case=args.case);m=s.model;d=s.data
 if args.environment=='no-ground':
  g=m.geom('groundplane');g.contype[:]=0;g.conaffinity[:]=0
 if args.environment=='gravity-1.5':m.opt.gravity[:]*=1.5
 z=s.load_ab(args.case);p=json.load(open(P/'parameters.json'));rows=[];times=[]
 for u in z['controls']:
  d.ctrl[:]=u
  # Observe pre-step state and its current controls, without advancing twice.
  w=copy.copy(d);mujoco.mj_forward(m,w);rows.append(sample_mechanics(m,w));times.append(float(d.time));mujoco.mj_step(m,d)
 out={k:np.asarray([x[k] for x in rows]) for k in rows[0]};out.update(transduce(out,p));out['time_s']=np.array(times);out['legs']=np.array(LEGS)
 if not all(np.isfinite(v).all() for k,v in out.items() if k!='legs'):raise RuntimeError('Nonfinite output')
 O=P/'results'/(args.case+'-'+args.environment);O.mkdir(parents=True,exist_ok=True);np.savez_compressed(O/'body-sensory.npz',**out)
 sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
 report={'status':'independently rerun archived motor input; no neural feedback to body yet','command':[sys.executable,*sys.argv],'case':args.case,'environment':args.environment,'samples':len(times),'duration_s':float(d.time),'dt_s':float(m.opt.timestep),'legs':LEGS,'mujoco':mujoco.__version__,'numpy':np.__version__,'python':platform.python_version(),'source_hashes':{str(f):sha(f) for f in [args.model_directory/'simulation.py',args.model_directory/'parameters.yaml',P/'parameters.json',P/'extract_body.py',P/'body_sensory.py']},'source_model':s.config['provenance']['model_source_sha256'],'force_conversion':'no SI inference; native forces and dimensionless bodyweights','model_total_native_weight':float(m.body_mass.sum()*np.linalg.norm(m.opt.gravity)),'max_load_bodyweights':out['load_bodyweights'].max(axis=0).tolist(),'contact_samples':(out['contact_count']>0).sum(axis=0).tolist(),'final_qpos_native':d.qpos.tolist(),'extra_applied_forces':bool(np.any(d.qfrc_applied) or np.any(d.xfrc_applied))};(O/'manifest.json').write_text(json.dumps(report,indent=2)+'\n');print(args.case,args.environment,report['max_load_bodyweights'],flush=True)
if __name__=='__main__':main()
