"""Export one independently runnable service, without other business implementations or credentials."""
from pathlib import Path
import importlib.util,json,sys,zipfile
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('runtime',ROOT/'scripts/backend-runtime.py');runtime=importlib.util.module_from_spec(spec);spec.loader.exec_module(runtime)
if not runtime.validated(ROOT):raise SystemExit('Build and pack the runtime first')
name=sys.argv[1];manifest=json.loads((ROOT/'backend/runtime/manifest.json').read_text());entry=manifest['services'][name]
out=Path(sys.argv[2]) if len(sys.argv)>2 else ROOT/'.run'/f'aperture-{name}.zip'
launcher='''#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "$0")" && pwd)
cd "$ROOT"
exec java -XX:ActiveProcessorCount=2 -Xmx128m -cp "'''+':'.join(entry['classpath'])+'" '+entry['mainClass']+'\n'
registry=json.loads((ROOT/'config/services.json').read_text());service=next(s for s in registry if s['name']==name)
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
 for relative in entry['classpath']:z.write(ROOT/'backend/runtime'/relative,relative)
 info=zipfile.ZipInfo('run.sh');info.external_attr=0o100755<<16;z.writestr(info,launcher)
 z.writestr('service.json',json.dumps(service,indent=2))
 z.writestr('README.txt',f'''APERTURE {name}: standalone JDK 21 service.
Set SERVICE={name}, HTTP_PORT={service['port']}, SERVICE_HOST=127.0.0.1,
DATABASE_REQUIRED={str(service['database']).lower()}, INTERNAL_SERVICE_TOKEN (your own >=32-character random token),
TRUSTED_SERVICE_HASHES (JSON caller name -> SHA256 hex digest),
and dependency URLs such as SESSIONS_URL, AUTHORIZATION_URL, ACCOUNTS_URL.
Database owners additionally need DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD.
Reference-data owners need DATA_DIR pointing to verified course data files.
Export these variables, then bash run.sh. No .env parser, credentials or other business service JARs are included.
GET /health; GET /api/{name}/openapi.json.
''')
print(out)
