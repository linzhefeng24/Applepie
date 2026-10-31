import type { StockResult, Audit } from "../../../objects/market";
import { Panel, Tag } from "../../../components/ui/Panel";
import { Chart } from "../../../components/ui/Chart";
import { priceChart, distribution } from "../functions/charts";
import { number, percent, compact } from "../../../utils/format";
export function FinancialPanel({}: {}) {
  return (
    <Panel title="财务与估值指标" subtitle="数据中没有财报，因此不展示虚构值">
      <div className="grid grid-cols-3 gap-4 px-5 pb-5">
        {["营业收入", "净利润", "ROE", "PE", "PB", "股息率"].map((x) => (
          <div key={x} className="rounded-lg bg-black/15 p-3">
            <div className="text-[10px] text-slate-500">{x}</div>
            <div className="mt-2 font-mono text-slate-600">未提供</div>
          </div>
        ))}
      </div>
    </Panel>
  );
}
