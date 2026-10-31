import json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'scripts'))
from settings import ROOT,read_settings
class ConfigurationTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory(prefix='aperture config ');self.root=Path(self.temp.name);(self.root/'config').mkdir();(self.root/'config/defaults.json').write_text((ROOT/'config/defaults.json').read_text())
 def tearDown(self):self.temp.cleanup()
 def test_relative_paths_follow_project_root_with_spaces(self):
  cfg=read_settings(self.root,environ={'PATH':''});self.assertEqual(cfg['DATA_DIR'],str(self.root/'data'));self.assertEqual(cfg['PG_DATA_DIR'],str(self.root/'data/pg'));self.assertIn('aperture config ',cfg['DATA_DIR'])
 def test_environment_wins_over_dotenv_and_defaults(self):
  (self.root/'.env').write_text('MARKET_PORT=8201\nDATA_DIR="my data"\nDB_PASSWORD="a b # c"\n')
  cfg=read_settings(self.root,environ={'PATH':'','MARKET_PORT':'8301'});self.assertEqual(cfg['MARKET_URL'],'http://127.0.0.1:8301');self.assertEqual(cfg['DATA_DIR'],str(self.root/'my data'));self.assertEqual(cfg['DB_PASSWORD'],'a b # c')
 def test_explicit_service_urls_preserved(self):
  (self.root/'.env').write_text('MARKET_URL=https://market.example.test\n');self.assertEqual(read_settings(self.root,environ={'PATH':''})['MARKET_URL'],'https://market.example.test')
 def test_no_execution_of_dotenv_text(self):
  target=self.root/'must-not-exist';value=f'$(touch "{target}")';(self.root/'.env').write_text('DB_PASSWORD='+repr(value)+'\n');cfg=read_settings(self.root,environ={'PATH':''});self.assertEqual(cfg['DB_PASSWORD'],value);self.assertFalse(target.exists())
 def test_discovers_bundled_postgres_without_version_path(self):
  binary=self.root/'.tools/pg/anything/version/bin';binary.mkdir(parents=True);(binary/'pg_ctl').touch();share=self.root/'.tools/pg/anything/share';share.mkdir();(share/'postgres.bki').touch();cfg=read_settings(self.root,environ={'PATH':''});self.assertEqual(cfg['PG_BIN'],str(binary));self.assertEqual(cfg['PG_SHARE'],str(share))
 def test_python_executable_preserves_venv_symlink_location(self):
  binary=self.root/'.venv/bin';binary.mkdir(parents=True);(binary/'python').symlink_to(sys.executable);cfg=read_settings(self.root,environ={'PATH':''});self.assertEqual(cfg['PYTHON_BIN'],str(binary/'python'))
if __name__=='__main__':unittest.main()
