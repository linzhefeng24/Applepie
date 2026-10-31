import contextlib,importlib.util,io,json,os,shutil,tempfile,unittest,zipfile
from pathlib import Path
spec=importlib.util.spec_from_file_location('backend_runtime',Path(__file__).resolve().parents[2]/'scripts/backend-runtime.py');runtime=importlib.util.module_from_spec(spec);spec.loader.exec_module(runtime)
class BackendRuntimeTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(prefix='aperture runtime ');self.root=Path(self.tmp.name)/'original';r=self.root
  (r/'backend/src/main/scala').mkdir(parents=True);(r/'backend/src/main/scala/Main.scala').write_text('object Main\n')
  (r/'backend/build.sbt').write_text('scalaVersion := "3.3.3"\n');(r/'backend/project').mkdir();(r/'backend/project/build.properties').write_text('sbt.version=1.10.7\n');(r/'backend/project/plugins.sbt').write_text('')
  classes=r/'backend/target/classes';classes.mkdir(parents=True);(classes/'Main.class').write_bytes(b'fixture-class')
  jar=r/'dependency.jar'
  with zipfile.ZipFile(jar,'w') as z:z.writestr('Fixture.class',b'fixture-dependency')
  (r/'.run').mkdir();(r/'.run/classpath').write_text(str(classes)+os.pathsep+str(jar))
  with contextlib.redirect_stdout(io.StringIO()):runtime.pack(r)
 def tearDown(self):self.tmp.cleanup()
 def test_pack_and_activate_preserve_classpath_order(self):
  files=runtime.validated(self.root);self.assertEqual([x.name for x in files],['app.jar','dependency.jar']);self.assertTrue(runtime.activate(self.root));self.assertEqual((self.root/'.run/classpath').read_text().split(os.pathsep),list(map(str,files)))
 def test_relocation_with_spaces_uses_new_root(self):
  moved=Path(self.tmp.name)/'new project location';shutil.copytree(self.root,moved);self.assertTrue(runtime.activate(moved));self.assertTrue(all(p.startswith(str(moved)) for p in (moved/'.run/classpath').read_text().split(os.pathsep)))
 def test_corrupt_artifact_rejected(self):
  with (self.root/'backend/runtime/app.jar').open('ab') as f:f.write(b'tampered')
  with self.assertRaises(runtime.CorruptRuntime):runtime.validated(self.root)
 def test_missing_manifest_rejected(self):
  (self.root/'backend/runtime/manifest.json').unlink()
  with self.assertRaises(runtime.CorruptRuntime):runtime.validated(self.root)
 def test_source_edits_require_rebuild(self):
  (self.root/'backend/src/main/scala/Main.scala').write_text('object Changed\n');self.assertIsNone(runtime.validated(self.root))
 def test_manifest_escape_rejected(self):
  path=self.root/'backend/runtime/manifest.json';m=json.loads(path.read_text());m['artifacts'][0]['path']='../outside.jar';path.write_text(json.dumps(m))
  with self.assertRaises(runtime.CorruptRuntime):runtime.validated(self.root)
if __name__=='__main__':unittest.main()
