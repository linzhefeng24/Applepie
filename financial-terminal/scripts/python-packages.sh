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
 echo '本项目使用独立的 HTTPS Python 软件源，不修改系统 pip 配置。'
 "$python_executable" -m pip --disable-pip-version-check install \
  --index-url "$index" --only-binary=:all: --timeout 30 --retries 2 "$@"
)
