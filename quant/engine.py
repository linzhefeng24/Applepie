"""Pure numerical functions: deterministic estimation and lagged, self-financing backtests."""
from __future__ import annotations
import numpy as np
from scipy.optimize import minimize
MODELS = ('equal', 'minvariance', 'meanvariance', 'mvsk', 'riskparity')
LABELS = dict(equal='等权组合', minvariance='最小方差', meanvariance='均值—方差', mvsk='MVSK', riskparity='风险平价')
WARNINGS = ['数据为用户提供的历史价格，复权方式未知；结果不含分红，不等于总收益。', '成交量来自源分钟记录，不能作为全市场成交量。', '32 个标的是人为精选样本，存在选择偏差；历史结果不代表未来表现。']
def validate(p):
    symbols=p['symbols']; n=len(symbols)
    if not 2 <= n <= 10 or len(set(symbols)) != n: raise ValueError('选择 2–10 个不重复标的')
    for key,lo,hi in [('maxWeight',1/n,1),('riskAversion',0,100),('skewPreference',0,20),('kurtosisAversion',0,20),('costBps',0,100),('lookback',60,504),('rebalance',5,126)]:
        x=p[key]
        if not isinstance(x,(int,float)) or not np.isfinite(x) or not lo-1e-9 <= x <= hi: raise ValueError(f'{key} 超出允许范围 [{lo:.3g}, {hi}]')
    if int(p['lookback'])!=p['lookback'] or int(p['rebalance'])!=p['rebalance']: raise ValueError('窗口和调仓间隔必须是整数')
    if p['model'] not in MODELS: raise ValueError('不支持的模型')
def align(series, symbols):
    maps={s:{b['date']:float(b['close']) for b in series[s]} for s in symbols}
    dates=sorted(set.intersection(*(set(maps[s]) for s in symbols)))
    if len(dates)<61: raise ValueError('共同历史不足 61 个价格观测，请扩大日期范围或减少标的')
    close=np.array([[maps[s][d] for s in symbols] for d in dates],dtype=float)
    if not np.isfinite(close).all() or (close<=0).any(): raise ValueError('行情价格无效')
    returns=close[1:]/close[:-1]-1
    dropped={s:len(maps[s])-len(dates) for s in symbols}
    return dates,returns,dropped

def statistics(returns):
    r=np.asarray(returns,dtype=float)
    if not len(r): raise ValueError('没有收益观测')
    mu=float(r.mean()); centered=r-mu; m2=float(np.mean(centered**2))
    sd=float(r.std(ddof=1)) if len(r)>1 else 0.
    eq=np.r_[1.,np.cumprod(1+r)]; peaks=np.maximum.accumulate(eq)
    downside=float(np.sqrt(np.mean(np.minimum(r,0)**2)))
    return dict(observations=len(r),totalReturn=float(eq[-1]-1),annualReturn=float(eq[-1]**(252/len(r))-1),volatility=sd*np.sqrt(252),sharpe=mu/sd*np.sqrt(252) if sd else 0.,sortino=mu/downside*np.sqrt(252) if downside else 0.,maxDrawdown=float(np.min(eq/peaks-1)),mean=mu,variance=float(r.var(ddof=1)) if len(r)>1 else 0.,skewness=float(np.mean(centered**3)/m2**1.5) if m2 else 0.,excessKurtosis=float(np.mean(centered**4)/m2**2-3) if m2 else 0.,var95=max(0.,-float(np.quantile(r,.05))))

def capped_simplex(values, cap):
    """Euclidean projection, avoiding infeasible optimizer starting points."""
    v=np.asarray(values); lo=float(v.min()-cap);hi=float(v.max())
    for _ in range(80):
        mid=(lo+hi)/2
        if np.clip(v-mid,0,cap).sum()>1: lo=mid
        else: hi=mid
    return np.clip(v-(lo+hi)/2,0,cap)

def objective(w, r, model, p):
    mu=r.mean(axis=0); cov=np.atleast_2d(np.cov(r,rowvar=False))
    if model=='minvariance': return float(w@cov@w*252)
    if model=='meanvariance': return float(-w@mu*252+p['riskAversion']*(w@cov@w)*252/2)
    if model=='riskparity':
        rc=w*(cov@w); variance=float(rc.sum())
        return float(np.sum((rc/max(variance,1e-16)-1/len(w))**2))
    # Fixed, weight-independent scale makes daily central moments comparable.
    scale=max(float(r.std(axis=0,ddof=1).mean()),1e-8)
    z=(r@w)/scale; mean=float(z.mean());c=z-mean
    return -mean+p['riskAversion']*np.mean(c**2)/2-p['skewPreference']*np.mean(c**3)/6+p['kurtosisAversion']*np.mean(c**4)/24

def optimize(r,model,p):
    n=r.shape[1];cap=float(p['maxWeight']);equal=np.ones(n)/n
    if model=='equal': return dict(weights=equal.tolist(),converged=True,message='解析等权解',iterations=0,objective=0.)
    rng=np.random.default_rng(42)
    starts=[equal]+[capped_simplex(rng.dirichlet(np.ones(n)),cap) for _ in range(2)]
    solutions=[minimize(objective,w,args=(r,model,p),method='SLSQP',bounds=[(0,cap)]*n,constraints=[dict(type='eq',fun=lambda x: x.sum()-1)],options=dict(maxiter=250,ftol=1e-10)) for w in starts]
    feasible=[s for s in solutions if np.isfinite(s.fun) and abs(s.x.sum()-1)<1e-6 and s.x.min()>=-1e-7 and s.x.max()<=cap+1e-7]
    good=[s for s in feasible if s.success]
    if not good:
        return dict(weights=equal.tolist(),converged=False,message='求解未收敛，回退等权持仓',iterations=sum(int(s.nit) for s in solutions),objective=float(objective(equal,r,model,p)))
    best=min(good,key=lambda s:s.fun)
    weights=capped_simplex(best.x,cap)
    return dict(weights=weights.tolist(),converged=True,message=str(best.message),iterations=int(best.nit),objective=float(best.fun))

def analyze(payload):
    p=payload['parameters'];validate(p);symbols=p['symbols'];dates,r,dropped=align(payload['series'],symbols)
    models=[]
    for model in MODELS:
        solved=optimize(r,model,p);pr=r@np.array(solved['weights']);counts,edges=np.histogram(pr,bins=24)
        models.append(dict(model=model,label=LABELS[model],**solved,metrics=statistics(pr),histogram=dict(edges=edges.tolist(),counts=counts.tolist())))
    corr=np.corrcoef(r,rowvar=False)
    corr=np.nan_to_num(corr,nan=0.).tolist()
    return dict(symbols=symbols,start=dates[0],end=dates[-1],sessions=len(dates),models=models,correlation=corr,droppedSessions=dropped,warnings=WARNINGS+['实验室指标是估计区间内每日恒定权重的毛收益描述，不是样本外回测。','高阶矩和最优权重对样本敏感；MVSK 为非凸优化，多起点不保证全局最优。'],methodology='MVSK 最小化 -E[z]+λ₂μ₂(z)/2-λ₃μ₃(z)/6+λ₄μ₄(z)/24；z=(组合日收益)/(样本中个股日波动率均值)。偏度、超额峰度用组合收益计算；波动率用样本标准差；Sharpe 无风险利率=0；252期年化。',alignment='仅使用共同价格日期，不插值、不前向填充；缺失日期会使某个收益间隔跨越多交易日。')

def simulate(r, dates, model, p):
    lookback=int(p['lookback']);every=int(p['rebalance']);fee=p['costBps']/10000
    first=lookback+1;w=np.zeros(r.shape[1]);net=[];trades=[];equity=1.;curve=[dict(date=dates[first],value=1.,drawdown=0.)];peak=1.
    for t in range(first,len(r)):
        cost=0.
        if (t-first)%every==0:
            # One close of signal lag: latest estimation return ends at prices[t-1],
            # execute at prices[t], then earn prices[t+1]/prices[t]-1.
            sample=r[t-lookback-1:t-1];solution=optimize(sample,model,p);target=np.array(solution['weights'])
            turnover=float(np.abs(target-w).sum());cost=fee*turnover;w=target
            trades.append(dict(executionDate=dates[t],signalEnd=dates[t-1],estimateStart=dates[t-lookback-1],returnDate=dates[t+1],weights=w.tolist(),turnover=turnover,cost=cost,converged=solution['converged']))
        gross=float(w@r[t]);daily=(1-cost)*(1+gross)-1;net.append(daily);equity*=1+daily;peak=max(peak,equity)
        curve.append(dict(date=dates[t+1],value=equity,drawdown=equity/peak-1))
        w=w*(1+r[t])/(1+gross)
    return dict(model=model,label=LABELS[model],metrics=statistics(net),curve=curve,trades=trades,totalTurnover=sum(x['turnover'] for x in trades),tradingCostRateSum=sum(x['cost'] for x in trades),failedRebalances=sum(not x['converged'] for x in trades))

def backtest(payload):
    p=payload['parameters'];validate(p);dates,r,dropped=align(payload['series'],p['symbols'])
    if len(r)<p['lookback']+22: raise ValueError('共同历史不足以完成估计窗口及至少 21 个样本外交易日，请扩大区间或缩短窗口')
    models=list(dict.fromkeys([p['model'],'equal','minvariance','meanvariance']))
    results=[simulate(r,dates,m,p) for m in models]
    return dict(symbols=p['symbols'],start=results[0]['curve'][0]['date'],end=dates[-1],results=results,droppedSessions=dropped,warnings=WARNINGS+['回测只使用价格收益；未建模分红、税、冲击、滑点、退市和成交限制。','仅做教学研究，不用于实盘下单。'],methodology='滚动估计窗口固定，信号滞后一整个收盘：估计截止于执行日前一个共同价格日期，在下一收盘执行，随后才计入持仓收益。权重随价格漂移；每次调仓按 Σ|目标权重−漂移权重|×单边费率扣费，首次建仓从现金计费，期末不清仓。对照组使用相同区间、成本及调仓日。',alignment='仅使用共同价格日期；无填充。基准是等权样本组合，并非市场指数。')
