#!/usr/bin/env bash
# Reuse the existing isolated checkout; never create or reset a worktree.
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT"
source scripts/runtime-env.sh
source scripts/python-packages.sh
mkdir -p .tools .run
for tool in java node npm python3 curl sha256sum; do command -v "$tool" >/dev/null || { echo "Missing required tool: $tool"; exit 1; }; done
node -e 'if(+process.versions.node.split(".")[0]<24)process.exit(1)' || { echo 'Node 24+ required'; exit 1; }
fetch_checked() {
 local url=$1 dest=$2 hash=$3
 if [[ -f "$dest" ]] && echo "$hash  $dest" | sha256sum --check --status; then return; fi
 curl --fail --location --silent --show-error "$url" -o "$dest.tmp"
 echo "$hash  $dest.tmp" | sha256sum --check --status || { echo "Checksum mismatch: $dest"; rm -f "$dest.tmp"; exit 1; }
 mv "$dest.tmp" "$dest"
}
source scripts/config.sh
# Prefer configured or installed binaries; the verified Debian bundle is only a fallback.
if [[ "$MANAGE_POSTGRES" == true && ! -x "$PG_BIN/pg_ctl" ]]; then
 if ! python3 - <<'PYOS'
import platform
from pathlib import Path
osrelease=Path('/etc/os-release').read_text() if Path('/etc/os-release').exists() else ''
assert platform.machine()=='x86_64' and 'ID=debian' in osrelease and 'VERSION_ID="13"' in osrelease
PYOS
 then echo 'Automatic PostgreSQL download supports Debian 13 x86_64 only. Install PostgreSQL and set PG_BIN, or use MANAGE_POSTGRES=false with an existing server.'; exit 1; fi
 command -v dpkg-deb >/dev/null || { echo 'dpkg-deb required for the Debian fallback'; exit 1; }
 fetch_checked https://deb.debian.org/debian/pool/main/p/postgresql-17/postgresql-17_17.11-0+deb13u1_amd64.deb .tools/pg-server.deb d2ce1ddffafa783f9acda4c92c86fc21e8288bff3782d739294f14fa797d7886
 fetch_checked https://deb.debian.org/debian/pool/main/p/postgresql-17/postgresql-client-17_17.11-0+deb13u1_amd64.deb .tools/pg-client.deb 9d8558f8dd57c8e92e218a20698383575d53742ca3f9e7c2b7fe5f246d5216ae
 dpkg-deb -x .tools/pg-server.deb .tools/pg
 dpkg-deb -x .tools/pg-client.deb .tools/pg
 source scripts/config.sh
fi
need_sbt=true
if [[ ${APERTURE_BUILD_FROM_SOURCE:-0} != 1 ]]; then
 if python3 scripts/backend-runtime.py check; then need_sbt=false; else status=$?; [[ $status -eq 1 ]] || exit "$status"; fi
fi
if [[ "$need_sbt" == true ]]; then
fetch_checked https://repo.maven.apache.org/maven2/org/scala-sbt/sbt-launch/1.10.7/sbt-launch-1.10.7.jar .tools/sbt-launch.jar 3cca02818047327a83efde776103a1ef92f76f72c062badbbb062499a3270c07
cat > .tools/repositories <<'EOF'
[repositories]
local
maven-central: https://repo.maven.apache.org/maven2
EOF
else
 echo '检测到可用的预编译 Scala 运行包，跳过 sbt/Maven 工具下载。'
fi
APERTURE_UV_BIN=$(python3 "$ROOT/scripts/bootstrap-uv.py")
export APERTURE_UV_BIN
python3 scripts/ensure-project-venv.py
echo '[1/6] 安装 Python 数值计算依赖…'
aperture_pip_install "$PYTHON_BIN" -r quant/requirements.txt
if ! "$PYTHON_BIN" -c 'import numpy,scipy,pandas,pyarrow,psycopg' >/dev/null 2>&1; then
 echo '检测到依赖文件缺失，正在重装固定版本依赖…'
 APERTURE_REINSTALL=1 aperture_pip_install "$PYTHON_BIN" -r quant/requirements.txt
 "$PYTHON_BIN" -c 'import numpy,scipy,pandas,pyarrow,psycopg'
fi
echo '[2/6] 初始化并验证数据库与精简行情数据…'
"$PYTHON_BIN" scripts/service-environment.py
if [[ ! -f "$DATA_DIR/daily.csv" ]]; then "$PYTHON_BIN" scripts/prepare_data.py; fi
python3 scripts/check-data.py
python3 scripts/check-minute-data.py
echo '[3/6] 安装前端依赖…'
[[ "$APERTURE_NPM_REGISTRY" == https://* ]] || { echo '项目 npm 软件源必须使用 HTTPS。'; exit 1; }
: > .run/npm-userconfig
: > .run/npm-globalconfig
npm --userconfig "$ROOT/.run/npm-userconfig" --globalconfig "$ROOT/.run/npm-globalconfig" --registry "$APERTURE_NPM_REGISTRY" --strict-ssl=true --prefix frontend ci --no-audit --no-fund
echo '[4/6] 准备 Scala 后端（发布包直接校验；源码版才编译）…'
scripts/build-backend.sh
echo '[5/6] 构建前端页面…'
npm --prefix frontend run build
echo '[6/6] 执行数值与配置检查…'
OPENBLAS_NUM_THREADS=1 "$PYTHON_BIN" -m unittest discover -s quant/tests -v
echo 'Setup complete. Start services with scripts/start-services.sh.'
