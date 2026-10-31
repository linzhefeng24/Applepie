import type { Parameters } from "../../objects/analysis";
import { useMarket, setSymbols } from "../../stores/research";
import { Panel } from "../../components/ui/Panel";
import { modelNames } from "../../utils/format";
export function ParameterForm({
  parameters: p,
  update,
  backtest = false,
  running,
  onRun,
}: {
  parameters: Parameters;
  update: <K extends keyof Omit<Parameters, "symbols">>(
    key: K,
    value: Parameters[K],
  ) => void;
  backtest?: boolean;
  running: boolean;
  onRun: () => void;
}) {
  const market = useMarket()!;
  const invalid =
    p.symbols.length < 2 ||
    p.symbols.length > 10 ||
    p.maxWeight * p.symbols.length < 1 - 1e-9 ||
    !p.start ||
    !p.end ||
    p.start >= p.end;
  return (
    <Panel title="实验参数" subtitle="固定输入，让每次研究可复现">
      <div className="space-y-5 px-5 pb-5">
        <div>
          <div className="mb-2 flex justify-between text-[11px] text-slate-400">
            <span>标的池</span>
            <span className="font-mono">{p.symbols.length} / 10</span>
          </div>
          <div className="flex max-h-52 flex-wrap gap-1.5 overflow-y-auto">
            {market.stocks.map((s) => (
              <button
                key={s.symbol}
                title={s.name}
                aria-pressed={p.symbols.includes(s.symbol)}
                disabled={
                  !p.symbols.includes(s.symbol) && p.symbols.length >= 10
                }
                onClick={() =>
                  setSymbols(
                    p.symbols.includes(s.symbol)
                      ? p.symbols.filter((x) => x !== s.symbol)
                      : [...p.symbols, s.symbol],
                  )
                }
                className={`rounded-md border px-2 py-1.5 font-mono text-[10px] ${p.symbols.includes(s.symbol) ? "border-[#b7ed77]/40 bg-[#b7ed77]/10 text-[#b7ed77]" : "border-white/5 bg-white/[.02] text-slate-500 hover:border-white/20"}`}
              >
                {s.symbol}
              </button>
            ))}
          </div>
        </div>
        <div className="grid grid-cols-1 gap-3">
          <label className="field">
            估计 / 回测数据起点
            <input
              type="date"
              aria-label="实验开始日期"
              value={p.start}
              onChange={(e) => update("start", e.target.value)}
            />
          </label>
          <label className="field">
            数据截止日期
            <input
              type="date"
              aria-label="实验结束日期"
              value={p.end}
              onChange={(e) => update("end", e.target.value)}
            />
          </label>
        </div>
        <div className="space-y-3 border-t border-white/[.07] pt-4">
          <div className="text-[10px] tracking-widest text-slate-500">
            CONSTRAINTS / 不卖空
          </div>
          <label className="field">
            单标的权重上限{" "}
            <span className="float-right font-mono text-[#b7ed77]">
              {Math.round(p.maxWeight * 100)}%
            </span>
            <input
              aria-label="单标的权重上限"
              type="range"
              min="0.1"
              max="1"
              step="0.05"
              value={p.maxWeight}
              onChange={(e) => update("maxWeight", +e.target.value)}
              className="w-full accent-[#b7ed77]"
            />
          </label>
          {p.maxWeight * p.symbols.length < 1 - 1e-9 && (
            <p className="text-[10px] text-rose-300">
              上限 × 标的数必须 ≥ 100%。
            </p>
          )}
          <div className="grid grid-cols-3 gap-2">
            {(
              [
                ["riskAversion", "方差 λ₂"],
                ["skewPreference", "偏度 λ₃"],
                ["kurtosisAversion", "峰度 λ₄"],
              ] as const
            ).map(([key, label]) => (
              <label className="field" key={key}>
                {label}
                <input
                  aria-label={label}
                  type="number"
                  min="0"
                  max={key === "riskAversion" ? 100 : 20}
                  step="0.5"
                  value={p[key]}
                  onChange={(e) => update(key, +e.target.value)}
                />
              </label>
            ))}
          </div>
        </div>
        {backtest && (
          <div className="space-y-3 border-t border-white/[.07] pt-4">
            <label className="field">
              主策略
              <select
                aria-label="主策略"
                value={p.model}
                onChange={(e) =>
                  update("model", e.target.value as Parameters["model"])
                }
              >
                {Object.entries(modelNames).map(([k, v]) => (
                  <option key={k} value={k}>
                    {v}
                  </option>
                ))}
              </select>
            </label>
            <div className="grid grid-cols-2 gap-2">
              <label className="field">
                滚动窗口 / 日
                <input
                  aria-label="滚动窗口"
                  type="number"
                  min="60"
                  max="504"
                  value={p.lookback}
                  onChange={(e) => update("lookback", +e.target.value)}
                />
              </label>
              <label className="field">
                调仓间隔 / 日
                <input
                  aria-label="调仓间隔"
                  type="number"
                  min="5"
                  max="126"
                  value={p.rebalance}
                  onChange={(e) => update("rebalance", +e.target.value)}
                />
              </label>
            </div>
            <label className="field">
              单边交易费 / bps
              <input
                aria-label="单边交易费"
                type="number"
                min="0"
                max="100"
                value={p.costBps}
                onChange={(e) => update("costBps", +e.target.value)}
              />
            </label>
            <p className="text-[10px] leading-5 text-slate-600">
              1 bps = 0.01%。信号截止至执行日前一个收盘，不使用未来数据。
            </p>
          </div>
        )}
        <button
          className="btn-primary w-full"
          disabled={invalid || running}
          onClick={onRun}
        >
          {running
            ? "计算中，请稍候…"
            : backtest
              ? "运行样本外回测 →"
              : "运行五模型分析 →"}
        </button>
        <p className="text-[10px] leading-5 text-slate-600">
          全部参数保存在结果快照中。更改参数后需重新运行才会更新结果。
        </p>
      </div>
    </Panel>
  );
}
