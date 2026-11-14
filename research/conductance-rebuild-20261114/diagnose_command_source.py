"""Inspect source-cell operating states without network or endpoint fitting."""
from pathlib import Path
import json,numpy as np
from model import simulate
R=Path(__file__).parent;O=R/'results/mcns-command';p=json.load(open(O/'P9-config.json'))['parameters'];p['group_parameters']={};rows=[]
for dose in [80.,120.,160.,200.,240.,320.]:
 r=simulate(np.zeros((1,1)),['other'],p,drive=np.array([dose]),cell_overrides={0:{'axon_bias_pA':5.}});n=r['valid_record_count'];v=r['voltage_first12'][:n];sel=r['record_time_ms']>=400;rate=float(r['spike_counts_1ms'][400:].sum());rows.append({'current_pA':dose,'rate_hz':rate,'soma_range_mV':[float(v[sel,0,0].min()),float(v[sel,0,0].max())],'axon_range_mV':[float(v[sel,0,1].min()),float(v[sel,0,1].max())]});np.savez_compressed(O/f'isolated-source-{dose:g}.npz',voltage=v,time_ms=r['record_time_ms'],spikes=r['spike_counts_1ms']);(O/'isolated-source-states.json').write_text(json.dumps(rows,indent=2));print(rows[-1],flush=True)
