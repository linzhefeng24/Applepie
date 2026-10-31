# Public project dependencies use a process-local index. Global pip config is never edited.
aperture_pip_install() (
 local python_executable=$1 index=${APERTURE_PYPI_INDEX_URL:-https://pypi.org/simple} name
 shift
 [[ "$index" == https://* ]] || { echo '项目 Python 软件源必须使用 HTTPS。'; return 1; }
 # Avoid inherited private indexes/extra indexes/targets/trusted-host disabling TLS.
 # Keep explicit CA, client certificate and proxy settings for the existing network.
 for name in "${!PIP_@}"; do
  case "$name" in PIP_CERT|PIP_CLIENT_CERT|PIP_PROXY|PIP_REQUIRE_HASHES|PIP_REQUIRE_VIRTUALENV|PIP_KEYRING_PROVIDER) ;; *) unset "$name";; esac
 done
 export PIP_CONFIG_FILE=/dev/null
 if [[ -n ${APERTURE_UV_BIN:-} && -x "$APERTURE_UV_BIN" ]]; then
  # Native uv installs into a venv directly; it never imports that venv's pip.
  unset UV_INDEX UV_DEFAULT_INDEX UV_INDEX_URL UV_EXTRA_INDEX_URL UV_FIND_LINKS UV_NO_INDEX UV_INSECURE_HOST UV_CONFIG_FILE
  [[ -z ${PIP_CERT:-} ]] || export SSL_CERT_FILE="$PIP_CERT"
  if [[ -n ${PIP_PROXY:-} ]]; then export HTTPS_PROXY="$PIP_PROXY" HTTP_PROXY="$PIP_PROXY"; fi
  local flags=()
  case "${PIP_REQUIRE_HASHES:-}" in 1|true|yes|on) flags+=(--require-hashes);; esac
  [[ ${APERTURE_REINSTALL:-0} != 1 ]] || flags+=(--reinstall)
  echo '使用经过校验的原生 uv 安装 Python 依赖（不调用 pip），软件源与全局配置隔离。'
  "$APERTURE_UV_BIN" --no-config pip install --python "$python_executable" --index-url "$index" --only-binary=:all: "${flags[@]}" "$@"
  return
 fi
 echo '本项目使用独立的 HTTPS Python 软件源，不修改系统 pip 配置。'
 "$python_executable" -m pip --disable-pip-version-check install \
  --index-url "$index" --only-binary=:all: --timeout 30 --retries 2 "$@"
)
