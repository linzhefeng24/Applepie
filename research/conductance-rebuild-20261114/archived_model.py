"""Load the SHA-verified muscle bundle from the repository, not a loose workspace copy."""
from pathlib import Path
import hashlib,importlib.util,json,sys,zipfile
ROOT=Path(__file__).parent
info=json.loads((ROOT/'data/body-model-release.json').read_text());bundle=ROOT.parent/'assets/flymimic-legacy-AB-twofile.zip'
if hashlib.sha256(bundle.read_bytes()).hexdigest()!=info['sha256']:raise ValueError('Archived body bundle checksum mismatch')
cache=ROOT/'.cache/archived-body';cache.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(bundle) as z:
 if set(z.namelist())!={'parameters.yaml','simulation.py'}:raise ValueError('Unexpected files in the archived body bundle')
 for name in z.namelist():
  payload=z.read(name);dest=cache/name
  if not dest.exists() or hashlib.sha256(dest.read_bytes()).digest()!=hashlib.sha256(payload).digest():dest.write_bytes(payload)
spec=importlib.util.spec_from_file_location('_verified_archived_AB_runtime',cache/'simulation.py');module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module);Simulation=module.Simulation
