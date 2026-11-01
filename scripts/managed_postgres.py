"""Verify the recorded postmaster before trusting pg_ctl or sending a signal."""
from pathlib import Path
import time

def postmaster_state(cluster, proc=Path('/proc')):
    marker=Path(cluster)/'postmaster.pid'
    try:
        pid=int(marker.read_text().splitlines()[0])
        if pid<=1:return 'unknown'
    except FileNotFoundError:return 'stopped'
    except (OSError,ValueError,IndexError):return 'unknown'
    try:args=(proc/str(pid)/'cmdline').read_bytes().split(b'\0')
    except FileNotFoundError:return 'stale'
    except OSError:return 'unknown'
    values=[a.decode(errors='replace') for a in args if a]
    if not values:return 'stale'
    if Path(values[0]).name!='postgres':return 'stale'
    try:directory=values[values.index('-D')+1]
    except (ValueError,IndexError):return 'unknown'
    return 'running' if Path(directory).resolve()==Path(cluster).resolve() else 'stale'

def archive_stale_pid(cluster):
    marker=Path(cluster)/'postmaster.pid'
    if postmaster_state(cluster)!='stale':return False
    # Preserve diagnostics; never signal the unrelated process whose PID was reused.
    marker.rename(marker.with_name('postmaster.pid.stale-'+str(time.time_ns())))
    return True

def connect_ready(connect,parameters,attempts=12,pause=.5):
    for attempt in range(attempts):
        try:return connect(**parameters,connect_timeout=2)
        except Exception as error:
            # Authentication, permissions and SQL/configuration errors are not readiness races.
            state=getattr(error,'sqlstate',None)
            if state!='57P03' and (state or 'connection refused' not in str(error).lower()):raise
            if attempt==attempts-1:raise
            time.sleep(pause)

def diagnostics(name,log):
    try:lines=Path(log).read_text(errors='replace').splitlines()[-35:]
    except OSError:lines=['（尚无该数据库的启动日志）']
    return f'数据库 {name} 启动或连接失败；日志：{log}\n'+'\n'.join(lines)
