import numpy as np
from shared.constants import MODELS,LABELS,WARNINGS
from shared.validation import validate
from shared.alignment import align
from shared.statistics import statistics
from optimization.solver import optimize
def analyze(payload):
    p=payload['parameters'];validate(p);symbols=p['symbols'];dates,r,dropped=align(payload['series'],symbols)
    models=[]
    for model in MODELS:
        solved=optimize(r,model,p);pr=r@np.array(solved['weights']);counts,edges=np.histogram(pr,bins=24)
        models.append(dict(model=model,label=LABELS[model],**solved,metrics=statistics(pr),histogram=dict(edges=edges.tolist(),counts=counts.tolist())))
    corr=np.corrcoef(r,rowvar=False)
    corr=np.nan_to_num(corr,nan=0.).tolist()
    return dict(symbols=symbols,start=dates[0],end=dates[-1],sessions=len(dates),models=models,correlation=corr,droppedSessions=dropped,warnings=WARNINGS+['组合分析指标是估计区间内每日恒定权重的毛收益描述，不是样本外回测。','高阶矩和最优权重对样本敏感；MVSK 为非凸优化，多起点不保证全局最优。'],methodology='MVSK 最小化 -E[z]+λ₂μ₂(z)/2-λ₃μ₃(z)/6+λ₄μ₄(z)/24；z=(组合日收益)/(样本中个股日波动率均值)。偏度、超额峰度用组合收益计算；波动率用样本标准差；Sharpe 无风险利率=0；252期年化。',alignment='仅使用共同价格日期，不插值、不前向填充；缺失日期会使某个收益间隔跨越多交易日。')
