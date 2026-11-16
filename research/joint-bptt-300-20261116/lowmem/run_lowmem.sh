#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 NUMBA_NUM_THREADS=1
export JAX_PLATFORMS=cpu PYTHONUNBUFFERED=1 SYNC_EVERY_SAVE=0
export XLA_FLAGS='--xla_cpu_multi_thread_eigen=false --xla_cpu_enable_fast_math=false'
export MPLCONFIGDIR="${TMPDIR:-/tmp}/applepie-lowmem-plots"
exec .venv/bin/python -c '
import os,runpy
limit=max(1,int(os.environ.get("APPLEPIE_LOW_MEMORY_CPUS","4")))
if hasattr(os,"sched_getaffinity"):
    cpus=sorted(os.sched_getaffinity(0));os.sched_setaffinity(0,cpus[:limit])
    print("LOW_MEMORY_CPU_LIMIT",len(os.sched_getaffinity(0)),flush=True)
runpy.run_path("lowmem/launch.py",run_name="__main__")
' "$@"
