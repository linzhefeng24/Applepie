"""Full-scope isolated low-memory gradient, compared with archived first gradient.
This is a validation pass, not an optimizer update or a shortened training run.
"""
from pathlib import Path
import argparse,json,sys,time,resource
import numpy as np
import jax
jax.config.update('jax_enable_x64',True)
import jax.numpy as j
parser=argparse.ArgumentParser();parser.add_argument('--work',type=Path,required=True);parser.add_argument('--reference',type=Path,required=True);parser.add_argument('--out',type=Path,required=True);a=parser.parse_args();sys.path.insert(0,str(a.work.resolve()))
from training_context import JointContext
from engine import Engine
ctx=JointContext();engine=Engine(ctx);start=time.monotonic();(value,aux),gradient=engine.value_grad(ctx.reference,j.asarray(.1));gradient.block_until_ready();g=np.asarray(gradient)
with np.load(a.reference,allow_pickle=False) as z:reference=z['gradient'];target=float(z['joint_loss'])
relative=float(np.linalg.norm(g-reference)/max(np.linalg.norm(reference),1e-30));loss_error=abs(float(value)-target)
memory=json.loads((a.work/'cache/train/low-memory-last.json').read_text());memory['parent_peak_rss_kib']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss;memory['conservative_parent_plus_largest_worker_peak_kib']=memory['parent_peak_rss_kib']+max(s['peak_rss_kib'] for s in memory['stages'])
report={'physical_steps':4000,'physical_duration_s':.4,'neural_ms':1400,'cells':3988,'edges':485045,'joint_loss':float(value),'reference_joint_loss':target,'joint_loss_abs_error':loss_error,'gradient_norm':float(np.linalg.norm(g)),'gradient_relative_l2_error':relative,'all_gradients_finite':bool(np.isfinite(g).all()),'numerical_parity_passed':bool(np.isfinite(g).all() and loss_error<1e-9 and relative<1e-6),'seconds':time.monotonic()-start,'memory':memory,'optimizer_updates':0,'reference_kind':'Full original manual-anchor gradient recovered from archived first Adam moments and original unclipped gradient norm; not recomputed baseline in this job','memory_comparison':'Reports measured low-memory aggregate upper bound; no simultaneous original-memory benchmark is claimed'}
a.out.mkdir(parents=True,exist_ok=True);(a.out/'low-memory-validation.json').write_text(json.dumps(report,indent=2)+'\n');np.savez_compressed(a.out/'low-memory-gradient.npz',gradient=g,reference=reference);print(json.dumps(report,indent=2));assert report['numerical_parity_passed'],'Do not promote before full loss/gradient parity'
