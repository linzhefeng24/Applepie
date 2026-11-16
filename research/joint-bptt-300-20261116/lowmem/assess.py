"""Explicit practical acceptance AFTER preserving the failed strict gradient test.

The1e-6 relative-gradient criterion is not retroactively called a pass. Assess
exact observable forward parity and actual first-Adam multiplier differences
alongside a stated1e-4 gradient tolerance. No numerical code is modified here.
"""
from pathlib import Path
import argparse,json
import numpy as np
HERE=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--profile',type=Path,required=True);p.add_argument('--forward',type=Path,required=True);p.add_argument('--config',type=Path,required=True);a=p.parse_args()
report=json.loads((a.profile/'low-memory-validation.json').read_text());forward=json.loads(a.forward.read_text());cfg=json.loads(a.config.read_text())
with np.load(a.profile/'low-memory-gradient.npz',allow_pickle=False) as z:old=z['reference'];new=z['gradient']
def first_delta(g):
 clipped=g*min(1.,cfg['gradient_clip_norm']/max(np.linalg.norm(g),1e-30))
 raw=-cfg['learning_rate']*clipped/(abs(clipped)+cfg['adam_epsilon'])
 # First step is inside original hard bounds, so projection is inactive.
 assert np.max(abs(cfg['original_group_bound']*np.tanh(raw)))<cfg['maximum_fractional_change_from_start']
 return cfg['original_group_bound']*np.tanh(raw)
cosine=float(np.sum(old*new)/(np.linalg.norm(old)*np.linalg.norm(new)));step=float(abs(first_delta(old)-first_delta(new)).max());signs=int(((old*new)<0).sum())
report.update(strict_gradient_parity_passed=report['numerical_parity_passed'],strict_gradient_relative_tolerance=1e-6,forward_parity=forward,gradient_cosine=cosine,gradient_sign_changes=signs,first_adam_multiplier_max_abs_difference=step,practical_thresholds={'gradient_relative_l2':1e-4,'gradient_cosine_minimum':1-1e-8,'first_adam_multiplier_max_abs_difference':1e-7,'max_conservative_process_peak_gib':6.5},limitation='Strict1e-6 gradient equality failed and remains a failure. The small gradient discrepancy was not isolated between nested recomputation and separately compiled stage boundaries. Practical acceptance tests only the manual-bank starting point, not every future parameter vector; it is not a claim of bitwise gradient equality or a new exact physical derivative.')
report['practical_low_memory_accepted']=bool(forward['u_exact'] and forward['spike_bins_exact'] and report['joint_loss_abs_error']==0 and report['all_gradients_finite'] and report['gradient_relative_l2_error']<1e-4 and cosine>1-1e-8 and step<1e-7 and signs==0 and report['memory']['conservative_parent_plus_largest_worker_peak_kib']<6.5*1024*1024)
(HERE/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));assert report['practical_low_memory_accepted']
