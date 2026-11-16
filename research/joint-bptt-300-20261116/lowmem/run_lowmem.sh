#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 NUMBA_NUM_THREADS=1
export JAX_PLATFORMS=cpu PYTHONUNBUFFERED=1 SYNC_EVERY_SAVE=0
export XLA_FLAGS='--xla_cpu_multi_thread_eigen=false --xla_cpu_enable_fast_math=false'
export MPLCONFIGDIR="${TMPDIR:-/tmp}/applepie-lowmem-plots"
exec .venv/bin/python lowmem/launch.py "$@"
