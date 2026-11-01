import { useMemo, useState } from "react";
import { usePriceSelection } from "../shared/hooks/usePriceSelection";
import { SelectionBar } from "../shared/SelectionBar";
import { alignPrices, portfolioRisk } from "../shared/functions/portfolio";
import { Chart, axis } from "../../components/ui/Chart";
import { ErrorBox, Loading, Empty } from "../../components/ui/Panel";
import { percent } from "../../utils/format";
import { download } from "../../utils/download";
export function ComparePage() {
  const [symbols, setSymbols] = useState(["AAPL", "GOOG", "GLD"]),
    [start, setStart] = useState("2023-01-01"),
    [end, setEnd] = useState("2026-10-23");
  const state = usePriceSelection(symbols, start, end);
  const aligned = useMemo(
    () => alignPrices(state.data, symbols),
    [state.data, symbols],
  );
  const comparisons =
    aligned.dates.length >= 3
      ? symbols.map((symbol, i) => ({
          symbol,
          ...portfolioRisk([aligned.prices[i]], [1]),
        }))
      : [];
  return (
    <section className="space-y-4">
      <div className="flex justify-between">
        <div>
          <h1 className="text-lg">证券对比</h1>
          <p className="text-xs text-slate-500">
            共同交易日 · 统一基期100 · 日频历史行情
          </p>
        </div>
        <button
          disabled={!comparisons.length}
          onClick={() =>
            download(
              "security-comparison.csv",
              "date," +
                symbols.join(",") +
                "\n" +
                aligned.dates
                  .map((d, t) =>
                    [d, ...aligned.prices.map((p) => (p[t] / p[0]) * 100)].join(
                      ",",
                    ),
                  )
                  .join("\n"),
              "text/csv;charset=utf-8",
            )
          }
        >
          导出对比 CSV
        </button>
      </div>
      <SelectionBar
        {...{ symbols, setSymbols, start, end, setStart, setEnd }}
      />
      {state.error ? (
        <ErrorBox error={state.error} />
      ) : state.loading ? (
        <Loading />
      ) : !comparisons.length ? (
        <Empty text="共同价格日不足，请调整证券或区间。" />
      ) : (
        <>
          <p className="text-xs text-slate-400">
            实际共同区间 {aligned.dates[0]} — {aligned.dates.at(-1)} ·{" "}
            {aligned.dates.length} 个价格日；缺失日期取交集，不前向填充。
          </p>
          <Chart
            label="多证券基期对比曲线"
            height={380}
            exportName="security-comparison"
            option={{
              legend: { data: symbols, textStyle: { color: "#94a3b8" } },
              xAxis: { ...axis, type: "category", data: aligned.dates },
              yAxis: { ...axis, type: "value", scale: true },
              dataZoom: [{ type: "inside" }, { type: "slider" }],
              series: symbols.map((s, i) => ({
                name: s,
                type: "line",
                showSymbol: false,
                data: aligned.prices[i].map(
                  (p) => (p / aligned.prices[i][0]) * 100,
                ),
              })),
            }}
          />
          <div className="table-scroll">
            <table className="w-full text-xs">
              <thead>
                <tr>
                  <th>证券</th>
                  <th>区间收益</th>
                  <th>年化波动率</th>
                  <th>最大回撤</th>
                  <th>日VaR95</th>
                </tr>
              </thead>
              <tbody>
                {comparisons.map((c) => (
                  <tr key={c.symbol}>
                    <td>{c.symbol}</td>
                    <td>{percent(c.totalReturn)}</td>
                    <td>{percent(c.volatility)}</td>
                    <td>{percent(c.maxDrawdown)}</td>
                    <td>{percent(c.var95)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </section>
  );
}
