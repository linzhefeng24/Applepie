from pathlib import Path
import sys,json,time
import numpy as np
from model import simulate
from network import load
from metrics import summarize
R=Path(__file__).parent;p=json.load(open(R/'configs/core-selected.json'));scope=sys.argv[1] if len(sys.argv)>1 else 'motor';duration=float(sys.argv[2]) if len(sys.argv)>2 else 1800.;p['duration_ms']=duration
W,roles,metadata=load(scope);print('Start',scope,len(W),'edges',np.count_nonzero(W),flush=True);t=time.time();r=simulate(W,roles,p);s=summarize(r);print('Finished',round(time.time()-t,2),'seconds; rhythmic MN',s['rhythmic_MN'],'active MN',sum(c['mean_spikes_per_s']>0 and role=='MN' for c,role in zip(s['cells'],roles)),flush=True)
(R/'results'/f'{scope}-baseline.json').write_text(json.dumps({'scope':scope,'neurons':len(W),'summary':s,'config':p,'metadata':metadata},indent=2));np.savez_compressed(R/'results'/f'{scope}-baseline.npz',spikes=r['spike_counts_1ms'],voltage=r['voltage_first12'],body_ids=[int(x['bodyId']) for x in metadata]);print([(roles[j],s['cells'][j]['burst_frequency_hz']) for j in range(5)],flush=True)
