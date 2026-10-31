#!/usr/bin/env bash
# One entry point from any directory: bash /path/to/project/run.sh
set -euo pipefail
ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
cd "$ROOT"
usage() {
 cat <<'EOF'
APERTURE 金融终端
  bash run.sh           首次安装项目依赖、构建并启动；以后直接启动
  bash run.sh stop      停止本项目服务及项目管理的数据库
  bash run.sh restart   重启（保留数据）
  bash run.sh setup     强制重新安装项目依赖并构建，再启动
  bash run.sh help      查看说明

需要 Linux / WSL、JDK 21+、Node 24+、Python 3.12+。
首次安装需要网络。自定义配置见 .env.example，日志在 .run/。
EOF
}
mode=${1:-start}
case "$mode" in start|stop|restart|setup) ;; help|-h|--help) usage; exit 0;; *) usage; exit 2;; esac
if [[ $# -gt 1 ]]; then usage; exit 2; fi
if [[ "$(uname -s)" != Linux ]]; then
 echo '当前一键脚本支持 Linux。Windows 请在 WSL 终端运行；尚未适配原生 Windows/macOS。'; exit 1
fi
if ! command -v python3 >/dev/null; then echo '缺少 Python 3.12+，请先安装并确保 python3 在 PATH 中。'; exit 1; fi
if [[ "$mode" == stop ]]; then bash scripts/stop-services.sh --database; exit; fi
missing=0
for tool in java node npm curl sha256sum setsid; do
 if ! command -v "$tool" >/dev/null; then echo "缺少基础工具：$tool"; missing=1; fi
done
[[ "$missing" == 0 ]] || { echo '请先安装 JDK 21+、Node 24+、Python 3.12+，然后再次运行同一个命令。'; exit 1; }
python3 - <<'PY'
import subprocess,re,sys
if sys.version_info<(3,12):raise SystemExit('需要 Python 3.12+。')
node=subprocess.check_output(['node','--version'],text=True)
if int(node.lstrip('v').split('.')[0])<24:raise SystemExit('需要 Node 24+。')
java=subprocess.run(['java','-version'],capture_output=True,text=True,check=True)
match=re.search(r'version "(\d+)',java.stderr+java.stdout)
if not match or int(match[1])<21:raise SystemExit('需要 JDK 21+。')
PY
mkdir -p .run
if [[ "$mode" == restart ]]; then bash scripts/stop-services.sh --database; fi
# Do not reinstall for every launch. Invalidate on relocation or dependency changes.
if [[ "$mode" == setup ]] || ! python3 scripts/launcher-state.py check; then
 bash scripts/stop-services.sh
 echo '首次运行或项目依赖发生变化：正在安装和构建，可能需要几分钟…'
 if ! bash scripts/setup.sh 2>&1 | tee .run/launcher-setup.log; then
  echo '安装未完成。请查看上面的错误和 .run/launcher-setup.log，修复后重新运行 bash run.sh。'; exit 1
 fi
 python3 scripts/launcher-state.py save
else
 # Source edits need a rebuild, even if dependencies did not change.
 if ! python3 scripts/launcher-state.py build-check; then
  echo '检测到代码更新，正在重新构建…'
  bash scripts/stop-services.sh
  bash scripts/build-backend.sh
  npm --prefix frontend run build
  python3 scripts/launcher-state.py save
 fi
fi
if ! bash scripts/start-services.sh; then
 echo '启动失败。请查看 .run/ 中对应服务的日志；修复后重新运行 bash run.sh。'; exit 1
fi
source scripts/config.sh
printf '\nAPERTURE 已启动。请在本机浏览器访问：%s\n' "$FRONTEND_URL"
echo '服务在后台运行。停止：bash run.sh stop；重启：bash run.sh restart。'
