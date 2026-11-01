import numpy as np
def statistics(returns):
    r=np.asarray(returns,dtype=float)
    if not len(r): raise ValueError('没有收益观测')
    mu=float(r.mean()); centered=r-mu; m2=float(np.mean(centered**2))
    sd=float(r.std(ddof=1)) if len(r)>1 else 0.
    eq=np.r_[1.,np.cumprod(1+r)]; peaks=np.maximum.accumulate(eq)
    downside=float(np.sqrt(np.mean(np.minimum(r,0)**2)))
    return dict(observations=len(r),totalReturn=float(eq[-1]-1),annualReturn=float(eq[-1]**(252/len(r))-1),volatility=sd*np.sqrt(252),sharpe=mu/sd*np.sqrt(252) if sd else 0.,sortino=mu/downside*np.sqrt(252) if downside else 0.,maxDrawdown=float(np.min(eq/peaks-1)),mean=mu,variance=float(r.var(ddof=1)) if len(r)>1 else 0.,skewness=float(np.mean(centered**3)/m2**1.5) if m2 else 0.,excessKurtosis=float(np.mean(centered**4)/m2**2-3) if m2 else 0.,var95=max(0.,-float(np.quantile(r,.05))))
