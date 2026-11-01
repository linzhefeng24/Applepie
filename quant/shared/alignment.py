import numpy as np
def align(series, symbols):
    maps={s:{b['date']:float(b['close']) for b in series[s]} for s in symbols}
    dates=sorted(set.intersection(*(set(maps[s]) for s in symbols)))
    if len(dates)<61: raise ValueError('共同历史不足 61 个价格观测，请扩大日期范围或减少标的')
    close=np.array([[maps[s][d] for s in symbols] for d in dates],dtype=float)
    if not np.isfinite(close).all() or (close<=0).any(): raise ValueError('行情价格无效')
    returns=close[1:]/close[:-1]-1
    dropped={s:len(maps[s])-len(dates) for s in symbols}
    return dates,returns,dropped
