#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT"
source scripts/runtime-env.sh
source scripts/config.sh
for name in frontend backtest optimization reports watchlist statistics history analysis portfolio market quant; do python3 scripts/processes.py stop "$name"; done
if [[ "${1:-}" == '--database' && "$MANAGE_POSTGRES" == true && -x "$PG_BIN/pg_ctl" ]] && "$PG_BIN/pg_ctl" -D "$PG_DATA_DIR" status >/dev/null 2>&1; then "$PG_BIN/pg_ctl" -D "$PG_DATA_DIR" stop -m fast; fi
echo 'Project services stopped.'
