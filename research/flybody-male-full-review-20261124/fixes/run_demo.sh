#!/usr/bin/env bash
# Unix LF launcher; model parameters and default Python entry point are unchanged.
set -euo pipefail
cd "$(dirname "$0")"
"${PYTHON:-python3}" 02_code/run_manual.py --render "$@"
