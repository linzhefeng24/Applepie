#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT"
for name in frontend analysis portfolio market quant; do python3 scripts/processes.py stop "$name"; done
if [[ "${1:-}" == '--database' ]]; then .tools/pg/usr/lib/postgresql/17/bin/pg_ctl -D data/pg stop -m fast; fi
echo 'Project services stopped.'
