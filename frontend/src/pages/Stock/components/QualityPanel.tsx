import type { StockResult, Audit } from "../../../objects/market";
import { Panel, Tag } from "../../../components/ui/Panel";
import { Chart } from "../../../components/ui/Chart";
import { priceChart, distribution } from "../functions/charts";
import { number, percent, compact } from "../../../utils/format";
export function QualityPanel({ audit }: { audit: Audit | undefined }) {
  return (
    <Panel title="数据质量与口径" subtitle="透明展示源数据覆盖情况">
      <div className="space-y-3 px-5 pb-5 text-xs text-slate-500">
        <p>
          原始分钟记录{" "}
          <span className="float-right font-mono text-slate-300">
            {audit?.rawMinutes.toLocaleString()}
          </span>
        </p>
        <p>
          清理的无效分钟 / 重复时间戳{" "}
          <span className="float-right font-mono text-slate-300">
            {audit?.rejectedMinutes} / {audit?.duplicates}
          </span>
        </p>
        <p>
          少于 300 条分钟记录的交易日{" "}
          <span className="float-right font-mono text-amber-200/70">
            {audit?.sessionsUnder300Minutes}
          </span>
        </p>
        <p>
          绝对日收益大于 25% 的交易日{" "}
          <span className="float-right font-mono text-amber-200/70">
            {audit?.dailyMovesOver25Pct}
          </span>
        </p>
      </div>
    </Panel>
  );
}
