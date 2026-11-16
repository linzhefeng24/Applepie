"""Use the original offline launcher; redirect only its numerical call adapter."""
from pathlib import Path
import hashlib,json
here=Path(__file__).resolve().parent;root=here.parent;original=root/'server.py';cfg=json.loads((here/'config.json').read_text())
assert hashlib.sha256(original.read_bytes()).hexdigest()==cfg['expected_server_sha256'],'Unexpected offline launcher version'
text=original.read_text();old="command=[sys.executable,str(work/REL/'train_chunk.py'),'--updates',str(count)]";new="command=[sys.executable,str(_lowmem_here/'train_entry.py'),'--work',str(work/REL),'--updates',str(count)]";assert text.count(old)==1;text=text.replace(old,new)
text=text.replace('else:work=new_run(mode,manifest)',"else:work=new_run('lowmem-'+mode,manifest)")
exec(compile(text,str(original),'exec'),{'__name__':'__main__','__file__':str(original),'_lowmem_here':here})
