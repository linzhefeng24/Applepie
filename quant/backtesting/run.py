from shared.constants import WARNINGS
from shared.validation import validate
from shared.alignment import align
from backtesting.simulation import simulate
def backtest(payload):
    p=payload['parameters'];validate(p);dates,r,dropped=align(payload['series'],p['symbols'])
    if len(r)<p['lookback']+22: raise ValueError('共同历史不足以完成估计窗口及至少 21 个样本外交易日，请扩大区间或缩短窗口')
    models=list(dict.fromkeys([p['model'],'equal','minvariance','meanvariance']))
    results=[simulate(r,dates,m,p) for m in models]
    return dict(symbols=p['symbols'],start=results[0]['curve'][0]['date'],end=dates[-1],results=results,droppedSessions=dropped,warnings=WARNINGS+['回测只使用价格收益；未建模分红、税、冲击、滑点、退市和成交限制。','仅做教学研究，不用于实盘下单。'],methodology='滚动估计窗口固定，信号滞后一整个收盘：估计截止于执行日前一个共同价格日期，在下一收盘执行，随后才计入持仓收益。权重随价格漂移；每次调仓按 Σ|目标权重−漂移权重|×单边费率扣费，首次建仓从现金计费，期末不清仓。对照组使用相同区间、成本及调仓日。',alignment='仅使用共同价格日期；无填充。基准是等权样本组合，并非市场指数。')
