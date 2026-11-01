"""Verified source minutes -> deterministic, compressed per-symbol database inputs."""
from pathlib import Path
import argparse,gzip,hashlib,io,json,os,tempfile,zipfile
import pandas as pd
from prepare_data import SYMBOLS,SHA
from clean_minutes import clean_minutes
from settings import read_settings

def prepare(archive,destination,sessions=60):
    archive=Path(archive);out=Path(destination)/'minutes';out.mkdir(parents=True,exist_ok=True)
    with archive.open('rb') as stream:assert hashlib.file_digest(stream,'sha256').hexdigest()==SHA,'Release SHA256 mismatch'
    entries=[]
    with zipfile.ZipFile(archive) as source:
        for symbol in SYMBOLS:
            frame,duplicates,rejected=clean_minutes(pd.read_parquet(io.BytesIO(source.read(f'part1/{symbol}_clean_1min.parquet'))))
            dates=frame.datetime.dt.strftime('%Y-%m-%d')
            if sessions:frame=frame[dates.isin(sorted(dates.unique())[-sessions:])].copy()
            records=frame.rename(columns=dict(datetime='time',Open='open',High='high',Low='low',Close='close',Volume='volume'))
            records['time']=records.time.dt.strftime('%Y-%m-%d %H:%M:%S');records.insert(0,'symbol',symbol)
            target=out/f'{symbol}.csv.gz';temporary=target.with_suffix('.tmp')
            with temporary.open('wb') as raw,gzip.GzipFile(fileobj=raw,mode='wb',filename='',mtime=0) as compressed,io.TextIOWrapper(compressed,encoding='utf8',newline='') as text:
                records[['symbol','time','open','high','low','close','volume']].to_csv(text,index=False)
            os.replace(temporary,target)
            with target.open('rb') as stream:checksum=hashlib.file_digest(stream,'sha256').hexdigest()
            entries.append(dict(symbol=symbol,file=target.name,sha256=checksum,rows=len(records),start=records.time.iloc[0],end=records.time.iloc[-1],duplicates=duplicates,rejected=rejected))
            print(symbol,len(records),entries[-1]['start'],'—',entries[-1]['end'],flush=True)
    manifest=dict(sourceSha256=SHA,sourceResolution='1min',timezone='source timestamps have no timezone; retained without conversion',selection='all available minutes' if not sessions else f'latest {sessions} recorded sessions per symbol',symbols=entries,rows=sum(e['rows'] for e in entries))
    (out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    print('Minute rows:',manifest['rows'],'compressed MiB:',round(sum(p.stat().st_size for p in out.glob('*.gz'))/1024**2,1))
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--archive',type=Path,required=True);parser.add_argument('--all',action='store_true');parser.add_argument('--sessions',type=int,default=60);parser.add_argument('--data-dir',type=Path,default=Path(read_settings()['DATA_DIR']));args=parser.parse_args()
    assert args.sessions>0,'sessions must be positive';prepare(args.archive,args.data_dir,None if args.all else args.sessions)
