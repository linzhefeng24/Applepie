# Keep WSL unpacked runtimes on Linux, not in Windows Downloads or copied virtualenvs.
if [[ -z ${APERTURE_RUNTIME_DIR:-} ]]; then
 if [[ -n ${WSL_DISTRO_NAME:-} && "$ROOT" =~ ^/mnt/[a-zA-Z]/ ]]; then
  APERTURE_RUNTIME_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/aperture/runtimes"
 else
  APERTURE_RUNTIME_DIR="$ROOT/.tools/runtimes"
 fi
fi
[[ "$APERTURE_RUNTIME_DIR" == /* ]] || APERTURE_RUNTIME_DIR="$ROOT/$APERTURE_RUNTIME_DIR"
export APERTURE_RUNTIME_DIR
if [[ -x "$APERTURE_RUNTIME_DIR/java/bin/java" ]]; then
 export JAVA_HOME="$APERTURE_RUNTIME_DIR/java"
 export PATH="$JAVA_HOME/bin:$PATH"
fi
if [[ -x "$APERTURE_RUNTIME_DIR/node/bin/node" ]]; then export PATH="$APERTURE_RUNTIME_DIR/node/bin:$PATH"; fi
if [[ -x "$APERTURE_RUNTIME_DIR/python/bin/python3" ]]; then export PATH="$APERTURE_RUNTIME_DIR/python/bin:$PATH"; fi
