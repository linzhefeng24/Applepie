import { useMemo, useState } from "react";
import { usePriceSelection } from "../shared/hooks/usePriceSelection";
import { SelectionBar } from "../shared/SelectionBar";
import { alignPrices, portfolioRisk } from "../shared/functions/portfolio";
import { Chart, axis } from "../../components/ui/Chart";
import { ErrorBox, Loading, Empty } from "../../components/ui/Panel";
import { percent } from "../../utils/format";
import { download } from "../../utils/download";
export function RiskPage() {
  const [symbols, setSymbols] = useState(["AAPL", "GOOG", "GLD"]),
    [start, setStart] = useState("2023-01-01"),
    [end, setEnd] = useState("2026-10-23"),
    [weights, setWeights] = useState<Record<string, number>>({
      AAPL: 40,
      GOOG: 30,
      GLD: 30,
    });
  const state = usePriceSelection(symbols, start, end);
  const aligned = useMemo(
    () => alignPrices(state.data, symbols),
    [state.data, symbols],
  );
  const sum = symbols.reduce((s, k) => s + (weights[k] || 0), 0);
  const valid =
    symbols.length > 0 &&
    Math.abs(sum - 100) < 1e-6 &&
    symbols.every((s) => Number.isFinite(weights[s]) && weights[s] >= 0);
  const result =
    valid && aligned.dates.length >= 3
      ? portfolioRisk(
          aligned.prices,
          symbols.map((s) => weights[s] / 100),
        )
      : null;
  return (
    <section className="space-y-4">
      <div className="flex justify-between">
        <div>
          <h1 className="text-lg">组合风险分析</h1>
          <p className="text-xs text-slate-500">
            自定义持仓权重 · 波动贡献 · 历史尾部损失
          </p>
        </div>
        <button
          disabled={!result}
          onClick={() =>
            download(
              "portfolio-risk.json",
              JSON.stringify(
                {
                  symbols,
                  weights,
                  start,
                  end,
                  actualStart: aligned.dates[0],
                  actualEnd: aligned.dates.at(-1),
                  ...result,
                },
                null,
                2,
              ),
              "application/json",
            )
          }
        >
          导出风险 JSON
        </button>
      </div>
      <SelectionBar
        {...{ symbols, setSymbols, start, end, setStart, setEnd }}
      />
      <div className="flex flex-wrap items-center gap-4 text-xs">
        {symbols.map((s) => (
          <label key={s}>
            {s} 权重 %{" "}
            <input
              aria-label={`${s}权重`}
              type="number"
              min={0}
              max={100}
              step={1}
              value={weights[s] ?? 0}
              onChange={(e) =>
                setWeights({ ...weights, [s]: Number(e.target.value) })
              }
              className="w-20"
            />
          </label>
        ))}
        <button
          onClick={() =>
            setWeights(
              Object.fromEntries(symbols.map((s) => [s, 100 / symbols.length])),
            )
          }
        >
          设为等权
        </button>
        <span>合计 {sum.toFixed(2)}%</span>
      </div>
      {!valid && (
        <p role="alert" className="text-amber-300">
          请设置非负权重，合计必须为100%。
        </p>
      )}
      {state.error ? (
        <ErrorBox error={state.error} />
      ) : state.loading ? (
        <Loading />
      ) : !result ? (
        <Empty text="调整权重或区间以查看风险结果。" />
      ) : (
        <>
          <div className="flex flex-wrap gap-8 border-y border-slate-800 py-4 text-sm">
            {[
              ["年化波动率", result.volatility],
              ["历史日VaR95", result.var95],
              ["历史日ES95", result.es95],
              ["最大回撤", result.maxDrawdown],
            ].map(([label, value]) => (
              <div key={String(label)}>
                <p className="text-xs text-slate-500">{label}</p>
                <strong className="font-mono">{percent(Number(value))}</strong>
              </div>
            ))}
          </div>
          <p className="text-xs text-slate-500">
            {result.observations}{" "}
            个共同日收益；252日年化，样本协方差。VaR取最差5%收益的边界，ES取该尾部均值，损失以正值表示。固定权重每日再平衡，不计费用，仅为样本内风险描述。
          </p>
          <Chart
            label="组合历史回撤曲线"
            height={270}
            exportName="portfolio-drawdown"
            option={{
              xAxis: { ...axis, type: "category", data: aligned.dates },
              yAxis: {
                ...axis,
                type: "value",
                axisLabel: {
                  formatter: (v: number) => (v * 100).toFixed(0) + "%",
                },
              },
              series: [
                {
                  type: "line",
                  showSymbol: false,
                  data: result.curve.map((p) => p.drawdown),
                  areaStyle: { opacity: 0.2 },
                },
              ],
            }}
          />
          <div className="table-scroll">
            <table className="w-full text-xs">
              <thead>
                <tr>
                  <th>成分</th>
                  <th>配置权重</th>
                  <th>年化波动贡献</th>
                  <th>波动贡献占比</th>
                </tr>
              </thead>
              <tbody>
                {symbols.map((s, i) => (
                  <tr key={s}>
                    <td>{s}</td>
                    <td>{percent(weights[s] / 100)}</td>
                    <td>{percent(result.contributions[i])}</td>
                    <td>
                      {percent(
                        result.volatility
                          ? result.contributions[i] / result.volatility
                          : 0,
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <h2>收益相关性矩阵</h2>
          <div className="table-scroll">
            <table className="w-full text-xs">
              <thead>
                <tr>
                  <th>证券</th>
                  {symbols.map((s) => (
                    <th key={s}>{s}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {symbols.map((s, i) => (
                  <tr key={s}>
                    <td>{s}</td>
                    {result.correlation[i].map((v, j) => (
                      <td key={j}>{v.toFixed(3)}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="text-xs text-slate-500">
            分散配置可使部分成分的波动贡献为负；历史风险不能保证未来损失上限。
          </p>
        </>
      )}
    </section>
  );
}
