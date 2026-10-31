"""Create APERTURE.zip from tracked source plus verified, prebuilt Scala dependencies."""
from pathlib import Path
import io,subprocess,sys,zipfile,importlib.util,hashlib
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('backend_runtime',ROOT/'scripts/backend-runtime.py');runtime=importlib.util.module_from_spec(spec);spec.loader.exec_module(runtime)
if runtime.validated(ROOT) is None:raise SystemExit('请先编译并运行 scripts/backend-runtime.py pack')
repo=Path(subprocess.check_output(['git','rev-parse','--show-toplevel'],cwd=ROOT,text=True).strip())
prefix=str(ROOT.relative_to(repo));tree='HEAD:'+prefix if prefix!='.' else 'HEAD'
source=subprocess.check_output(['git','archive','--format=zip','--prefix=APERTURE/',tree],cwd=repo)
# The bundled source must match the runtime, not merely the developer's working tree.
with zipfile.ZipFile(io.BytesIO(source)) as archive:
    selected=[]
    for item in archive.infolist():
        if item.is_dir():continue
        rel=Path(item.filename).relative_to('APERTURE')
        if str(rel).startswith('backend/src/main/') or str(rel) in {'backend/build.sbt','backend/project/build.properties','backend/project/plugins.sbt'}:selected.append((rel,item))
    fingerprint=hashlib.sha256()
    for rel,item in sorted(selected,key=lambda pair:pair[0]):fingerprint.update(str(rel).encode());fingerprint.update(archive.read(item))
    if fingerprint.hexdigest()!=runtime.source_hash(ROOT):raise SystemExit('Git HEAD 中的 Scala 源码与运行包不一致，请先提交源码再发布。')
out=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else repo/'downloads/APERTURE.zip';out.parent.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(io.BytesIO(source)) as src,zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as dest:
    for entry in src.infolist():dest.writestr(entry,src.read(entry))
    for p in sorted((ROOT/'backend/runtime').rglob('*')):
        if p.is_file():dest.write(p,str(Path('APERTURE')/p.relative_to(ROOT)))
with zipfile.ZipFile(out) as z:
    if z.testzip() is not None:raise SystemExit('ZIP 校验失败')
print(f'{out.name}: {out.stat().st_size/1024/1024:.1f} MiB；包含已验证的 Scala 运行包，正常启动不访问 Maven。')
