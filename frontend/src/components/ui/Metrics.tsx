import type { Metrics as M } from "../../objects/market";
import { number, percent } from "../../utils/format";
export function Metric({
  label,
  value,
  note,
  positive,
}: {
  label: string;
  value: string;
  note?: string;
  positive?: boolean;
}) {
  return (
    <div className="min-w-0 rounded border border-white/[.08] bg-[#111823] p-3">
      <div className="text-[11px] text-slate-400">{label}</div>
      <div
        className={`mt-2 font-mono text-xl tracking-tight ${positive === undefined ? "text-slate-100" : positive ? "text-[#55c9a3]" : "text-rose-300"}`}
      >
        {value}
      </div>
      {note && <div className="mt-2 text-[10px] text-slate-500">{note}</div>}
    </div>
  );
}
export function Metrics({
  data,
  backtest = false,
}: {
  data: M;
  backtest?: boolean;
}) {
  return (
    <div className="grid grid-cols-2 gap-3 xl:grid-cols-4">
      <Metric
        label={backtest ? "样本外年化收益" : "区间年化收益"}
        value={percent(data.annualReturn)}
        positive={data.annualReturn >= 0}
        note="价格收益 · 252 期年化"
      />
      <Metric
        label="年化波动率"
        value={percent(data.volatility)}
        note={`${data.observations} 个收益观测`}
      />
      <Metric
        label="Sharpe 比率"
        value={number(data.sharpe)}
        note="无风险利率设为 0"
      />
      <Metric
        label="最大回撤"
        value={percent(data.maxDrawdown)}
        positive={false}
        note="从历史高点的最大下跌"
      />
    </div>
  );
}
