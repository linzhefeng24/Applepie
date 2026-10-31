#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT"
mkdir -p .run
if [[ ! -f .env ]]; then echo 'Run scripts/setup.sh first'; exit 1; fi
set -a; source .env; set +a
export DATA_DIR="$ROOT/data"
PG="$ROOT/.tools/pg/usr/lib/postgresql/17/bin"
if ! "$PG/pg_ctl" -D data/pg status >/dev/null 2>&1; then
 "$PG/pg_ctl" -D data/pg -l .run/postgres.log -o "-h 127.0.0.1 -p $DB_PORT -k $ROOT/.run" start
fi
[[ -f .run/classpath ]] || scripts/build-backend.sh
start() {
 local name=$1; shift
 if python3 scripts/processes.py alive "$name"; then return; fi
 nohup setsid "$@" > ".run/$name.log" 2>&1 < /dev/null & echo $! > ".run/$name.pid"
 python3 scripts/processes.py record "$name"
}
start quant env OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python quant/server.py
for service in market portfolio analysis; do
 start "$service" env SERVICE="$service" java -XX:ActiveProcessorCount=2 -Xmx384m -cp "$(cat .run/classpath)" Main
done
if [[ -f frontend/dist/index.html ]]; then start frontend npm --prefix frontend run preview; fi
.venv/bin/python - <<'PY'
import urllib.request,time
from pathlib import Path
ports=[8101,8102,8103,8104]+([4173] if Path("frontend/dist/index.html").exists() else [])
for port in ports:
 for attempt in range(60):
  try:
   with urllib.request.urlopen(f'http://127.0.0.1:{port}'+('/' if port==4173 else '/health'),timeout=2) as r: assert r.status==200
   print(f'Service {port} ready');break
  except Exception:
   if attempt==59:raise
   time.sleep(.5)
PY
