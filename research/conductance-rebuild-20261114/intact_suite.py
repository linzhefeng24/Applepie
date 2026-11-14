"""Fixed-parameter intact T1 tests; no tuning against individual test responses."""
from pathlib import Path
import json,time,sys
import numpy as np
from network import load
from model import simulate
from metrics import summarize
R=Path(__file__).parent;prefix='adult-intact' if len(sys.argv)>1 else 'intact';config_name='adult-network-selected.json' if len(sys.argv)>1 else 'downstream-selected.json';p=json.load(open(R/'configs'/config_name));p['duration_ms']=1200.;w,roles,meta=load('full');ids=[int(x['bodyId']) for x in meta];(R/f'results/{prefix}-metadata.json').write_text(json.dumps(meta,indent=2));records=[]
conditions=[('baseline',{},(),{}),('drive_120',{'drive_pA':120.},(),{}),('drive_200',{'drive_pA':200.},(),{}),('drive_240',{'drive_pA':240.},(),{})]
for label,typ in [('E1_silenced','IN17A001'),('E2_silenced','INXXX466'),('I1_silenced','IN16B036'),('I2_silenced','IN19A007')]:conditions.append((label,{},tuple(i for i,x in enumerate(meta) if x['type']==typ),{}))
for typ in ['DNg75','DNg97','DNg55','DNg16']:conditions.append((typ+'_coactivation',{},(),{typ:160.}))
conditions.extend([('DNb08_alone',{'drive_pA':0.},(),{'DNb08':160.}),('no_DN',{'drive_pA':0.},(),{})])
for label,changes,ablate,extra in conditions:
 q={**p,**changes};drive=np.array([q['drive_pA'] if r=='DN' else extra.get(x['type'],0.) for r,x in zip(roles,meta)]);t=time.time();print('Start',label,flush=True);out=simulate(w,roles,q,drive=drive,ablate=ablate);s=summarize(out)
 rec={'condition':label,'parameters':q,'ablation_body_ids':[ids[i] for i in ablate],'extra_DN_injection_pA':extra,'summary':s,'neurons':len(w),'scope':'all 4604 cells in author T1 graph; two front legs, not full six-leg VNC','runtime_s':time.time()-t};records.append(rec)
 (R/f'results/{prefix}-suite-progress.json').write_text(json.dumps(records,indent=2));np.savez_compressed(R/'results'/f'{prefix}-{label}.npz',spikes=out['spike_counts_1ms'],voltage=out['voltage_first12'],body_ids=ids)
 print('Finish',label,'rhythmic MN',s['rhythmic_MN'],'E1/E2',[(s['cells'][j]['rhythmic'],round(s['cells'][j]['burst_frequency_hz'],2)) for j in [1,2]],'seconds',round(time.time()-t,1),flush=True)
(R/f'results/{prefix}-suite.json').write_text(json.dumps(records,indent=2));(R/f'configs/{prefix}-frozen.json').write_text(json.dumps(p,indent=2))
