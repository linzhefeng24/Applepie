"""Run a command with the configured project interpreter, including WSL Linux caches."""
import os,sys
from settings import read_settings
python=read_settings()['PYTHON_BIN']
if not os.path.isfile(python):raise SystemExit('项目 Python 尚未准备好，请先运行 bash run.sh。')
os.execv(python,[python,*sys.argv[1:]])
