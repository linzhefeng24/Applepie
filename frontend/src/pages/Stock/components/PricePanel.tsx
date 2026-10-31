import type { StockResult, Audit } from "../../../objects/market";
import { Panel, Tag } from "../../../components/ui/Panel";
import { Chart } from "../../../components/ui/Chart";
import { priceChart, distribution } from "../functions/charts";
import { number, percent, compact } from "../../../utils/format";
export function PricePanel({
  data,
  comparison,
}: {
  data: StockResult;
  comparison: StockResult | null;
}) {
  return (
    <Panel
      title={comparison ? "相对表现 / 共同首日归零" : "历史收盘价"}
      subtitle={`${data.bars[0].date} — ${data.bars.at(-1)!.date} · 日频 / ${data.stock.source}`}
      action={<Tag>{comparison ? "PRICE RETURN %" : "USD"}</Tag>}
    >
      <Chart
        label="历史价格与股票比较"
        height={335}
        option={priceChart(data, comparison)}
      />
    </Panel>
  );
}
