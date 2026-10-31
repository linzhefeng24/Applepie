#!/usr/bin/env bash
# Reuse the existing isolated checkout; never create or reset a worktree.
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT"
mkdir -p .tools .run
for tool in java node npm python3 curl sha256sum dpkg-deb; do command -v "$tool" >/dev/null || { echo "Missing required tool: $tool"; exit 1; }; done
node -e 'if(+process.versions.node.split(".")[0]<24)process.exit(1)' || { echo 'Node 24+ required'; exit 1; }
fetch_checked() {
 local url=$1 dest=$2 hash=$3
 if [[ -f "$dest" ]] && echo "$hash  $dest" | sha256sum --check --status; then return; fi
 curl --fail --location --silent --show-error "$url" -o "$dest.tmp"
 echo "$hash  $dest.tmp" | sha256sum --check --status || { echo "Checksum mismatch: $dest"; rm -f "$dest.tmp"; exit 1; }
 mv "$dest.tmp" "$dest"
}
# Checksums were verified against signed Debian trixie Release metadata during onboarding.
PG="$ROOT/.tools/pg/usr/lib/postgresql/17/bin"
if [[ ! -x "$PG/postgres" ]]; then
 fetch_checked https://deb.debian.org/debian/pool/main/p/postgresql-17/postgresql-17_17.11-0+deb13u1_amd64.deb .tools/pg-server.deb d2ce1ddffafa783f9acda4c92c86fc21e8288bff3782d739294f14fa797d7886
 fetch_checked https://deb.debian.org/debian/pool/main/p/postgresql-17/postgresql-client-17_17.11-0+deb13u1_amd64.deb .tools/pg-client.deb 9d8558f8dd57c8e92e218a20698383575d53742ca3f9e7c2b7fe5f246d5216ae
 dpkg-deb -x .tools/pg-server.deb .tools/pg
 dpkg-deb -x .tools/pg-client.deb .tools/pg
fi
"$PG/postgres" --version
fetch_checked https://repo.maven.apache.org/maven2/org/scala-sbt/sbt-launch/1.10.7/sbt-launch-1.10.7.jar .tools/sbt-launch.jar 3cca02818047327a83efde776103a1ef92f76f72c062badbbb062499a3270c07
cat > .tools/repositories <<'EOF'
[repositories]
local
maven-central: https://repo.maven.apache.org/maven2
EOF
[[ -d .venv ]] || python3 -m venv .venv
.venv/bin/pip install -r quant/requirements.txt
if [[ ! -f data/pg/PG_VERSION ]]; then
 "$PG/initdb" -D data/pg -L "$ROOT/.tools/pg/usr/share/postgresql/17" --auth-local=trust --auth-host=scram-sha-256 --username=terminal --no-locale --encoding=UTF8
fi
if ! "$PG/pg_ctl" -D data/pg status >/dev/null 2>&1; then
 "$PG/pg_ctl" -D data/pg -l .run/postgres.log -o "-h 127.0.0.1 -p 55432 -k $ROOT/.run" start
fi
if [[ ! -f .env ]]; then
 .venv/bin/python - <<'PY'
from pathlib import Path
import secrets,psycopg
from psycopg import sql
root=Path.cwd();password=secrets.token_hex(24)
with psycopg.connect(host=str(root/'.run'),port=55432,user='terminal',dbname='postgres',autocommit=True) as c:
 c.execute(sql.SQL('ALTER ROLE terminal PASSWORD {}').format(sql.Literal(password)))
 if not c.execute("SELECT 1 FROM pg_database WHERE datname='terminal'").fetchone():c.execute('CREATE DATABASE terminal')
p=Path('.env');p.write_text('DB_HOST=127.0.0.1\nDB_PORT=55432\nDB_NAME=terminal\nDB_USER=terminal\nDB_PASSWORD='+password+'\n');p.chmod(0o600)
print('Created local, ignored PostgreSQL configuration; no external credentials required.')
PY
fi
if [[ ! -f data/daily.csv ]]; then .venv/bin/python scripts/prepare_data.py; fi
python3 scripts/check-data.py
npm --prefix frontend ci --no-audit --no-fund
scripts/build-backend.sh
npm --prefix frontend run build
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m unittest discover -s quant/tests -v
echo 'Setup complete. Start services with scripts/start-services.sh.'
