"""Remove unused allocated recording tail; no integration values changed."""
from pathlib import Path
import json,hashlib,sys
import numpy as np
R=Path(__file__).resolve().parent;P=R.parents[1]/'research/manual-full-rerun-20261119/cache/extracted/Manual_FreeBody';sys.path.insert(0,str(P/'02_code'));from flymodel import Model
m=Model(P/'01_model/model.yaml');s=m.config['neural']['solver'];duration=m.config['experiments']['DN_drive']['duration_ms'];steps=round(duration/s['dt_ms']);stride=round(s['record_interval_ms']/s['dt_ms']);valid=(steps+stride-1)//stride;audit=[]
for p in sorted((R/'cache').glob('*.npz')):
 old=hashlib.sha256(p.read_bytes()).hexdigest()
 with np.load(p) as z:d={k:z[k] for k in z.files}
 if 'record_time_ms' in d:continue
 assert d['voltage'].shape[0]==valid+1
 assert not d['voltage'][-1].any() and not d['currents_pA'][-1].any()
 np.savez_compressed(p,spikes=d['spikes'],voltage=d['voltage'][:valid],currents_pA=d['currents_pA'][:valid],record_indices=d['record_indices'],record_time_ms=np.arange(valid)*stride*s['dt_ms']+s['dt_ms'])
 new=hashlib.sha256(p.read_bytes()).hexdigest();j=R/(p.stem+'.json');r=json.loads(j.read_text());r['output_npz'].update(sha256=new,bytes=p.stat().st_size);r['raw_trace_alignment']='unused zero tail removed, explicit160point time axis added; no neuronal state changed';j.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');audit.append({'case':p.stem,'before_sha256':old,'after_sha256':new,'actual_record_points':valid})
(R/'trace-alignment.json').write_text(json.dumps({'operation':'remove unused allocation only; no simulation rerun or numerical-state alteration','cases':audit},indent=2)+'\n')
