"""Inject a storage/execution adapter into the unchanged validated optimizer."""
from pathlib import Path
import argparse,hashlib,json,os,sys
p=argparse.ArgumentParser();p.add_argument('--work',type=Path,required=True);p.add_argument('--updates',type=int,required=True);a=p.parse_args();r=a.work.resolve();root=r.parents[1]
manifest=json.loads((Path(__file__).resolve().parents[1]/'PACKAGE_MANIFEST.json').read_text())
path=r/'train_chunk.py';text=path.read_text();assert hashlib.sha256(path.read_bytes()).hexdigest()==manifest['offline_compatibility_patch']['bundled_sha256']
old='value_grad=jax.jit(jax.value_and_grad(ctx.loss,has_aux=True));value_only=jax.jit(ctx.loss)'
new='from engine import Engine; engine=Engine(ctx); value_grad=engine.value_grad; value_only=engine.value_only'
assert text.count(old)==1;text=text.replace(old,new)
sys.path.insert(0,str(r));sys.argv=[str(path),'--updates',str(a.updates)]
os.environ['SYNC_EVERY_SAVE']='0';os.environ['TRAIN_SOURCE_REF']=manifest['training_source_revision']
exec(compile(text,str(path),'exec'),{'__name__':'__main__','__file__':str(path)})
