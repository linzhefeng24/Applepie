#!/usr/bin/env bash
# Reuse the existing isolated checkout; never create or reset a worktree.
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT"
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
fetch_checked https://repo.maven.apache.org/maven2/org/scala-sbt/sbt-launch/1.10.7/sbt-launch-1.10.7.jar .tools/sbt-launch.jar 3cca02818047327a83efde776103a1ef92f76f72c062badbbb062499a3270c07
cat > .tools/repositories <<'EOF'
[repositories]
local
maven-central: https://repo.maven.apache.org/maven2
EOF
[[ -d .venv ]] || python3 -m venv .venv
.venv/bin/pip install -r quant/requirements.txt
if [[ "$MANAGE_POSTGRES" == true ]]; then
 "$PG_BIN/postgres" --version
 if [[ ! -f "$PG_DATA_DIR/PG_VERSION" ]]; then
  share=(); [[ -z "$PG_SHARE" ]] || share=(-L "$PG_SHARE")
  "$PG_BIN/initdb" -D "$PG_DATA_DIR" "${share[@]}" --auth-local=trust --auth-host=scram-sha-256 --username="$DB_USER" --no-locale --encoding=UTF8
 fi
 mkdir -p "$PG_SOCKET_DIR"; chmod 700 "$PG_SOCKET_DIR"
 if ! "$PG_BIN/pg_ctl" -D "$PG_DATA_DIR" status >/dev/null 2>&1; then
  "$PG_BIN/pg_ctl" -D "$PG_DATA_DIR" -l "$ROOT/.run/postgres.log" -o "-h $DB_HOST -p $DB_PORT -k '$PG_SOCKET_DIR'" start
 fi
 if [[ -z "${DB_PASSWORD:-}" ]]; then
  "$PYTHON_BIN" scripts/bootstrap-db.py
  source scripts/config.sh
 fi
fi
"$PYTHON_BIN" - <<'PYDB'
import os,psycopg
with psycopg.connect(host=os.environ['DB_HOST'],port=os.environ['DB_PORT'],dbname=os.environ['DB_NAME'],user=os.environ['DB_USER'],password=os.environ.get('DB_PASSWORD','')) as c:
 assert c.execute('SELECT 1').fetchone()==(1,)
print('Configured PostgreSQL connection verified.')
PYDB
if [[ ! -f "$DATA_DIR/daily.csv" ]]; then "$PYTHON_BIN" scripts/prepare_data.py; fi
python3 scripts/check-data.py
npm --prefix frontend ci --no-audit --no-fund
scripts/build-backend.sh
npm --prefix frontend run build
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m unittest discover -s quant/tests -v
echo 'Setup complete. Start services with scripts/start-services.sh.'
