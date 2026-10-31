import { useState } from "react";
import type { AnalysisResult, Model } from "../../objects/analysis";
import { Panel, Notice, Tag } from "../../components/ui/Panel";
import { Chart, axis } from "../../components/ui/Chart";
import { Metrics } from "../../components/ui/Metrics";
import { number, percent, palette } from "../../utils/format";
export function AnalysisView({ data }: { data: AnalysisResult }) {
  const [model, setModel] = useState<Model>("mvsk");
  const selected = data.models.find((x) => x.model === model) || data.models[0];
  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-2 text-[11px] text-slate-500">
        <span>
          {data.start} → {data.end} · {data.sessions} 个共同价格日
        </span>
        <Tag>IN SAMPLE / 估计区间</Tag>
      </div>
      <div className="flex flex-wrap gap-2">
        {data.models.map((m) => (
          <button
            key={m.model}
            onClick={() => setModel(m.model)}
            className={`btn ${selected.model === m.model ? "!border-[#b7ed77]/40 !text-[#b7ed77] !bg-[#b7ed77]/5" : ""}`}
          >
            {m.label}
          </button>
        ))}
      </div>
      <Metrics data={selected.metrics} />
      <div className="grid gap-4 xl:grid-cols-2">
        <Panel
          title="组合配置"
          subtitle={`${selected.label} · ${selected.converged ? "求解成功" : "回退等权"}`}
          action={<Tag>{selected.iterations} ITERATIONS</Tag>}
        >
          <div className="grid grid-cols-[.9fr_1fr] items-center">
            <Chart
              label="组合权重环形图"
              height={220}
              option={{
                tooltip: { trigger: "item", formatter: "{b}: {d}%" },
                series: [
                  {
                    type: "pie",
                    radius: ["55%", "78%"],
                    center: ["50%", "50%"],
                    label: { show: false },
                    itemStyle: { borderWidth: 3, borderColor: "#111823" },
                    data: data.symbols.map((s, i) => ({
                      name: s,
                      value: selected.weights[i],
                      itemStyle: { color: palette[i % palette.length] },
                    })),
                  },
                ],
              }}
            />
            <div className="space-y-3 pr-5">
              {data.symbols.map((s, i) => (
                <div key={s} className="text-xs">
                  <div className="mb-1 flex justify-between">
                    <span className="font-mono text-slate-300">{s}</span>
                    <span className="font-mono text-slate-400">
                      {percent(selected.weights[i], 1)}
                    </span>
                  </div>
                  <div className="h-1 rounded bg-white/5">
                    <div
                      className="h-1 rounded"
                      style={{
                        width: `${selected.weights[i] * 100}%`,
                        background: palette[i % palette.length],
                      }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
          <div className="border-t border-white/5 px-5 py-3 text-[10px] text-slate-500">
            {selected.message} · 权重和{" "}
            {percent(
              selected.weights.reduce((a, b) => a + b, 0),
              1,
            )}
          </div>
        </Panel>
        <Panel title="组合收益分布" subtitle="直接从组合日收益计算高阶矩">
          <Chart
            height={220}
            label="组合收益分布"
            option={{
              xAxis: {
                ...axis,
                type: "category",
                data: selected.histogram.counts.map((_, i) =>
                  percent(
                    (selected.histogram.edges[i] +
                      selected.histogram.edges[i + 1]) /
                      2,
                    1,
                  ),
                ),
              },
              yAxis: { ...axis, type: "value" },
              series: [
                {
                  type: "bar",
                  data: selected.histogram.counts,
                  itemStyle: {
                    color: "#67c8f1",
                    opacity: 0.7,
                    borderRadius: [2, 2, 0, 0],
                  },
                },
              ],
            }}
          />
          <div className="flex justify-around border-t border-white/5 py-3 text-[10px] text-slate-500">
            <span>
              偏度{" "}
              <b className="font-mono text-slate-200">
                {number(selected.metrics.skewness)}
              </b>
            </span>
            <span>
              超额峰度{" "}
              <b className="font-mono text-slate-200">
                {number(selected.metrics.excessKurtosis)}
              </b>
            </span>
            <span>
              日 VaR95{" "}
              <b className="font-mono text-slate-200">
                {percent(selected.metrics.var95)}
              </b>
            </span>
          </div>
        </Panel>
      </div>
      <Panel
        title="模型横向对照"
        subtitle="同一价格区间 · 同一约束 · 每日恒定权重毛收益描述"
      >
        <div className="table-scroll">
          <table className="w-full">
            <thead>
              <tr>
                <th>模型</th>
                <th>年化收益</th>
                <th>波动率</th>
                <th>Sharpe</th>
                <th>最大回撤</th>
                <th>偏度</th>
                <th>超额峰度</th>
                <th>求解状态</th>
              </tr>
            </thead>
            <tbody>
              {data.models.map((m) => (
                <tr
                  key={m.model}
                  className={
                    m.model === selected.model ? "bg-[#b7ed77]/[.035]" : ""
                  }
                >
                  <td>
                    <button
                      className="text-slate-200"
                      onClick={() => setModel(m.model)}
                    >
                      {m.label}
                    </button>
                  </td>
                  <td className="font-mono text-[#b7ed77]">
                    {percent(m.metrics.annualReturn)}
                  </td>
                  <td>{percent(m.metrics.volatility)}</td>
                  <td>{number(m.metrics.sharpe)}</td>
                  <td>{percent(m.metrics.maxDrawdown)}</td>
                  <td>{number(m.metrics.skewness)}</td>
                  <td>{number(m.metrics.excessKurtosis)}</td>
                  <td
                    className={
                      m.converged ? "text-[#b7ed77]" : "text-amber-200"
                    }
                  >
                    {m.converged ? "已收敛" : "回退等权"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Panel>
      <Panel title="收益相关性" subtitle="共同日期上的 Pearson 相关系数">
        <Chart
          label="股票收益相关性热力图"
          height={290}
          option={{
            grid: { left: 65, right: 65, top: 15, bottom: 35 },
            tooltip: {
              position: "top",
              formatter: (p: { value: number[] }) =>
                `${data.symbols[p.value[0]]} × ${data.symbols[p.value[1]]}: ${p.value[2].toFixed(3)}`,
            },
            xAxis: { type: "category", data: data.symbols, ...axis },
            yAxis: { type: "category", data: data.symbols, ...axis },
            visualMap: {
              min: -1,
              max: 1,
              calculable: false,
              orient: "vertical",
              right: 0,
              top: "center",
              inRange: { color: ["#293d65", "#192632", "#91bc65"] },
              textStyle: { color: "#718197" },
            },
            series: [
              {
                type: "heatmap",
                label: {
                  show: true,
                  color: "#dce6e0",
                  fontSize: 10,
                  formatter: (p: { value: number[] }) => p.value[2].toFixed(2),
                },
                data: data.correlation.flatMap((row, i) =>
                  row.map((v, j) => [i, j, v]),
                ),
                itemStyle: { borderColor: "#111823", borderWidth: 3 },
              },
            ],
          }}
        />
      </Panel>
      <Notice>
        <details>
          <summary className="cursor-pointer">
            模型方法、对齐规则与研究限制
          </summary>
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
