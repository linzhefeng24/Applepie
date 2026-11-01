#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
mkdir -p "$ROOT/.run"
if [[ ${APERTURE_BUILD_FROM_SOURCE:-0} != 1 ]]; then
 if python3 "$ROOT/scripts/backend-runtime.py" activate; then exit 0; else status=$?; fi
 if [[ $status -ne 1 ]]; then exit "$status"; fi
fi
echo '正在构建 Scala 后端。首次需要下载 sbt / Scala / Maven 依赖，输出会实时显示。'
echo '完整日志保存在项目的 .run/compile.log。'
# Keep a visible heartbeat even when the JVM is waiting for a dependency download.
python3 -u -c 'import time
start=time.monotonic()
while True:
 time.sleep(20)
 print(f"Scala 构建进程仍在运行（已用时 {int(time.monotonic()-start)} 秒），详细日志：.run/compile.log",flush=True)' &
heartbeat_pid=$!
cleanup() { kill "$heartbeat_pid" 2>/dev/null || true; wait "$heartbeat_pid" 2>/dev/null || true; }
trap cleanup EXIT
# pipefail preserves the actual sbt failure; tee must not turn a failed build into success.
mapfile -t exports < <(python3 - "$ROOT" <<'PYEXPORT'
import json,sys
from pathlib import Path
for s in json.loads((Path(sys.argv[1])/'config/services.json').read_text()):
 if s['kind']=='scala':print('export '+s['name']+' / Runtime / fullClasspath')
PYEXPORT
)
"$ROOT/scripts/sbt.sh" compile "${exports[@]}" 2>&1 | tee "$ROOT/.run/compile.log" | python3 -u -c 'import sys
for line in sys.stdin:
 # The generated Java classpath is retained in the file but need not flood the terminal.
 if not (line.startswith("/") and ".jar" in line and ":" in line):
  print(line,end="",flush=True)'
cleanup
trap - EXIT
python3 - "$ROOT" <<'PY'
from pathlib import Path
import sys
import json
r=Path(sys.argv[1]);lines=(r/'.run/compile.log').read_text().splitlines()
names=[s['name'] for s in json.loads((r/'config/services.json').read_text()) if s['kind']=='scala']
classpaths=[s for s in lines if s.startswith('/') and '.jar' in s]
assert len(classpaths)==len(names),(len(classpaths),len(names))
(r/'.run/source-classpaths.json').write_text(json.dumps(dict(zip(names,classpaths))))
(r/'.run/service-classpaths.json').write_text(json.dumps({name:dict(mainClass=f'services.{name}.routes.ServiceMain',classpath=cp) for name,cp in zip(names,classpaths)}))
(r/'.run/build-root').write_text(str(r.resolve()))
PY
echo 'Scala 后端构建完成。'
