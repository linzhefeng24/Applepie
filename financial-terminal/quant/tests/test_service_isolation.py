"""Architectural invariants: no cross-service SQL and independently launchable business artifacts."""
from pathlib import Path
import json,re,unittest
ROOT=Path(__file__).resolve().parents[2]
class ServiceIsolationTests(unittest.TestCase):
 def test_registry_and_entrypoints(self):
  services=json.loads((ROOT/'config/services.json').read_text());self.assertEqual(len(services),19)
  self.assertEqual(len({s['port'] for s in services}),19)
  dbs=[s['dbPort'] for s in services if s['database']];self.assertEqual(len(dbs),8);self.assertEqual(len(set(dbs)),8)
  for s in services:
   if s['kind']=='scala':self.assertTrue((ROOT/f"backend/src/main/scala/services/{s['name']}/routes/ServiceMain.scala").exists())
 def test_no_cross_owner_table_access(self):
  for p in (ROOT/'backend/src/main/scala/services').rglob('*.scala'):
   owner=p.relative_to(ROOT/'backend/src/main/scala/services').parts[0]
   for imported in re.findall(r'(?:import|new) services\.(\w+)\.tables',p.read_text()):self.assertEqual(owner,imported,str(p))
 def test_python_workers_have_distinct_routes_and_no_database_imports(self):
  for name in ['optimizer','backtest']:
   s=(ROOT/f'quant/{name}_server.py').read_text();self.assertIn("serve('quant_"+name,s)
  for directory in ['optimization','backtesting','shared','transport']:
   for p in (ROOT/'quant'/directory).rglob('*.py'):self.assertNotRegex(p.read_text(),r'\b(?:psycopg|sqlalchemy|sqlite3)\b',str(p))
 def test_packaged_business_classpaths_are_disjoint(self):
  manifest=ROOT/'backend/runtime/manifest.json'
  if not manifest.exists():self.skipTest('No packaged runtime')
  m=json.loads(manifest.read_text())
  if m['format']!=2:self.skipTest('Legacy local runtime awaiting repack')
  for name,entry in m['services'].items():
   self.assertEqual([p for p in entry['classpath'] if p.startswith('services/')],[f'services/{name}.jar'])
