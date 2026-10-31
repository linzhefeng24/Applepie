import { PricePanel } from "./components/PricePanel";
import { DistributionPanel } from "./components/DistributionPanel";
import { AnnualTable } from "./components/AnnualTable";
import { FinancialPanel } from "./components/FinancialPanel";
import { QualityPanel } from "./components/QualityPanel";
import { useState } from "react";
import {
  useSelectedStock,
  selectStock,
  useMarket,
} from "../../stores/research";
import { PageTitle } from "../../components/ui/PageTitle";
import {
  Panel,
  Notice,
  Loading,
  ErrorBox,
  Empty,
  Tag,
} from "../../components/ui/Panel";
import { Metrics } from "../../components/ui/Metrics";
import { useStock } from "./hooks/useStock";
import { number, percent } from "../../utils/format";
export function StockPage() {
  const market = useMarket()!;
  const symbol = useSelectedStock();
  const [start, setStart] = useState(
    market.stocks.reduce(
      (date, s) => (s.firstDate < date ? s.firstDate : date),
      "9999",
    ),
  );
  const [end, setEnd] = useState(
    market.stocks.reduce(
      (date, s) => (s.lastDate > date ? s.lastDate : date),
      "",
    ),
  );
  const [compare, setCompare] = useState("");
  const state = useStock(symbol, start, end, compare);
  const audit = market.provenance.audits.find((x) => x.symbol === symbol);
  return (
    <>
      <PageTitle
        eyebrow="EQUITY RESEARCH"
        title="个股研究"
        description="历史价格、年度表现、收益分布与数据质量。"
      />
      <div className="mb-6 flex flex-wrap items-end gap-3">
        <label className="field">
          研究标的
          <select
            aria-label="研究标的"
            value={symbol}
            onChange={(e) => selectStock(e.target.value)}
          >
            {market.stocks.map((s) => (
              <option key={s.symbol} value={s.symbol}>
                {s.symbol} · {s.name}
              </option>
            ))}
          </select>
        </label>
        <label className="field">
          起始日期
          <input
            aria-label="起始日期"
            type="date"
            value={start}
            onChange={(e) => setStart(e.target.value)}
          />
        </label>
        <label className="field">
          截止日期
          <input
            aria-label="截止日期"
            type="date"
            value={end}
            onChange={(e) => setEnd(e.target.value)}
          />
        </label>
        <label className="field">
          比较标的
          <select
            aria-label="比较标的"
            value={compare}
            onChange={(e) => setCompare(e.target.value)}
          >
            <option value="">不比较 / 价格模式</option>
            {market.stocks
              .filter((s) => s.symbol !== symbol)
              .map((s) => (
                <option key={s.symbol}>{s.symbol}</option>
              ))}
          </select>
        </label>
      </div>
      {state.status === "loading" ? (
        <Loading />
      ) : state.status === "error" ? (
        <ErrorBox error={state.error} />
      ) : !state.data.bars.length ? (
        <Empty text="当前区间没有行情，请调整日期。" />
      ) : (
        <>
          <div className="mb-5 flex items-center gap-3">
            <h2 className="font-mono text-2xl font-semibold text-white">
              {symbol}
            </h2>
            <span className="text-sm text-slate-400">
              {state.data.stock.name}
            </span>
            <Tag>{state.data.stock.sector} / USD</Tag>
          </div>
          <Metrics data={state.data.metrics} />
          <div className="mt-5 grid gap-4 xl:grid-cols-[2fr_1fr]">
            <PricePanel data={state.data} comparison={state.comparison} />
            <DistributionPanel data={state.data} />
          </div>
          {state.comparison && (
            <div className="mt-4">
              <Panel
                title="同区间指标对比"
                subtitle="各标的按自身可用观测计算，图表则按共同日期对齐"
              >
                <div className="table-scroll">
                  <table className="w-full">
                    <thead>
                      <tr>
                        <th>标的</th>
                        <th>区间收益</th>
                        <th>年化波动</th>
                        <th>Sharpe</th>
                        <th>最大回撤</th>
                        <th>观测</th>
                      </tr>
                    </thead>
                    <tbody>
                      {[state.data, state.comparison].map((x) => (
                        <tr key={x.stock.symbol}>
                          <td className="font-mono text-[#b7ed77]">
                            {x.stock.symbol}
                          </td>
                          <td>{percent(x.metrics.totalReturn)}</td>
                          <td>{percent(x.metrics.volatility)}</td>
                          <td>{number(x.metrics.sharpe)}</td>
                          <td>{percent(x.metrics.maxDrawdown)}</td>
                          <td>{x.metrics.observations}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </Panel>
            </div>
          )}
          <div className="mt-5">
            <AnnualTable data={state.data} />
          </div>
          <div className="mt-5 grid gap-4 xl:grid-cols-2">
            <FinancialPanel />
            <QualityPanel audit={audit} />
          </div>
          <div className="mt-5">
            <Notice>
              复权状态未知，未计分红；跨日价格跳变可能包含公司行动。日线由所有有效源分钟聚合，缺失分钟不补齐；价格与成交量不等于交易所官方日行情。首年收益从首个可用收盘价开始，后续年使用前一年最后可用收盘价作为基期；历史不足的年化数字应谨慎解读。
            </Notice>
          </div>
        </>
      )}
    </>
  );
}
