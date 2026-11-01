from pathlib import Path
import importlib.util,sys,tempfile,unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('managed_postgres',ROOT/'scripts/managed_postgres.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class ManagedPostgresTests(unittest.TestCase):
 def test_pid_reuse_does_not_mean_our_cluster_is_running(self):
  with tempfile.TemporaryDirectory() as folder:
   root=Path(folder);cluster=root/'cluster';cluster.mkdir();proc=root/'proc';(proc/'123').mkdir(parents=True)
   self.assertEqual(m.postmaster_state(cluster,proc),'stopped')
   (cluster/'postmaster.pid').write_text('123\n')
   (proc/'123/cmdline').write_bytes(b'python3\0another-program.py\0')
   self.assertEqual(m.postmaster_state(cluster,proc),'stale')
   (proc/'123/cmdline').write_bytes(b'/usr/bin/postgres\0-D\0'+str(cluster).encode()+b'\0')
   self.assertEqual(m.postmaster_state(cluster,proc),'running')
   (proc/'123/cmdline').write_bytes(b'/usr/bin/postgres\0-D\0/another/cluster\0')
   self.assertEqual(m.postmaster_state(cluster,proc),'stale')
   (proc/'123/cmdline').unlink();self.assertEqual(m.postmaster_state(cluster,proc),'stale')
 def test_refused_connection_is_retried_but_authentication_is_not(self):
  class Error(Exception):sqlstate=None
  connect=unittest.mock.Mock(side_effect=[Error('Connection refused'),object()])
  with patch.object(m.time,'sleep'):self.assertIsNotNone(m.connect_ready(connect,{},attempts=2))
  self.assertEqual(connect.call_count,2)
  class Recovering(Error):sqlstate='57P03'
  connect=unittest.mock.Mock(side_effect=[Recovering('database system is starting up'),object()])
  with patch.object(m.time,'sleep'):self.assertIsNotNone(m.connect_ready(connect,{},attempts=2))
  self.assertEqual(connect.call_count,2)
  connect=unittest.mock.Mock(side_effect=Error('password authentication failed'))
  with self.assertRaises(Error):m.connect_ready(connect,{})
  self.assertEqual(connect.call_count,1)
 def test_stale_marker_is_archived_without_signalling(self):
  with tempfile.TemporaryDirectory() as folder:
   marker=Path(folder)/'postmaster.pid';marker.write_text('old marker')
   with patch.object(m,'postmaster_state',return_value='stale'):self.assertTrue(m.archive_stale_pid(folder))
   self.assertFalse(marker.exists());self.assertEqual(next(Path(folder).glob('postmaster.pid.stale-*')).read_text(),'old marker')
