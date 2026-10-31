"""Manage only process IDs whose start time, cwd and command match this project's records."""
from pathlib import Path
import os, signal, sys, time
ROOT=Path(__file__).resolve().parents[1]
NAMES={'market','history','statistics','watchlist','reports','optimization','backtest','portfolio','analysis','quant','frontend'}
def identity(pid):
    proc=Path(f'/proc/{pid}')
    stat=(proc/'stat').read_text().rsplit(')',1)[1].split()
    if stat[0]=='Z':return None
    cwd=(proc/'cwd').resolve();cwd.relative_to(ROOT)
    command=(proc/'cmdline').read_bytes().replace(b'\0',b' ').decode(errors='replace')
    return stat[19],command

def owned(name):
    try:
        pid=int((ROOT/f'.run/{name}.pid').read_text());found=identity(pid)
        if found is None:return None
        stamp,command=found;marker=ROOT/f'.run/{name}.started'
        if not marker.exists() or marker.read_text()!=stamp:return None
        match={'quant':'quant/server.py','frontend':'npm'}.get(name,' Main')
        return pid if match in command else None
    except (OSError,ValueError):return None
if __name__=='__main__':
    mode,name=sys.argv[1:3]
    if name not in NAMES:raise SystemExit(2)
    if mode=='record':
        pid=int((ROOT/f'.run/{name}.pid').read_text());found=identity(pid)
        if found is None:raise SystemExit(1)
        (ROOT/f'.run/{name}.started').write_text(found[0])
    elif mode=='alive':raise SystemExit(0 if owned(name) else 1)
    elif mode=='stop':
        pid=owned(name)
        if pid:
            if os.getpgid(pid)==pid:os.killpg(pid,signal.SIGTERM)
            else:os.kill(pid,signal.SIGTERM)
            for _ in range(100):
                if not owned(name):break
                time.sleep(.1)
            else:raise SystemExit(f'{name} did not stop; inspect logs')
        (ROOT/f'.run/{name}.pid').unlink(missing_ok=True);(ROOT/f'.run/{name}.started').unlink(missing_ok=True)
