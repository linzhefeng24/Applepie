import type { StockResult, Audit } from "../../../objects/market";
import { Panel, Tag } from "../../../components/ui/Panel";
import { Chart } from "../../../components/ui/Chart";
import { priceChart, distribution } from "../functions/charts";
import { number, percent, compact } from "../../../utils/format";
export function DistributionPanel({ data }: { data: StockResult }) {
  return (
    <Panel title="收益分布" subtitle="相邻源日线的简单价格收益">
      <Chart
        label="日收益直方图"
        height={245}
        option={distribution(data.bars)}
      />
      <div className="grid grid-cols-2 gap-3 border-t border-white/5 px-5 py-4">
        <div className="text-[10px] text-slate-500">
          偏度{" "}
          <strong className="ml-2 font-mono text-slate-200">
            {number(data.metrics.skewness)}
          </strong>
        </div>
        <div className="text-[10px] text-slate-500">
          超额峰度{" "}
          <strong className="ml-2 font-mono text-slate-200">
            {number(data.metrics.excessKurtosis)}
          </strong>
        </div>
      </div>
    </Panel>
  );
}
