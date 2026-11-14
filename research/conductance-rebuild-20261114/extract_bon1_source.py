"""Read published per-brain source data; preserve original amplitudes.
43 samples at 6Hz, -2..5s relative onset, verified against ED Fig5e axes.
No invented temporal interpolation in the stored experimental data.
"""
from pathlib import Path
import csv,json,hashlib
import numpy as np,openpyxl
R=Path(__file__).parent;O=R/'data/experimental-source';p=O/'brk-MOESM26.xlsx';w=openpyxl.load_workbook(p,read_only=True,data_only=True)
a=[r for r in w['Extended Data Figure 5e'].values if any(v is not None for v in r)][2:];control=np.array([r[1:6] for r in a],float);brk=np.array([r[7:13] for r in a],float);assert brk.shape==(43,6) and control.shape==(43,5);t=np.arange(43)/6-2
with (O/'BON1-ED5e.csv').open('w',newline='') as f:
 q=csv.writer(f);q.writerow(['time_relative_stimulus_s']+[f'control_brain{i+1}' for i in range(5)]+[f'BRK_brain{i+1}' for i in range(6)]);q.writerows(np.c_[t,control,brk])
meta={'source':'https://doi.org/10.1038/s41586-024-07854-7','sheet':'Extended Data Figure 5e','sampling_hz':6,'time_axis':'43 samples, -2 to5s; onset0, pulse end2s; aligned to published figure axes and6Hz methods','source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'train_brains_1based':[1,2,3,4],'holdout_brains_1based':[5,6],'readout':'GCaMP6s soma dF/F, not Hz','amplitude_policy':'retain source units; gain is indicator nuisance parameter, not inferred spike rate','source_fig5f_AUC':'per-brain0..2s values preserved in XLSX, separate from fluorescence trace fitting','large_source_file':'MOESM18 retained outside git cache; not used for BON1 fitting; original URL/hash remain in download manifest'};(O/'BON1-extraction.json').write_text(json.dumps(meta,indent=2));print(brk.shape,'peak',brk.mean(axis=1).max())
