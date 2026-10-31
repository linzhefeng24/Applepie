#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
args=(-XX:ActiveProcessorCount=4 -Xmx2G "-Duser.home=$ROOT/.tools/home" -Dsbt.override.build.repos=true "-Dsbt.repository.config=$ROOT/.tools/repositories")
if [[ -n "${HTTPS_PROXY:-}" ]]; then
 read -r proxy_host proxy_port < <(python3 -c 'import os,urllib.parse;u=urllib.parse.urlparse(os.environ["HTTPS_PROXY"]);print(u.hostname,u.port or 80)')
 args+=("-Dhttps.proxyHost=$proxy_host" "-Dhttps.proxyPort=$proxy_port" "-Dhttp.proxyHost=$proxy_host" "-Dhttp.proxyPort=$proxy_port")
fi
cd "$ROOT/backend"
exec java "${args[@]}" -jar "$ROOT/.tools/sbt-launch.jar" "$@"
