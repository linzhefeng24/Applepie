import hashlib,importlib.util,io,json,tempfile,unittest,zipfile
from pathlib import Path
from unittest.mock import patch
spec=importlib.util.spec_from_file_location('bootstrap_uv',Path(__file__).resolve().parents[2]/'scripts/bootstrap-uv.py')
uv=importlib.util.module_from_spec(spec);spec.loader.exec_module(uv)
class NativeBootstrapTests(unittest.TestCase):
 def wheel(self):
  out=io.BytesIO()
  with zipfile.ZipFile(out,'w') as z:z.writestr('uv-0.9.27.data/scripts/uv',b'\x7fELFtest-binary')
  return out.getvalue()
 def metadata(self,checksum):
  return json.dumps({'info':{'version':uv.VERSION},'urls':[{'packagetype':'bdist_wheel','filename':'uv-manylinux_2_17_x86_64.whl','url':'https://files.pythonhosted.org/test.whl','digests':{'sha256':checksum}}]}).encode()
 def test_verified_install_cache_and_corruption_recovery_without_pip(self):
  wheel=self.wheel();meta=self.metadata(hashlib.sha256(wheel).hexdigest())
  def fetch(url,**kwargs):return io.BytesIO(meta if url.endswith('/json') else wheel)
  with tempfile.TemporaryDirectory() as tmp,patch.object(uv.platform,'machine',return_value='x86_64'),patch.object(uv.urllib.request,'urlopen',side_effect=fetch) as request:
   binary=uv.ensure_uv(tmp);self.assertEqual(binary.read_bytes(),b'\x7fELFtest-binary');self.assertEqual(request.call_count,2)
   uv.ensure_uv(tmp);self.assertEqual(request.call_count,2)
   binary.write_bytes(b'broken');uv.ensure_uv(tmp);self.assertEqual(request.call_count,4);self.assertEqual(binary.read_bytes(),b'\x7fELFtest-binary')
 def test_invalid_download_checksum_never_replaces_binary(self):
  wheel=self.wheel();meta=self.metadata('0'*64)
  with tempfile.TemporaryDirectory() as tmp,patch.object(uv.platform,'machine',return_value='x86_64'),patch.object(uv.urllib.request,'urlopen',side_effect=lambda url,**kw:io.BytesIO(meta if url.endswith('/json') else wheel)):
   with self.assertRaisesRegex(RuntimeError,'SHA256'):uv.ensure_uv(tmp)
   self.assertFalse((Path(tmp)/'uv').exists())
