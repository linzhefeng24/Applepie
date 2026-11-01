#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT"
source scripts/runtime-env.sh
source scripts/config.sh
mapfile -t names < <(python3 - <<'PYNAMES'
import json
from pathlib import Path
print('\n'.join([s['name'] for s in json.loads(Path('config/services.json').read_text())]+['frontend','market','history','analysis','portfolio','quant']))
PYNAMES
)
for name in "${names[@]}"; do python3 scripts/processes.py stop "$name"; done
if [[ "${1:-}" == '--database' && "$MANAGE_POSTGRES" == true ]]; then "$PYTHON_BIN" scripts/service-environment.py stop; fi
echo 'Project services stopped.'
