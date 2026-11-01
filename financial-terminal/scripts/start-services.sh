#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT"
source scripts/runtime-env.sh
source scripts/config.sh
mkdir -p .run
"$PYTHON_BIN" scripts/service-environment.py
scripts/build-backend.sh
"$PYTHON_BIN" scripts/start-services.py
