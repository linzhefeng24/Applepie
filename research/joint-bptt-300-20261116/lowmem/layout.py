"""Nested recomputation, without changing neural equations or stop-gradients.

Apply only to an instance of the immutable validated HH implementation. The
transformation changes its last scan's storage layout; equations remain in
the original file. Each ms still runs once in the continuous forward pass.
During reverse mode block interiors are recomputed, never replaced by targets.
"""
from pathlib import Path
import hashlib,inspect,json,textwrap,types
import jax
import jax.numpy as jnp
from jax import lax

def nested_scan(step,state,xs,block_size=20):
 n=len(xs)
 if n<block_size:return lax.scan(jax.checkpoint(step),state,xs)
 blocks,tail=divmod(n,block_size)
 def group(carry,values):return lax.scan(jax.checkpoint(step),carry,values)
 state,out=lax.scan(jax.checkpoint(group),state,xs[:blocks*block_size].reshape((blocks,block_size,*xs.shape[1:])))
 out=jax.tree_util.tree_map(lambda x:x.reshape((blocks*block_size,*x.shape[2:])),out)
 if tail:
  state,last=lax.scan(jax.checkpoint(step),state,xs[blocks*block_size:])
  out=jax.tree_util.tree_map(lambda x,y:jnp.concatenate((x,y)),out,last)
 return state,out

def attach(neural,model_directory):
 cfg=json.loads((Path(__file__).parent/'config.json').read_text());path=Path(model_directory)/'full_hh.py'
 assert hashlib.sha256(path.read_bytes()).hexdigest()==cfg['expected_full_hh_sha256'],'Unrecognized HH equations'
 original=type(neural).forward;source=textwrap.dedent(inspect.getsource(original))
 old='lax.scan(jax.checkpoint(ms_step),init,j.arange(T))'
 assert source.count(old)==1,'Expected exactly one storage-layout replacement'
 changed=source.replace(old,'_nested_scan(ms_step,init,j.arange(T),block_size=_memory_block_ms)')
 namespace=dict(original.__globals__);namespace.update(_nested_scan=nested_scan,_memory_block_ms=cfg['neural_checkpoint_block_ms'])
 exec(compile(changed,'<HH nested-recomputation storage layout>','exec'),namespace)
 neural.forward=types.MethodType(namespace['forward'],neural)
 return {'original_sha256':cfg['expected_full_hh_sha256'],'transformed_forward_sha256':hashlib.sha256(changed.encode()).hexdigest(),'checkpoint_block_ms':cfg['neural_checkpoint_block_ms']}
