import { useState } from "react";
import type { BacktestResult, Model } from "../../objects/analysis";
import { Panel, Notice, Tag } from "../../components/ui/Panel";
import { Chart, axis } from "../../components/ui/Chart";
import { Metrics } from "../../components/ui/Metrics";
import { number, percent, palette } from "../../utils/format";
import { download } from "../../utils/download";
export function BacktestView({ data }: { data: BacktestResult }) {
  const [model, setModel] = useState<Model>(data.results[0].model);
  const selected =
    data.results.find((x) => x.model === model) || data.results[0];
  const categories = data.results[0].curve.map((p) => p.date);
  const option = (drawdown = false) => ({
    legend: { top: 0, textStyle: { color: "#8a98ae", fontSize: 10 } },
    grid: { top: 40 },
    xAxis: { ...axis, type: "category", data: categories, boundaryGap: false },
    yAxis: {
      ...axis,
      type: "value",
      scale: true,
      axisLabel: {
        formatter: (v: number) => (drawdown ? percent(v, 0) : v.toFixed(2)),
      },
    },
    dataZoom: [{ type: "inside" }],
    series: data.results.map((r, i) => ({
      name: r.label,
      type: "line",
      showSymbol: false,
      lineStyle: {
        width: r.model === selected.model ? 2.5 : 1,
        opacity: r.model === selected.model ? 1 : 0.65,
      },
      itemStyle: { color: palette[i] },
      data: r.curve.map((p) => (drawdown ? p.drawdown : p.value)),
    })),
  });
  function exportCSV() {
    download(
      "backtest-curves.csv",
      "date," +
        data.results.map((r) => r.model).join(",") +
        "\n" +
        categories
          .map(
            (date, i) =>
              date + "," + data.results.map((r) => r.curve[i].value).join(","),
          )
          .join("\n"),
      "text/csv;charset=utf-8",
    );
  }
  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-2 text-[11px] text-slate-500">
        <span>
          {data.start} → {data.end} · {selected.curve.length - 1} 个样本外收益日
        </span>
        <Tag>OUT OF SAMPLE / 扣费后</Tag>
      </div>
      <div className="flex flex-wrap gap-2">
        {data.results.map((r) => (
          <button
            key={r.model}
            onClick={() => setModel(r.model)}
            className={`btn ${selected.model === r.model ? "!border-[#b7ed77]/40 !text-[#b7ed77]" : ""}`}
          >
            {r.label}
          </button>
        ))}
      </div>
      <Metrics data={selected.metrics} backtest />
      <Panel
        title="组合净值"
        subtitle="初始净值 1.00 · 相同区间、成本与调仓日"
        action={
          <button className="btn no-print" onClick={exportCSV}>
            导出 CSV
          </button>
        }
      >
        <Chart label="样本外组合净值" height={330} option={option()} />
      </Panel>
      <Panel title="回撤轨迹" subtitle="相对各自历史最高净值">
        <Chart label="组合回撤" height={220} option={option(true)} />
      </Panel>
      <Panel title="策略对照" subtitle="风险平价可通过左侧主策略切换加入">
        <div className="table-scroll">
          <table className="w-full">
            <thead>
              <tr>
                <th>策略</th>
                <th>年化收益</th>
                <th>波动率</th>
                <th>Sharpe</th>
                <th>最大回撤</th>
                <th>累计双向换手</th>
                <th>未收敛调仓</th>
              </tr>
            </thead>
            <tbody>
              {data.results.map((r) => (
                <tr key={r.model}>
                  <td>
                    <button
                      onClick={() => setModel(r.model)}
                      className={
                        r.model === selected.model
                          ? "text-[#b7ed77]"
                          : "text-slate-300"
                      }
                    >
                      {r.label}
                    </button>
                  </td>
                  <td>{percent(r.metrics.annualReturn)}</td>
                  <td>{percent(r.metrics.volatility)}</td>
                  <td>{number(r.metrics.sharpe)}</td>
                  <td>{percent(r.metrics.maxDrawdown)}</td>
                  <td>{percent(r.totalTurnover, 1)}</td>
                  <td>{r.failedRebalances}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Panel>
      <Panel
        title={`${selected.label} / 调仓审计`}
        subtitle="每条记录保留估计截止日、执行日与持仓，便于检查未来数据泄漏"
      >
        <div className="max-h-72 overflow-auto">
          <table className="w-full">
            <thead className="sticky top-0 bg-[#111823]">
              <tr>
                <th>信号截止</th>
                <th>执行日</th>
                <th>首个收益日</th>
                <th>双向换手</th>
                <th>费率扣减</th>
                <th>目标持仓</th>
                <th>状态</th>
              </tr>
            </thead>
            <tbody>
              {selected.trades.map((t) => (
                <tr key={t.executionDate}>
                  <td className="font-mono text-[10px]">{t.signalEnd}</td>
                  <td className="font-mono text-[10px] text-slate-200">
                    {t.executionDate}
                  </td>
                  <td className="font-mono text-[10px]">{t.returnDate}</td>
                  <td>{percent(t.turnover, 1)}</td>
                  <td>{percent(t.cost, 3)}</td>
                  <td className="text-[10px] text-slate-500">
                    {t.weights
                      .map((w, i) => `${data.symbols[i]} ${percent(w, 0)}`)
                      .join(" / ")}
                  </td>
                  <td
                    className={
                      t.converged ? "text-[#b7ed77]" : "text-amber-200"
                    }
                  >
                    {t.converged ? "收敛" : "等权回退"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Panel>
      <Notice>
        <details open>
          <summary className="cursor-pointer">回测方法与限制</summary>
          <p className="mt-3">{data.methodology}</p>
          <p className="mt-2">{data.alignment}</p>
          <p className="mt-2">
            因对齐移除的价格日：
            {Object.entries(data.droppedSessions)
              .map(([s, n]) => `${s} ${n}`)
              .join(" · ")}
          </p>
          {data.warnings.map((w) => (
            <p className="mt-2" key={w}>
              {w}
            </p>
          ))}
        </details>
      </Notice>
    </div>
  );
}
