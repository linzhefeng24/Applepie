import { useState } from "react";
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
  const visible = {
    ...data,
    bars: period ? data.bars.slice(-period) : data.bars,
  };
  return (
    <Panel
      title={comparison ? "相对表现 / 共同首日归零" : "价格走势 / 日线"}
      subtitle={`${visible.bars[0]?.date || "—"} — ${visible.bars.at(-1)?.date || "—"} · USD · 历史行情`}
    >
      <div
        className="flex flex-wrap items-center gap-1 px-3 pb-2"
        aria-label="图表工具栏"
      >
        {(
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
      <Chart
        label="历史价格与股票比较"
        height={315}
        option={priceChart(visible, comparison, mode, averages, data.bars)}
      />
    </Panel>
  );
}
