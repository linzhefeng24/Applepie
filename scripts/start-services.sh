#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT"
source scripts/config.sh
mkdir -p .run
if [[ "$MANAGE_POSTGRES" == true ]]; then
 [[ -x "$PG_BIN/pg_ctl" ]] || { echo 'PostgreSQL not found. Run scripts/setup.sh or configure PG_BIN.'; exit 1; }
 mkdir -p "$PG_SOCKET_DIR"; chmod 700 "$PG_SOCKET_DIR"
 if ! "$PG_BIN/pg_ctl" -D "$PG_DATA_DIR" status >/dev/null 2>&1; then
  "$PG_BIN/pg_ctl" -D "$PG_DATA_DIR" -l "$ROOT/.run/postgres.log" -o "-h $DB_HOST -p $DB_PORT -k '$PG_SOCKET_DIR'" start
 fi
fi
# Java classpaths are generated machine-local artifacts. Rebuild when moved or when entries vanished.
if ! python3 - <<'PY'
from pathlib import Path
import sys
root=Path.cwd();stamp=root/'.run/build-root';cp=root/'.run/classpath'
try: valid=stamp.read_text()==str(root) and all(Path(p).exists() for p in cp.read_text().split(':'))
except OSError:valid=False
sys.exit(0 if valid else 1)
PY
then scripts/build-backend.sh; fi
start() {
 local name=$1; shift
 if python3 scripts/processes.py alive "$name"; then return; fi
 nohup setsid "$@" > ".run/$name.log" 2>&1 < /dev/null & echo $! > ".run/$name.pid"
 python3 scripts/processes.py record "$name"
}
start quant env OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 "$PYTHON_BIN" quant/server.py
for service in market portfolio analysis; do
 key="${service^^}_PORT"
 start "$service" env SERVICE="$service" HTTP_PORT="${!key}" java -XX:ActiveProcessorCount=2 -Xmx384m -cp "$(cat .run/classpath)" Main
done
if [[ -f frontend/dist/index.html ]]; then start frontend npm --prefix frontend run preview; fi
"$PYTHON_BIN" - <<'PY'
import urllib.request,time,os
from pathlib import Path
urls=[os.environ[k+'_URL']+'/health' for k in ['MARKET','PORTFOLIO','ANALYSIS','QUANT']]
if Path('frontend/dist/index.html').exists():urls.append(os.environ['FRONTEND_URL'])
for url in urls:
 for attempt in range(60):
  try:
   with urllib.request.urlopen(url,timeout=2) as r:assert r.status==200
   print(f'Ready: {url}');break
  except Exception:
   if attempt==59:raise
   time.sleep(.5)
PY
