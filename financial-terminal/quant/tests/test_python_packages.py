import json,os,subprocess,tempfile,unittest
from pathlib import Path
HELPER=Path(__file__).resolve().parents[2]/'scripts/python-packages.sh'
class PythonPackageSourceTests(unittest.TestCase):
 def test_private_index_config_ignored_without_mutating_parent(self):
  with tempfile.TemporaryDirectory() as tmp:
   fake=Path(tmp)/'fake-python'
   fake.write_text("#!/usr/bin/env python3\nimport os,json,sys\nprint(json.dumps({'args':sys.argv[1:],'config':os.environ.get('PIP_CONFIG_FILE'),'index':os.environ.get('PIP_INDEX_URL'),'extra':os.environ.get('PIP_EXTRA_INDEX_URL'),'trusted':os.environ.get('PIP_TRUSTED_HOST'),'target':os.environ.get('PIP_TARGET'),'hashes':os.environ.get('PIP_REQUIRE_HASHES'),'cert':os.environ.get('PIP_CERT'),'proxy':os.environ.get('HTTPS_PROXY')}))\n")
   fake.chmod(0o755)
   script='source "$1"; aperture_pip_install "$2" uv==0.9.27; printf "parent-index=%s\\n" "$PIP_INDEX_URL"'
   env={**os.environ,'PIP_INDEX_URL':'http://private.invalid/simple','PIP_EXTRA_INDEX_URL':'http://extra.invalid/simple','PIP_TRUSTED_HOST':'pypi.org','PIP_TARGET':'/unwanted-target','PIP_CONFIG_FILE':'/unwanted-config','PIP_REQUIRE_HASHES':'1','PIP_CERT':'/test/ca.pem','HTTPS_PROXY':'http://proxy.test:8080','APERTURE_PYPI_INDEX_URL':'https://pypi.org/simple'}
   result=subprocess.run(['bash','-c',script,'test',str(HELPER),str(fake)],capture_output=True,text=True,env=env)
   self.assertEqual(result.returncode,0,result.stderr)
   data=json.loads(next(line for line in result.stdout.splitlines() if line.startswith('{')))
   self.assertEqual(data['config'],'/dev/null');self.assertIsNone(data['index']);self.assertIsNone(data['extra']);self.assertIsNone(data['trusted']);self.assertIsNone(data['target']);self.assertEqual(data['hashes'],'1');self.assertEqual(data['cert'],'/test/ca.pem');self.assertEqual(data['proxy'],'http://proxy.test:8080')
   self.assertIn('https://pypi.org/simple',data['args']);self.assertIn('--only-binary=:all:',data['args']);self.assertIn('parent-index=http://private.invalid/simple',result.stdout)
 def test_http_index_rejected(self):
  result=subprocess.run(['bash','-c','source "$1"; aperture_pip_install /must-not-run uv','test',str(HELPER)],capture_output=True,text=True,env={**os.environ,'APERTURE_PYPI_INDEX_URL':'http://private.invalid/simple'})
  self.assertNotEqual(result.returncode,0);self.assertIn('HTTPS',result.stdout);self.assertNotIn('No such file',result.stderr)
if __name__=='__main__':unittest.main()
