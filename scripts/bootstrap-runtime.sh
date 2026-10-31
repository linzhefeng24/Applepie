#!/usr/bin/env bash
# Ubuntu/Debian bootstrap. Never changes global Node/Python versions or shell profiles.
# Can also be invoked directly: bash scripts/bootstrap-runtime.sh
set -euo pipefail
ROOT=${ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}
source "$ROOT/scripts/runtime-env.sh"
source "$ROOT/scripts/apt-official.sh"

aperture_java_ok() {
 local major
 command -v java >/dev/null || return 1
 major=$(java -version 2>&1 | sed -nE 's/.*version "([0-9]+).*/\1/p' | head -1)
 [[ "$major" =~ ^[0-9]+$ && "$major" -ge 21 ]]
}
aperture_python_ok() { command -v python3 >/dev/null && python3 -c 'import sys;sys.exit(0 if (3,12)<=sys.version_info[:2]<(3,14) else 1)'; }
aperture_node_ok() { command -v node >/dev/null && command -v npm >/dev/null && node -e 'if(+process.versions.node.split(".")[0]<24)process.exit(1)'; }
aperture_link() {
 if [[ -e "$2" && ! -L "$2" ]]; then echo "工具目录已存在且不是链接，未覆盖：$2"; return 1; fi
 ln -sfn "$1" "$2"
}
aperture_apt_install() {
 if [[ ${APERTURE_NO_SYSTEM_INSTALL:-0} == 1 ]]; then echo "当前禁止系统安装，缺少的软件包：$*"; return 1; fi
 if [[ ${APERTURE_APT_READY:-0} != 1 ]]; then
  if [[ ! -r /etc/os-release ]] || ! command -v apt-get >/dev/null; then
   echo '自动安装基础工具目前支持 Ubuntu / Debian（含 WSL）；请在该环境运行。'; return 1
  fi
  local aperture_os_id aperture_os_suite aperture_os_arch
  aperture_os_id=$(. /etc/os-release; printf '%s' "$ID")
  case "$aperture_os_id" in ubuntu|debian) ;; *) echo '此发行版暂不支持自动安装。'; return 1;; esac
  aperture_os_suite=$(. /etc/os-release; printf '%s' "${VERSION_CODENAME:-${UBUNTU_CODENAME:-}}")
  aperture_os_arch=$(dpkg --print-architecture)
  aperture_prepare_apt_options "$aperture_os_id" "$aperture_os_suite" "$aperture_os_arch"
  APERTURE_APT=(apt-get)
  if [[ $EUID -ne 0 ]]; then
   if ! command -v sudo >/dev/null; then echo '安装系统依赖需要管理员权限，但没有 sudo。请由管理员提供 sudo 或预装依赖。'; return 1; fi
   echo '需要安装缺少的系统依赖；sudo 可能提示输入你的 Linux 密码。'
   sudo -v
   APERTURE_APT=(sudo --preserve-env=http_proxy,https_proxy,HTTP_PROXY,HTTPS_PROXY,no_proxy,NO_PROXY apt-get)
  fi
  "${APERTURE_APT[@]}" "${APERTURE_APT_OPTIONS[@]}" update
  APERTURE_APT_READY=1
 fi
 # apt preserves distribution package signatures. Never add unverified package sources.
 if [[ $EUID -eq 0 ]]; then
  DEBIAN_FRONTEND=noninteractive "${APERTURE_APT[@]}" "${APERTURE_APT_OPTIONS[@]}" install -y --no-install-recommends "$@"
 else
  sudo --preserve-env=http_proxy,https_proxy,HTTP_PROXY,HTTPS_PROXY,no_proxy,NO_PROXY env DEBIAN_FRONTEND=noninteractive apt-get "${APERTURE_APT_OPTIONS[@]}" install -y --no-install-recommends "$@"
 fi
}
aperture_use_installed_java() {
 local binary major resolved
 for binary in /usr/lib/jvm/*/bin/java; do
  [[ -x "$binary" ]] || continue
  major=$("$binary" -version 2>&1 | sed -nE 's/.*version "([0-9]+).*/\1/p' | head -1)
  if [[ "$major" =~ ^[0-9]+$ && "$major" -ge 21 ]]; then
   resolved=$(readlink -f "$binary")
   aperture_link "${resolved%/bin/java}" "$APERTURE_RUNTIME_DIR/java"
   source "$ROOT/scripts/runtime-env.sh"
   return 0
  fi
 done
 return 1
}
aperture_bootstrap_runtime() {
 mkdir -p "$APERTURE_RUNTIME_DIR" "$ROOT/.run"
 local packages=()
 command -v curl >/dev/null || packages+=(curl)
 [[ -f /etc/ssl/certs/ca-certificates.crt ]] || packages+=(ca-certificates)
 command -v tar >/dev/null || packages+=(tar)
 command -v xz >/dev/null || packages+=(xz-utils)
 command -v sha256sum >/dev/null || packages+=(coreutils)
 command -v setsid >/dev/null || packages+=(util-linux)
 command -v python3 >/dev/null || packages+=(python3 python3-venv)
 if ! aperture_java_ok && ! aperture_use_installed_java; then packages+=(openjdk-21-jdk-headless); fi
 if [[ ${#packages[@]} -gt 0 ]]; then aperture_apt_install "${packages[@]}"; fi
 if ! aperture_java_ok; then aperture_use_installed_java || { echo 'JDK 21 安装后仍不可用。请检查 apt 输出。'; return 1; }; fi
 if ! aperture_python_ok; then
  echo '当前 Python 与项目依赖不兼容，正在为本项目安装 Python 3.12（不替换系统 Python）…'
  if ! python3 -c 'import venv,ensurepip' >/dev/null 2>&1; then aperture_apt_install python3-venv; fi
  if [[ ! -x "$APERTURE_RUNTIME_DIR/uv-bootstrap/bin/python" ]]; then python3 -m venv "$APERTURE_RUNTIME_DIR/uv-bootstrap"; fi
  "$APERTURE_RUNTIME_DIR/uv-bootstrap/bin/python" -m pip install 'uv==0.9.27'
  export UV_PYTHON_INSTALL_DIR="$APERTURE_RUNTIME_DIR/python-installs"
  "$APERTURE_RUNTIME_DIR/uv-bootstrap/bin/uv" python install 3.12 --no-bin
  local python_binary
  python_binary=$("$APERTURE_RUNTIME_DIR/uv-bootstrap/bin/uv" python find --managed-python 3.12)
  aperture_link "$(dirname "$(dirname "$python_binary")")" "$APERTURE_RUNTIME_DIR/python"
  source "$ROOT/scripts/runtime-env.sh"
 fi
 # A distro Python may exist without the separate venv/ensurepip package.
 if ! python3 -c 'import venv,ensurepip' >/dev/null 2>&1; then aperture_apt_install python3-venv; fi
 if ! aperture_node_ok; then
  echo '正在为本项目安装 Node 24（不替换系统 Node）…'
  local arch manifest checksum filename version directory archive
  case "$(uname -m)" in x86_64) arch=x64;; aarch64|arm64) arch=arm64;; *) echo 'Node 自动安装暂不支持此 CPU 架构。'; return 1;; esac
  manifest="$APERTURE_RUNTIME_DIR/node-SHASUMS256.txt"
  curl --fail --location --silent --show-error https://nodejs.org/dist/latest-v24.x/SHASUMS256.txt -o "$manifest"
  read -r checksum filename < <(awk -v arch="$arch" '$2 ~ ("^node-v24\\.[0-9]+\\.[0-9]+-linux-" arch "\\.tar\\.xz$") {print $1,$2;exit}' "$manifest")
  [[ "$checksum" =~ ^[0-9a-f]{64}$ && "$filename" =~ ^node-v24\.[0-9]+\.[0-9]+-linux-(x64|arm64)\.tar\.xz$ ]] || { echo 'Node 官方校验清单格式异常，停止安装。'; return 1; }
  version=${filename%%-linux-*};version=${version#node-}
  archive="$APERTURE_RUNTIME_DIR/$filename"
  curl --fail --location --silent --show-error "https://nodejs.org/dist/$version/$filename" -o "$archive.tmp"
  printf '%s  %s\n' "$checksum" "$archive.tmp" | sha256sum --check --status || { rm -f "$archive.tmp"; echo 'Node SHA256 校验失败，停止安装。'; return 1; }
  mv "$archive.tmp" "$archive"
  tar -xJf "$archive" -C "$APERTURE_RUNTIME_DIR"
  directory=${filename%.tar.xz}
  aperture_link "$directory" "$APERTURE_RUNTIME_DIR/node"
  source "$ROOT/scripts/runtime-env.sh"
 fi
 # Now Python is available: honor .env and external database mode before installing PostgreSQL.
 source "$ROOT/scripts/config.sh"
 if [[ "$MANAGE_POSTGRES" == true && ! -x "$PG_BIN/pg_ctl" ]]; then
  echo '正在安装 PostgreSQL；应用将使用独立的项目数据目录。'
  aperture_apt_install postgresql postgresql-client
  source "$ROOT/scripts/config.sh"
  [[ -x "$PG_BIN/pg_ctl" ]] || { echo 'PostgreSQL 安装后未找到 pg_ctl，请检查 apt 输出。'; return 1; }
 fi
 aperture_java_ok && aperture_node_ok && aperture_python_ok || { echo '基础运行环境验证失败。'; return 1; }
 echo 'Java、Node、Python、PostgreSQL 配置检查完成。'
}
aperture_bootstrap_runtime
