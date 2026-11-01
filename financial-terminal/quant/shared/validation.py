import numpy as np
from shared.constants import MODELS
def validate(p):
    symbols=p['symbols']; n=len(symbols)
    if not 2 <= n <= 10 or len(set(symbols)) != n: raise ValueError('选择 2–10 个不重复标的')
    for key,lo,hi in [('maxWeight',1/n,1),('riskAversion',0,100),('skewPreference',0,20),('kurtosisAversion',0,20),('costBps',0,100),('lookback',60,504),('rebalance',5,126)]:
        x=p[key]
        if not isinstance(x,(int,float)) or not np.isfinite(x) or not lo-1e-9 <= x <= hi: raise ValueError(f'{key} 超出允许范围 [{lo:.3g}, {hi}]')
    if int(p['lookback'])!=p['lookback'] or int(p['rebalance'])!=p['rebalance']: raise ValueError('窗口和调仓间隔必须是整数')
    if p['model'] not in MODELS: raise ValueError('不支持的模型')
