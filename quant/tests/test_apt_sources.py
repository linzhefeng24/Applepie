"""Source selection must preserve signature checks and exclude unrelated repositories."""
import subprocess,tempfile,unittest,os
from pathlib import Path
HELPER=Path(__file__).resolve().parents[2]/'scripts/apt-official.sh'
class OfficialSourceTests(unittest.TestCase):
 def generate(self,distro,suite,arch):
  with tempfile.TemporaryDirectory() as temp:
   out=Path(temp)/'official.sources'
   result=subprocess.run(['bash','-c','source "$1"; aperture_write_official_sources "$2" "$3" "$4" "$5"','test',str(HELPER),distro,suite,arch,str(out)],capture_output=True,text=True)
   return result,out.read_text() if out.exists() else ''
 def test_ubuntu_resolute_signed_official_sources(self):
  result,text=self.generate('ubuntu','resolute','amd64');self.assertEqual(result.returncode,0);self.assertIn('Suites: resolute resolute-updates',text);self.assertIn('Suites: resolute-security',text);self.assertIn('ubuntu-archive-keyring.gpg',text);self.assertNotIn('docker.com',text);self.assertNotIn('nodesource',text);self.assertNotIn('Trusted:',text)
 def test_ubuntu_arm_uses_ports_for_security_too(self):
  result,text=self.generate('ubuntu','noble','arm64');self.assertEqual(result.returncode,0);self.assertEqual(text.count('URIs: http://ports.ubuntu.com/ubuntu-ports'),2);self.assertNotIn('security.ubuntu.com',text)
 def test_debian_signed_official_sources(self):
  result,text=self.generate('debian','trixie','amd64');self.assertEqual(result.returncode,0);self.assertIn('deb.debian.org/debian-security',text);self.assertIn('debian-archive-keyring.gpg',text)
 def test_rejects_source_field_injection(self):
  result,text=self.generate('ubuntu','noble\nTrusted: yes','amd64');self.assertNotEqual(result.returncode,0);self.assertEqual(text,'')
 def test_invocation_uses_isolated_sources_and_lists(self):
  if not Path('/etc/os-release').exists():self.skipTest('Linux only')
  with tempfile.TemporaryDirectory() as temp:
   code='source "$1"; . /etc/os-release; aperture_prepare_apt_options "$ID" "$VERSION_CODENAME" "$(dpkg --print-architecture)"; printf "%s\\n" "${APERTURE_APT_OPTIONS[@]}"'
   result=subprocess.run(['bash','-c',code,'test',str(HELPER)],capture_output=True,text=True,env={**os.environ,'TMPDIR':temp})
   if not any(Path(p).exists() for p in ['/usr/share/keyrings/ubuntu-archive-keyring.gpg','/usr/share/keyrings/debian-archive-keyring.gpg']):self.skipTest('No distro keyring')
   self.assertEqual(result.returncode,0,result.stderr);self.assertIn('Dir::Etc::sourcelist='+temp,result.stdout);self.assertIn('Dir::Etc::sourceparts='+temp,result.stdout);self.assertIn('Dir::State::lists='+temp,result.stdout);self.assertIn('AllowUnauthenticated=false',result.stdout);self.assertIn('AllowInsecureRepositories=false',result.stdout)
if __name__=='__main__':unittest.main()
