"""Create/recover only the selected managed venv; pip is not required."""
from pathlib import Path
import os,subprocess,sys,time
from settings import read_settings
cfg=read_settings();target=Path(cfg['APERTURE_VENV_DIR']);python=Path(cfg['PYTHON_BIN'])
def valid(executable):
 try:return subprocess.run([str(executable),'-c','import sys,ssl,json;assert (3,12)<=sys.version_info[:2]<(3,14);assert sys.prefix!=sys.base_prefix'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0
 except OSError:return False
if valid(python):raise SystemExit(0)
if python!=target/'bin/python':raise SystemExit('显式配置的 PYTHON_BIN 不可用，未修改该外部环境。')
if target.exists() or target.is_symlink():
 if not target.is_symlink() and not (target/'pyvenv.cfg').exists() and any(target.iterdir()):raise SystemExit('虚拟环境目录包含未知文件，未覆盖。')
 backup=target.with_name(target.name+'.broken-'+str(time.time_ns()));target.rename(backup)
 print('已保留损坏的旧虚拟环境备份，正在创建干净环境。')
target.parent.mkdir(parents=True,exist_ok=True)
subprocess.run([os.environ['APERTURE_UV_BIN'],'--no-config','venv','--python',sys.executable,str(target)],check=True)
if not valid(python):raise SystemExit('项目 Python 环境创建后检查失败。')
print('项目 Python 环境已就绪（不依赖 pip）。')
