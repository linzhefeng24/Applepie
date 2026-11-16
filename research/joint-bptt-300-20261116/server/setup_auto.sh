#!/usr/bin/env bash
# Additive installer for an existing, hash-verified runtime bundle.
# Keep original setup.sh and numerical files intact; choose a compatible Python
# automatically instead of making the user change their system Python.
set -euo pipefail
cd -- "$(dirname -- "$0")"
if [[ ! -f server.py || ! -f PACKAGE_MANIFEST.json || ! -f setup.sh ]]; then
  printf 'Place setup_auto.sh inside the extracted applepie_local directory.\n' >&2
  exit 1
fi
is_python312() {
  "$1" -c 'import sys; raise SystemExit(sys.version_info[:2] != (3,12))' >/dev/null 2>&1
}
python_bin=''
for candidate in "${PYTHON:-}" python3.12 python3 python; do
  if [[ -n "$candidate" ]] && command -v "$candidate" >/dev/null 2>&1 && is_python312 "$candidate"; then
    python_bin="$candidate"
    break
  fi
done
if [[ -z "$python_bin" ]]; then
  printf 'Preparing a project-specific Python3.12; existing system Python stays installed.\n'
  uv_bin=''
  if command -v uv >/dev/null 2>&1; then
    uv_bin="$(command -v uv)"
  elif [[ -x "$HOME/.local/bin/uv" ]]; then
    uv_bin="$HOME/.local/bin/uv"
  elif [[ -x "$PWD/.tools/bin/uv" ]]; then
    uv_bin="$PWD/.tools/bin/uv"
  fi
  if [[ -z "$uv_bin" ]]; then
    mkdir -p .tools/bin
    if command -v wget >/dev/null 2>&1; then
      wget -O .tools/install-uv.sh https://astral.sh/uv/install.sh
    elif command -v curl >/dev/null 2>&1; then
      curl -fL https://astral.sh/uv/install.sh -o .tools/install-uv.sh
    else
      printf 'Install wget or curl, then rerun this script.\n' >&2
      exit 1
    fi
    UV_INSTALL_DIR="$PWD/.tools/bin" UV_NO_MODIFY_PATH=1 sh .tools/install-uv.sh
    uv_bin="$PWD/.tools/bin/uv"
  fi
  export UV_PYTHON_INSTALL_DIR="${UV_PYTHON_INSTALL_DIR:-$PWD/.tools/python}"
  "$uv_bin" python install --no-bin 3.12
  python_bin="$("$uv_bin" python find --managed-python 3.12)"
fi
is_python312 "$python_bin"
# Avoid attempting to create a venv using its own existing executable.
python_bin="$("$python_bin" -c 'import sys; print(getattr(sys,"_base_executable",sys.executable))')"
is_python312 "$python_bin"
printf 'Using: %s\n' "$python_bin"
"$python_bin" --version
"$python_bin" server.py verify
if [[ -x .venv/bin/python ]] && ! is_python312 "$PWD/.venv/bin/python"; then
  backup=".venv.previous.$(date -u +%Y%m%dT%H%M%SZ).$$"
  mv .venv "$backup"
  printf 'Preserved incompatible project environment as %s\n' "$backup"
fi
PYTHON="$python_bin" bash setup.sh
