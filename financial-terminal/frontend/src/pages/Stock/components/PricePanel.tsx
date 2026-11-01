import { useFrequencyBars } from "../../../hooks/useFrequencyBars";
import { useEffect, useState } from "react";
import type { StockResult } from "../../../objects/market";
import { Panel } from "../../../components/ui/Panel";
import { Chart } from "../../../components/ui/Chart";
import { priceChart } from "../functions/charts";
export function PricePanel({
  data,
  comparison,
}: {
  data: StockResult;
  comparison: StockResult | null;
}) {
  const [mode, setMode] = useState<"line" | "candle">("candle");
  const [period, setPeriod] = useState(252);
  const [averages, setAverages] = useState(true);
  const frequencyState = useFrequencyBars(
    data.stock.symbol,
    data.bars,
    data.bars[0]?.date || "",
    data.bars.at(-1)?.date || "",
  );
  useEffect(() => {
    if (comparison) frequencyState.setFrequency("1d");
  }, [comparison]);
  const plottedBars =
    frequencyState.frequency === "1d"
      ? period
        ? data.bars.slice(-period)
        : data.bars
      : frequencyState.bars;
  const visible = {
    ...data,
    bars: plottedBars,
  };
  return (
    <Panel
      title={comparison ? "相对表现 / 共同首日归零" : "价格走势 / 多频率"}
      subtitle={`${visible.bars[0]?.date || "—"} — ${visible.bars.at(-1)?.date || "—"} · USD · 历史行情`}
    >
      <div
        className="flex flex-wrap items-center gap-1 px-3 pb-2"
        aria-label="图表工具栏"
      >
        <select
          aria-label="K线频率"
          value={frequencyState.frequency}
          disabled={!!comparison}
          onChange={(e) => frequencyState.setFrequency(e.target.value)}
        >
          {frequencyState.options.length ? (
            frequencyState.options.map((f) => (
              <option key={f.code} value={f.code} disabled={!f.available}>
                {f.label}
              </option>
            ))
          ) : (
            <option value="1d">日</option>
          )}
        </select>
        {frequencyState.frequency === "1d" &&
          (
            [
              ["1M", 22],
              ["3M", 63],
              ["6M", 126],
              ["1Y", 252],
              ["全部", 0],
            ] as const
          ).map(([label, n]) => (
            <button
              key={label}
              aria-pressed={period === n}
              className={`px-2 py-1 font-mono text-[10px] ${period === n ? "bg-white/10 text-[#e9b45b]" : "text-slate-500"}`}
              onClick={() => setPeriod(n)}
            >
              {label}
            </button>
          ))}
        {!comparison && (
          <>
            <span className="mx-1 h-3 border-l border-white/10" />
            <button
              className="btn !px-2"
              aria-pressed={mode === "candle"}
              onClick={() => setMode(mode === "candle" ? "line" : "candle")}
            >
              {mode === "candle" ? "日 K" : "折线"}
            </button>
            <button
              className={`btn !px-2 ${averages ? "!text-[#e9b45b]" : ""}`}
              aria-pressed={averages}
              onClick={() => setAverages(!averages)}
            >
              MA
            </button>
          </>
        )}
      </div>
      {frequencyState.error && (
        <p className="frequency-note">{frequencyState.error}</p>
      )}
      {frequencyState.minute && (
        <p className="frequency-note">
          分钟范围 {frequencyState.selected?.start} —{" "}
          {frequencyState.selected?.end}
          ；默认显示末7个自然日；数据中心可自定义。
        </p>
      )}
      {frequencyState.frequency !== "1d" && !frequencyState.minute && (
        <p className="frequency-note">
          月/年线从真实日线聚合，首尾周期可能不完整；均线按K线根数计算，不足周期不显示。统计与比较仍采用日频。
        </p>
      )}
      <Chart
        label="历史价格与股票比较"
        height={315}
        option={priceChart(
          visible,
          comparison,
          mode,
          averages,
          frequencyState.frequency === "1d" ? data.bars : frequencyState.bars,
        )}
        exportName={`aperture-${data.stock.symbol}-price`}
      />
    </Panel>
  );
}
