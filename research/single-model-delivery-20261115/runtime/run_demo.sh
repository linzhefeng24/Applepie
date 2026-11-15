#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python 02_code/run.py demo
