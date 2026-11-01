import numpy as np
from shared.constants import LABELS
from shared.statistics import statistics
from optimization.solver import optimize
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
