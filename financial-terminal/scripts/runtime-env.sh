# Project-local tools are activated only for this launcher and its child processes.
APERTURE_RUNTIME_DIR="$ROOT/.tools/runtimes"
if [[ -x "$APERTURE_RUNTIME_DIR/java/bin/java" ]]; then
 export JAVA_HOME="$APERTURE_RUNTIME_DIR/java"
 export PATH="$JAVA_HOME/bin:$PATH"
fi
if [[ -x "$APERTURE_RUNTIME_DIR/node/bin/node" ]]; then export PATH="$APERTURE_RUNTIME_DIR/node/bin:$PATH"; fi
if [[ -x "$APERTURE_RUNTIME_DIR/python/bin/python3" ]]; then export PATH="$APERTURE_RUNTIME_DIR/python/bin:$PATH"; fi
