# Invocation-local official sources. Does not edit /etc/apt or relax verification.
aperture_write_official_sources() {
 local distro=$1 suite=$2 arch=$3 output=$4 mirror keyring
 [[ "$suite" =~ ^[a-z][a-z0-9-]*$ && "$arch" =~ ^[a-z0-9][a-z0-9-]*$ ]] || { echo '发行版代号或 CPU 架构无效，停止准备软件源。'; return 1; }
 case "$distro" in
 ubuntu)
  keyring=/usr/share/keyrings/ubuntu-archive-keyring.gpg
  case "$arch" in amd64|i386) mirror=http://archive.ubuntu.com/ubuntu;; *) mirror=http://ports.ubuntu.com/ubuntu-ports;; esac
  cat > "$output" <<EOF
Types: deb
URIs: $mirror
Suites: $suite $suite-updates
Components: main universe
Architectures: $arch
Signed-By: $keyring

Types: deb
URIs: $(if [[ "$arch" == amd64 || "$arch" == i386 ]]; then printf '%s' http://security.ubuntu.com/ubuntu; else printf '%s' "$mirror"; fi)
Suites: $suite-security
Components: main universe
Architectures: $arch
Signed-By: $keyring
EOF
  ;;
 debian)
  keyring=/usr/share/keyrings/debian-archive-keyring.gpg
  cat > "$output" <<EOF
Types: deb
URIs: http://deb.debian.org/debian
Suites: $suite $suite-updates
Components: main
Architectures: $arch
Signed-By: $keyring

Types: deb
URIs: http://deb.debian.org/debian-security
Suites: $suite-security
Components: main
Architectures: $arch
Signed-By: $keyring
EOF
  ;;
 *) echo '自动安装仅支持 Ubuntu / Debian。'; return 1;;
 esac
}
aperture_prepare_apt_options() {
 local distro=$1 suite=$2 arch=$3 keyring
 case "$distro" in ubuntu) keyring=/usr/share/keyrings/ubuntu-archive-keyring.gpg;; debian) keyring=/usr/share/keyrings/debian-archive-keyring.gpg;; *) return 1;; esac
 [[ -r "$keyring" ]] || { echo "缺少发行版官方签名 keyring：$keyring；不能安全安装依赖。"; return 1; }
 APERTURE_APT_DIR=$(mktemp -d "${TMPDIR:-/tmp}/aperture-apt.XXXXXXXX")
 chmod 755 "$APERTURE_APT_DIR"
 mkdir -p "$APERTURE_APT_DIR/sources.list.d" "$APERTURE_APT_DIR/lists/partial"
 aperture_write_official_sources "$distro" "$suite" "$arch" "$APERTURE_APT_DIR/official.sources"
 APERTURE_APT_OPTIONS=(
  -o "Dir::Etc::sourcelist=$APERTURE_APT_DIR/official.sources"
  -o "Dir::Etc::sourceparts=$APERTURE_APT_DIR/sources.list.d"
  -o "Dir::State::lists=$APERTURE_APT_DIR/lists"
  -o 'Dir::Cache::pkgcache=' -o 'Dir::Cache::srcpkgcache='
  -o Acquire::AllowInsecureRepositories=false
  -o Acquire::AllowDowngradeToInsecureRepositories=false
  -o APT::Get::AllowUnauthenticated=false
 )
 echo '仅为本次安装使用发行版官方签名源；不改动系统的 Docker、NodeSource 等第三方源。'
}
