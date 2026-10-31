"""Package a consistent launcher overlay, including the tests run by setup.sh."""
from pathlib import Path
import io,os,subprocess,sys,zipfile
ROOT=Path(__file__).resolve().parents[1]

def package(destination):
 repo=Path(subprocess.check_output(['git','rev-parse','--show-toplevel'],cwd=ROOT,text=True).strip())
 prefix=str(ROOT.relative_to(repo));tree='HEAD:'+prefix if prefix!='.' else 'HEAD'
 source=subprocess.check_output(['git','archive','--format=zip','--prefix=APERTURE/',tree],cwd=repo)
 folders=('scripts/','quant/tests/')
 files={'run.sh','config/defaults.json','.env.example','README.md','quant/requirements.txt','docs/VALIDATION.md'}
 out=Path(destination).resolve();out.parent.mkdir(parents=True,exist_ok=True)
 temporary=out.with_name(out.name+'.tmp')
 try:
  with zipfile.ZipFile(io.BytesIO(source)) as archive:
   selected=[entry for entry in archive.infolist() if not entry.is_dir() and (entry.filename.removeprefix('APERTURE/').startswith(folders) or entry.filename.removeprefix('APERTURE/') in files)]
   names={entry.filename.removeprefix('APERTURE/') for entry in selected}
   required={'scripts/bootstrap-uv.py','scripts/python-packages.sh','scripts/setup.sh','quant/tests/test_python_packages.py','quant/tests/test_uv_bootstrap.py','config/defaults.json','run.sh'}
   if not required<=names:raise RuntimeError('启动补丁缺少配套脚本或测试，已停止打包。')
   with zipfile.ZipFile(temporary,'w',zipfile.ZIP_DEFLATED) as target:
    for entry in selected:target.writestr(entry,archive.read(entry))
  with zipfile.ZipFile(temporary) as archive:
   if archive.testzip() is not None:raise RuntimeError('补丁 ZIP 校验失败')
  os.replace(temporary,out)
 finally:temporary.unlink(missing_ok=True)
 print(f'{out.name}: {out.stat().st_size} bytes；{len(selected)} 个文件，包含配套测试。')

if __name__=='__main__':
 default=Path(subprocess.check_output(['git','rev-parse','--show-toplevel'],cwd=ROOT,text=True).strip())/'downloads/APERTURE-startup-fix.zip'
 package(sys.argv[1] if len(sys.argv)>1 else default)
