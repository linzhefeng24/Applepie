"""Cross-language contract checks: registered business APIs must have matching callers."""
from pathlib import Path
import re,unittest
ROOT=Path(__file__).resolve().parents[2]
class ApiContractTests(unittest.TestCase):
 def test_registered_messages_match_frontend_service_and_filename(self):
  backend=set()
  for route in (ROOT/'backend/src/main/scala/services').glob('*/routes/*Routes.scala'):
   owner=route.parents[1].name
   for message in re.findall(r'register\[(\w+),',route.read_text()):
    source=route.parents[1]/'api'/f'{message}.scala'
    self.assertTrue(source.exists(),str(source))
    self.assertIn(f'package services.{owner}.api',source.read_text())
    self.assertRegex(source.read_text(),r'def plan(?:\(connection: Connection\))?: IO\[')
    backend.add((owner,message))
  frontend=set()
  for message in (ROOT/'frontend/src/apis').glob('*/*Message.ts'):
   match=re.search(r'readonly service = "([^"]+)"',message.read_text())
   self.assertIsNotNone(match,str(message))
   self.assertEqual(message.parent.name,match[1])
   frontend.add((match[1],message.stem))
  self.assertEqual(backend,frontend)
