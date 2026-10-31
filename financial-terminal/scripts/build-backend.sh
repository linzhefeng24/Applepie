#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
mkdir -p "$ROOT/.run"
"$ROOT/scripts/sbt.sh" compile 'export Runtime / fullClasspath' > "$ROOT/.run/compile.log" 2>&1 || { tail -60 "$ROOT/.run/compile.log"; exit 1; }
python3 - "$ROOT" <<'PY'
from pathlib import Path
import sys
r=Path(sys.argv[1]);lines=(r/'.run/compile.log').read_text().splitlines();cp=next(s for s in reversed(lines) if s.startswith('/') and '.jar' in s);(r/'.run/classpath').write_text(cp)
PY
echo 'Scala services compiled.'
