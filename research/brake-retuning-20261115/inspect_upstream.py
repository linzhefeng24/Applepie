"""Compare early/late real presynaptic event loads, not inferred causal currents."""
from pathlib import Path
import json,hashlib,numpy as np
from scipy import sparse
R=Path(__file__).parent;N=R.parent/'conductance-rebuild-20261114';B=N/'results/mcns-brake-extension';source=N/'results/frozen-neural-panel-brake-extension-r9/BRK.npz';m=json.load(open(B/'neurons.json'));w=sparse.load_npz(B/'signed-hypothesis-connectivity.npz').tocsc();z=np.load(source);cp=z['cell_parameters'];early=z['spikes'][200:450].sum(0)/.25;late=z['spikes'][1000:1450].sum(0)/.45;rows=[]
for typ in ['IN07B001','IN18B011','IN21A017']:
 for j,x in enumerate(m):
  if x['type']!=typ:continue
  c=w[:,j].tocoo();e=[]
  for i,v in zip(c.row,c.data):
   if v<=0:continue
   gain=cp[i,12]*cp[j,5];e.append({'pre':m[i]['bodyId'],'pre_type':m[i]['type'],'structural_count':float(v),'source_gain':float(cp[i,12]),'early_Hz':float(early[i]),'late_Hz':float(late[i]),'weighted_event_change':float(v*gain*(late[i]-early[i]))})
  e.sort(key=lambda x:x['weighted_event_change']);rows.append({'target':x['bodyId'],'type':typ,'direct_BRK_inputs':[x for x in e if x['pre_type']=='AN19A018'],'declining_excitatory_sources':e[:12]})
O=R/'results';O.mkdir(exist_ok=True);(O/'upstream-review.json').write_text(json.dumps({'input_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'scope':'actual old extended BRK run; all rows descriptive event loads, not causal current attribution','interpretation':'Direct BRK drive persists; early excitation from IN17A001/IN19A014/IN03A001 and other relays decays. BRK shared source_gain0.5 was inherited from brain tuning; test terminal-specific efficacy without raising every brain/VNC output.','targets':rows},indent=2)+'\n')
