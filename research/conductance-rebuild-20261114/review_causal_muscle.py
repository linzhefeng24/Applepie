"""Inventory the entire motor readout as well as the12 inspected tibial MNs.
Nonzero spikes are not a test for rhythm; no loss or automatic parameter choice.
"""
from pathlib import Path
import json,hashlib,sys
import numpy as np
R=Path(__file__).parent;B=R/'results/manual-mechanism';m=json.load(open(B/'neurons.json'));ii=np.array([i for i,x in enumerate(m) if x['class']=='motor neuron']);records=[];prefix=sys.argv[1] if len(sys.argv)>1 else 'expanded-right-extensors-third-direct-DN-weak';tag=sys.argv[2] if len(sys.argv)>2 else 'causal-motor-readout-review'
for suffix in ['', '-E1-silenced','-E2-silenced']:
 mode=prefix+suffix;path=B/(mode+'.npz');z=np.load(path);sp=z['spikes'];u=z['u'];rates=sp[400:].sum(axis=0)/1.2;selected=json.load(open(B/(mode+'-diagnosis.json')))['cells'][26:];active=ii[rates[ii]>0];records.append({'mode':mode,'raw_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'motor_neurons_total':len(ii),'motor_neurons_with_post400ms_spikes':len(active),'active_motor_neurons':[{'body_id':m[i]['bodyId'],'type':m[i]['type'],'rate_hz':float(rates[i]),'ISI_ms_min_median_max':(np.quantile(np.diff(np.repeat(np.arange(400,len(sp)),sp[400:,i])),[0,.5,1]).tolist() if sp[400:,i].sum()>1 else [])} for i in active],'inspected_tibial_cells':selected,'channels_with_nonzero_u_after400ms':int((u[400:].max(axis=0)>0).sum()),'interpretation':'Activity counts do not establish oscillation, correct antagonist phase or locomotion. Unmapped channels are zero placeholders, not measured silence.'})
(B/(tag+'.json')).write_text(json.dumps({'analysis_code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'method':__doc__,'conditions':records},indent=2)+'\n');print([(r['mode'],r['motor_neurons_with_post400ms_spikes'],r['channels_with_nonzero_u_after400ms']) for r in records])
