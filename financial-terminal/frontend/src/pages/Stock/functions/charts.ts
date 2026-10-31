import type { Bar, StockResult } from "../../../objects/market";
import { axis } from "../../../components/ui/Chart";
export function priceChart(data: StockResult, comparison: StockResult | null) {
  const bars = data.bars;
  const dateSet = new Set(comparison?.bars.map((b) => b.date) || []);
  const aligned = comparison ? bars.filter((b) => dateSet.has(b.date)) : bars;
  const other = new Map(comparison?.bars.map((b) => [b.date, b.close]));
  const base = aligned[0]?.close || 1;
  const baseOther = other.get(aligned[0]?.date) || 1;
  return {
    tooltip: { trigger: "axis" },
    legend: { show: !!comparison, textStyle: { color: "#8a98ae" }, top: 0 },
    grid: { top: comparison ? 40 : 20 },
    xAxis: {
      ...axis,
      type: "category",
      data: aligned.map((b) => b.date),
      boundaryGap: false,
    },
    yAxis: {
      ...axis,
      type: "value",
      scale: true,
      axisLabel: {
        formatter: (v: number) =>
          comparison ? `${v.toFixed(0)}%` : v.toFixed(0),
      },
    },
    dataZoom: [
      { type: "inside" },
      {
        type: "slider",
        height: 15,
        bottom: 2,
        borderColor: "transparent",
        fillerColor: "#b7ed7712",
        dataBackground: {
          lineStyle: { color: "#4d5d70" },
          areaStyle: { color: "#27303b" },
        },
        handleStyle: { color: "#596958" },
        textStyle: { color: "#66778c" },
      },
    ],
    series: [
      {
        name: data.stock.symbol,
        type: "line",
        showSymbol: false,
        lineStyle: { width: 2 },
        areaStyle: comparison
          ? undefined
          : {
              color: {
                type: "linear",
                x: 0,
                y: 0,
                x2: 0,
                y2: 1,
                colorStops: [
                  { offset: 0, color: "#b7ed7720" },
                  { offset: 1, color: "#b7ed7700" },
                ],
              },
            },
        data: aligned.map((b) =>
          comparison ? (b.close / base - 1) * 100 : b.close,
        ),
      },
      ...(comparison
        ? [
            {
              name: comparison.stock.symbol,
              type: "line",
              showSymbol: false,
              lineStyle: { width: 1.5 },
              data: aligned.map(
                (b) => (other.get(b.date)! / baseOther - 1) * 100,
              ),
            },
          ]
        : []),
    ],
  };
}
export function distribution(bars: Bar[]) {
  const r = bars.slice(1).map((b, i) => b.close / bars[i].close - 1);
  if (!r.length) return {};
  const low = Math.min(...r),
    high = Math.max(...r);
  const width = (high - low || 0.01) / 24;
  const counts = Array.from({ length: 24 }, () => 0);
  r.forEach((x) => {
    counts[Math.min(23, Math.floor((x - low) / width))]++;
  });
  return {
    xAxis: {
      ...axis,
      type: "category",
      data: counts.map(
        (_, i) => `${((low + (i + 0.5) * width) * 100).toFixed(1)}%`,
      ),
    },
    yAxis: { ...axis, type: "value" },
    series: [
      {
        type: "bar",
        barCategoryGap: "10%",
        itemStyle: {
          color: "#67c8f1",
          opacity: 0.75,
          borderRadius: [2, 2, 0, 0],
        },
        data: counts,
      },
    ],
  };
}
