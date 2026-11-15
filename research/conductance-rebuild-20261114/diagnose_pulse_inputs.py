"""Compare real input event loads for manual interpretation, not optimization.
Rate x count x effective release approximates mean conductance away from pulse
boundaries; it is not causal attribution or a measured physiological weight.
"""
from pathlib import Path
import json,sys
import numpy as np
from scipy import sparse
R=Path(__file__).parent;O=R/'results/frozen-neural-panel-r4';base,case=sys.argv[1:3];cfg=json.load(open(O/(case+'-config.json')));B=R/cfg['graph_directory'] if 'graph_directory' in cfg else R/'results/mcns-command-v2';m=json.load(open(B/'neurons.json'));W=sparse.load_npz(B/'signed-hypothesis-connectivity.npz').tocsc();a=np.load(O/(base+'.npz'));b=np.load(O/(case+'.npz'));ra=a['spikes'][500:950].sum(axis=0)/.45;rb=b['spikes'][500:950].sum(axis=0)/.45;rows=[]
for j,x in enumerate(m):
 if x['type'] not in ['DNg100','DNg97','DNa02','IN27X001']:continue
 c=W[:,j].tocoo();sources=[]
 for i,w in zip(c.row,c.data):
  gain=b['cell_parameters'][i,12]*(b['cell_parameters'][j,5] if w>0 else b['cell_parameters'][i,6]);v=float(w*gain*(rb[i]-ra[i]));sources.append({'source_body':m[i]['bodyId'],'source_type':m[i]['type'],'nt':m[i]['predictedNt'],'signed_count':float(w),'baseline_hz':float(ra[i]),'pulse_hz':float(rb[i]),'signed_event_load_change':v})
 sources.sort(key=lambda x:abs(x['signed_event_load_change']),reverse=True);rows.append({'target_body':x['bodyId'],'target_type':x['type'],'side':x['somaSide'],'largest_changes':sources[:15]})
out={'baseline':base,'case':case,'window_ms':[500,950],'warning':__doc__,'targets':rows};(O/(case+'-input-change.json')).write_text(json.dumps(out,indent=2));print([(x['target_type'],x['side'],[(z['source_type'],round(z['signed_event_load_change'])) for z in x['largest_changes'][:5]]) for x in rows])
