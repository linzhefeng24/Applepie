"""Verify compressed minute inputs without loading the database or decompressing all records."""
from pathlib import Path
import hashlib,json,re
from settings import read_settings
root=Path(read_settings()['DATA_DIR']);directory=root/'minutes';manifest=directory/'manifest.json'
if not manifest.exists():print('未配置分钟输入；仅日线及更粗频率可用。');raise SystemExit(0)
report=json.loads(manifest.read_text());provenance=json.loads((root/'provenance.json').read_text())
if report['sourceSha256']!=provenance['sha256']:raise SystemExit('分钟数据与日线的原始来源校验和不一致。')
for entry in report['symbols']:
 if not re.fullmatch(r'[A-Z][A-Z0-9-]{0,14}',entry['symbol']) or entry['file']!=entry['symbol']+'.csv.gz':raise SystemExit('分钟数据文件名无效。')
 with (directory/entry['file']).open('rb') as file:
  if hashlib.file_digest(file,'sha256').hexdigest()!=entry['sha256']:raise SystemExit('分钟数据文件损坏：'+entry['symbol'])
print(f"Verified {len(report['symbols'])} minute inputs / {report['rows']} source observations; compressed SHA256 checks passed.")
