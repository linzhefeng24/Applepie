"""Install a checksum-verified native uv binary without importing or executing pip."""
from pathlib import Path
import hashlib,json,os,platform,re,ssl,sys,tempfile,urllib.parse,urllib.request,zipfile
ROOT=Path(__file__).resolve().parents[1]
VERSION='0.9.27'
def checksum(path):
 with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def ensure_uv(directory):
 directory=Path(directory).absolute();directory.mkdir(parents=True,exist_ok=True)
 target=directory/'uv';manifest=directory/'manifest.json';arch=platform.machine()
 try:
  saved=json.loads(manifest.read_text())
  if saved['version']==VERSION and saved['arch']==arch and target.is_file() and checksum(target)==saved['binarySha256']:
   return target
 except (OSError,ValueError,KeyError,TypeError):pass
 tags={'x86_64':'x86_64','aarch64':'aarch64','arm64':'aarch64'}
 if sys.platform!='linux' or arch not in tags:raise RuntimeError('当前平台暂不支持自动安装 uv。')
 cert=os.environ.get('PIP_CERT') or os.environ.get('SSL_CERT_FILE')
 context=ssl.create_default_context()
 if cert:context.load_verify_locations(cafile=cert)
 print('正在下载经过 SHA256 验证的 uv 工具（不使用旧 pip）…',file=sys.stderr,flush=True)
 def request(url):return urllib.request.urlopen(url,context=context,timeout=60)
 with request(f'https://pypi.org/pypi/uv/{VERSION}/json') as response:metadata=json.load(response)
 if metadata['info']['version']!=VERSION:raise RuntimeError('uv 版本元数据不匹配')
 candidates=[f for f in metadata['urls'] if f['packagetype']=='bdist_wheel' and 'manylinux_2_17_'+tags[arch] in f['filename']]
 if len(candidates)!=1:raise RuntimeError('未找到唯一兼容的 uv 安装包')
 wheel=candidates[0];url=urllib.parse.urlparse(wheel['url']);expected=wheel['digests']['sha256']
 if url.scheme!='https' or url.hostname!='files.pythonhosted.org' or not re.fullmatch('[0-9a-f]{64}',expected):raise RuntimeError('uv 下载来源或校验和无效')
 with tempfile.TemporaryDirectory(prefix='download-',dir=directory) as tmp:
  archive=Path(tmp)/'uv.whl';h=hashlib.sha256()
  with request(wheel['url']) as response,archive.open('wb') as out:
   while True:
    block=response.read(1024*1024)
    if not block:break
    h.update(block);out.write(block)
  if h.hexdigest()!=expected:raise RuntimeError('uv 安装包 SHA256 校验失败，已停止使用')
  with zipfile.ZipFile(archive) as z:
   names=[n for n in z.namelist() if n in {f'uv-{VERSION}.data/scripts/uv','uv/uv'}]
   if len(names)!=1:raise RuntimeError('uv 安装包内可执行文件无效')
   binary=Path(tmp)/'uv'
   with z.open(names[0]) as src,binary.open('wb') as out:
    while True:
     block=src.read(1024*1024)
     if not block:break
     out.write(block)
  with binary.open('rb') as f:
   if f.read(4)!=b'\x7fELF':raise RuntimeError('uv 文件不是有效 Linux 可执行文件')
  binary.chmod(0o755)
  saved=dict(version=VERSION,arch=arch,wheelSha256=expected,binarySha256=checksum(binary))
  meta=Path(tmp)/'manifest.json';meta.write_text(json.dumps(saved,indent=2)+'\n')
  os.replace(binary,target);os.replace(meta,manifest)
 print('uv 工具已通过完整性校验。',file=sys.stderr,flush=True)
 return target
if __name__=='__main__':
 try:
  directory=Path(os.environ.get('APERTURE_RUNTIME_DIR',str(ROOT/'.tools/runtimes')))/'uv-native'
  print(ensure_uv(directory))
 except Exception as e:print('uv 自动准备失败：'+str(e),file=sys.stderr);raise SystemExit(1)
