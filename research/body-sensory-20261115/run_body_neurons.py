"""Six-leg HH sensory prototypes driven by actual replayed mechanics.

Mechanics to current is updated from the corresponding causal body sample (ZOH,
no future interpolation). chief spikes come from a separately simulated MANC
command trial; this is an explicit paired-input experiment, not the assertion
that these neural spikes generated the A/B motor program. Load/touch fibers have
no identified EM ID and share the sensory membrane prior as an exploratory
substitute, not an adult receptor measurement.
"""
from pathlib import Path
import argparse,json,sys,hashlib,platform
import numpy as np
from body_sensory import transduce,LEGS
R=Path(__file__).parent;N=R.parent/'conductance-rebuild-20261114';sys.path.insert(0,str(N));from sensory_terminal_model import simulate

def main():
 a=argparse.ArgumentParser();a.add_argument('body_case');a.add_argument('--chief-mode',choices=['passive','motor','motor_web','motor_chief_off'],default='passive');a.add_argument('--source-tag',default='r3');args=a.parse_args();f=R/'results'/args.body_case/'body-sensory.npz';z=np.load(f);p=json.load(open(R/'parameters.json'));trans=transduce(z,p);mp=json.load(open(N/'configs/sensory-terminal-r2.json'));duration=len(z['time_s'])*(z['time_s'][1]-z['time_s'][0])*1000;mp['duration_ms']=float(duration);steps=round(duration/mp['dt_ms']);t=np.arange(steps)*mp['dt_ms']/1000;idx=np.minimum(np.searchsorted(z['time_s'],t,side='right')-1,len(z['time_s'])-1);idx=np.maximum(idx,0);source=N/'results/sensory-command-probes'/args.source_tag/(args.chief_mode+'.npz');chief=np.load(source);ids=[100513,13157,14517,165560,12443,12804];O=R/'results'/args.body_case/(args.chief_mode+'-'+args.source_tag);O.mkdir(parents=True,exist_ok=True);rows=[]
 for leg,body in zip(LEGS,ids):
  i=LEGS.index(leg);sp=chief['spikes'][:,list(map(str,chief['body_ids'])).index(str(body))][:int(np.ceil(duration))];I=trans['proprio_current_pA'][idx,i];q=z['knee_deg'][idx,i];r=simulate(sp,mp,input_current_pA=I,angle_deg=q)
  # Two additional functional load/touch fibers use zero GABA conductance.
  extra=np.zeros_like(I);extra[:,0]=trans['load_current_pA'][idx,i];extra[:,1]=trans['touch_current_pA'][idx,i];l=simulate(np.zeros_like(sp),{**mp,'chief_compound_peak_nS':0.},input_current_pA=extra,angle_deg=q)
  np.savez_compressed(O/(leg+'.npz'),**r,load_voltage=l['voltage'][:,:2],load_spikes=l['spikes'][:,:2],load_calcium=l['calcium'][:,:2],load_input_current_pA=l['input_current_pA'][:,:2])
  rows.append({'leg':leg,'chief_MANC_body_id':body,'chief_spikes':int(sp.sum()),'numerical_failure':bool(r['numerical_failure'] or l['numerical_failure']),'proprio_proximal_spikes':r['spikes'][:,:,0].sum(0).tolist(),'proprio_terminal_spikes':r['spikes'][:,:,2].sum(0).tolist(),'load_touch_terminal_spikes':l['spikes'][:,:2,2].sum(0).tolist()})
 sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();manifest={'status':'newly rerun body→sensory-HH paired-input experiment; not closed-loop motor control','body_case':args.body_case,'chief_mode':args.chief_mode,'time_mapping':'body and chief trial t=0 aligned; no periodic tiling; causal previous-sample hold for mechanics','duration_ms':float(duration),'conditions':rows,'input_hashes':{str(p):sha(p) for p in [f,source,R/'parameters.json',N/'configs/sensory-terminal-r2.json']},'code_hashes':{str(p):sha(p) for p in [Path(__file__),R/'body_sensory.py',N/'sensory_terminal_model.py',N/'model.py']},'python':platform.python_version(),'numpy':np.__version__,'command':[sys.executable,*sys.argv],'randomness':'deterministic; no random draws'};(O/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(args.body_case,args.chief_mode,rows,flush=True)
if __name__=='__main__':main()
