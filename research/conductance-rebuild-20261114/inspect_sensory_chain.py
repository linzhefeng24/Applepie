"""Full causal traces of a new sensory mechanism hypothesis; no score/ranking."""
from pathlib import Path
import hashlib,json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).parent;O=R/'results/sensory-terminal-probes';cases=['passive','motor','motor_web','motor_chief_off','chief_LF'];fig,axs=plt.subplots(5,4,figsize=(15,12),sharex=True)
for row,c in enumerate(cases):
 z=np.load(O/'chain-r3'/(c+'.npz'));t=z['time_ms'];axs[row,0].plot(t,z['angle_deg']);axs[row,1].plot(t,z['voltage'][:,0,0],label='proximal');axs[row,1].plot(t,z['voltage'][:,0,2],label='terminal',alpha=.8);axs[row,2].plot(t,z['calcium'][:,0,2],label='hook flex');axs[row,2].plot(t,z['calcium'][:,1,2],label='hook ext');axs[row,3].plot(t,z['calcium'][:,2,2],label='claw flex');axs[row,3].plot(t,z['calcium'][:,3,2],label='claw ext');axs[row,0].set_ylabel(c)
 for a in axs[row]:a.grid(alpha=.2)
for ax,title in zip(axs[0],['Same imposed angle (deg)','Hook flex voltage (mV)','Hook terminal Ca (uM)','Claw terminal Ca (uM)']):ax.set_title(title)
for a in axs[-1]:a.set_xlabel('Time (ms)')
axs[0,1].legend();axs[0,2].legend();axs[0,3].legend();fig.suptitle('Actual simulated DNg100 / DNg74 → chief9A spikes → hypothetical sensory terminals');fig.tight_layout();fig.savefig(O/'chain-r3/full-causal-traces.png',dpi=150)
rows=[]
for c in cases:
 p=O/'chain-r3'/(c+'-diagnosis.json');d=json.load(open(p));rows.append(d)
p=O/'chain-GABA-block/motor-diagnosis.json';rows.append(json.load(open(p)))
(O/'chain-r3/causal-review.json').write_text(json.dumps({'status':'newly rerun compartmental mechanism; sensory geometry and physiology estimated; not whole-animal reconstruction','conditions':rows,'inspection_code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},indent=2)+'\n')
