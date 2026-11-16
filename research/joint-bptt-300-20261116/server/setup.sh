#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
python_bin="${PYTHON:-python3}"
"$python_bin" -c 'import sys; assert sys.version_info[:2] == (3,12), "Please use Python3.12 (see README_zh.md)"'
"$python_bin" server.py verify
"$python_bin" -m venv .venv
.venv/bin/python -m pip install -r research/joint-bptt-300-20261116/requirements.txt
.venv/bin/python research/joint-bptt-300-20261116/patch_mjx.py
printf '\nSetup complete. Run: bash run.sh info; bash run.sh check\n'
