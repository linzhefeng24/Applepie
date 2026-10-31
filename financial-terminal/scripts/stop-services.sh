#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT"
source scripts/config.sh
for name in frontend analysis portfolio market quant; do python3 scripts/processes.py stop "$name"; done
if [[ "${1:-}" == '--database' && "$MANAGE_POSTGRES" == true ]]; then "$PG_BIN/pg_ctl" -D "$PG_DATA_DIR" stop -m fast; fi
echo 'Project services stopped.'
