import { useEffect, useRef } from "react";
import * as echarts from "echarts/core";
import { LineChart, BarChart, PieChart, HeatmapChart } from "echarts/charts";
import {
  GridComponent,
  TooltipComponent,
  LegendComponent,
  DataZoomComponent,
  VisualMapComponent,
} from "echarts/components";
import { CanvasRenderer } from "echarts/renderers";
import type { EChartsCoreOption } from "echarts/core";
echarts.use([
  LineChart,
  BarChart,
  PieChart,
  HeatmapChart,
  GridComponent,
  TooltipComponent,
  LegendComponent,
  DataZoomComponent,
  VisualMapComponent,
  CanvasRenderer,
]);
export function Chart({
  option,
  height = 300,
  label,
}: {
  option: EChartsCoreOption;
  height?: number;
  label: string;
}) {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (!ref.current) return;
    const chart = echarts.init(ref.current, undefined, { renderer: "canvas" });
    chart.setOption({
      backgroundColor: "transparent",
      color: ["#b7ed77", "#67c8f1", "#c1a0ff", "#f4bd73", "#f08c9d"],
      textStyle: {
        color: "#8a98ae",
        fontFamily: "ui-monospace, monospace",
        fontSize: 10,
      },
      tooltip: {
        trigger: "axis",
        backgroundColor: "#172233",
        borderColor: "#2a3546",
        textStyle: { color: "#dce4ef", fontSize: 11 },
      },
      grid: { left: 58, right: 22, top: 24, bottom: 42 },
      ...option,
    });
    const observer = new ResizeObserver(() => chart.resize());
    observer.observe(ref.current);
    return () => {
      observer.disconnect();
      chart.dispose();
    };
  }, [option]);
  return <div ref={ref} style={{ height }} role="img" aria-label={label} />;
}
export const axis = {
  axisLine: { lineStyle: { color: "#293241" } },
  axisTick: { show: false },
  splitLine: { lineStyle: { color: "#ffffff07" } },
  axisLabel: { color: "#68788e", fontSize: 10 },
};
