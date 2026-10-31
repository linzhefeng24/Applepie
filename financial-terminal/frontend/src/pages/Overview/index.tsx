import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { ArrowUpRight, Activity } from "lucide-react";
import { StockPool } from "./components/StockPool";
import {
  useMarket,
  useSelectedStock,
  selectStock,
  setSymbols,
} from "../../stores/research";
import { Panel, Loading, ErrorBox } from "../../components/ui/Panel";
import { PricePanel } from "../Stock/components/PricePanel";
import { useStock } from "../Stock/hooks/useStock";
import { number, percent } from "../../utils/format";
export function OverviewPage() {
  const market = useMarket()!;
  const symbol = useSelectedStock();
  const [sector, setSector] = useState("全部行业");
  const selected =
    market.stocks.find((s) => s.symbol === symbol) || market.stocks[0];
  const detail = useStock(
    selected.symbol,
    selected.firstDate,
    selected.lastDate,
    "",
  );
  const quotes = market.stocks.flatMap((s) =>
    market.quotes[s.symbol] ? [{ ...s, ...market.quotes[s.symbol] }] : [],
  );
  const gainers = quotes.filter((q) => q.changePct > 0).length;
  const losers = quotes.filter((q) => q.changePct < 0).length;
  const ranked = [...quotes].sort((a, b) => b.changePct - a.changePct);
  const sectors = useMemo(
    () =>
      Array.from(new Set(market.stocks.map((s) => s.sector))).map((name) => {
        const stocks = market.stocks.filter((s) => s.sector === name);
        const valid = stocks.filter((s) =>
          Number.isFinite(market.quotes[s.symbol]?.changePct),
        );
        return {
          name,
          stocks,
          change: valid.length
            ? valid.reduce((a, s) => a + market.quotes[s.symbol].changePct, 0) /
              valid.length
            : null,
        };
      }),
    [market],
  );
  const last = quotes.reduce((date, q) => (q.date > date ? q.date : date), "");
  return (
    <>
      <div className="desk-title">
        <div>
          <div className="desk-eyebrow">MARKET MONITOR / 01</div>
          <h1>行情工作台</h1>
        </div>
        <div className="flex items-center gap-3">
          <span className="hidden text-[11px] text-slate-500 md:block">
            最新可用日线 · 非实时行情
          </span>
          <Link to="/lab" className="btn-primary">
            组合研究 <ArrowUpRight size={13} />
          </Link>
        </div>
      </div>
      <div className="market-summary">
        <div>
          <label>证券覆盖</label>
          <strong>
            {market.stocks.length}
            <small> EQUITIES / ETF</small>
          </strong>
        </div>
        <div>
          <label>上涨 / 下跌 / 持平</label>
          <strong>
            <span className="positive">{gainers}</span>
            <span className="text-slate-600"> / </span>
            <span className="negative">{losers}</span>
            <small> / {quotes.length - gainers - losers}</small>
          </strong>
        </div>
        <div>
          <label>日线观测</label>
          <strong>{market.provenance.rows.toLocaleString()}</strong>
        </div>
        <div>
          <label>最新数据日</label>
          <strong className="!text-base">{last}</strong>
        </div>
        <div>
          <label>研究模型</label>
          <strong>
            05<small> MVSK + CLASSIC</small>
          </strong>
        </div>
      </div>
      <div className="desk-workspace">
        <StockPool sector={sector} setSector={setSector} />
        <div className="space-y-3 min-w-0">
          <Panel
            title="证券速览"
            subtitle="与左侧行情表联动"
            action={
              <span className="panel-code">SECURITY / {selected.symbol}</span>
            }
          >
            <div className="quote-detail">
              <div>
                <strong>{selected.symbol}</strong>
                <span>{selected.name}</span>
                <small>
                  {selected.sector} · USD ·{" "}
                  {market.quotes[selected.symbol]?.date}
                </small>
              </div>
              <div className="text-right">
                <b>{number(market.quotes[selected.symbol]?.close)}</b>
                <span
                  className={
                    market.quotes[selected.symbol]?.changePct >= 0
                      ? "positive"
                      : "negative"
                  }
                >
                  {percent(market.quotes[selected.symbol]?.changePct)}
                </span>
              </div>
            </div>
            <div className="flex gap-2 px-3 pb-3">
              <Link to="/stocks" className="btn flex-1">
                完整个股研究 <ArrowUpRight size={12} />
              </Link>
              <Link
                to="/lab"
                className="btn flex-1"
                onClick={() =>
                  setSymbols([
                    selected.symbol,
                    ...market.stocks
                      .filter((s) => s.symbol !== selected.symbol)
                      .slice(0, 4)
                      .map((s) => s.symbol),
                  ])
                }
              >
                构建组合
              </Link>
            </div>
          </Panel>
          {detail.status === "ready" && detail.data.bars.length > 0 ? (
            <PricePanel data={detail.data} comparison={null} />
          ) : detail.status === "error" ? (
            <ErrorBox error={detail.error} />
          ) : (
            <Loading />
          )}
          {detail.status === "ready" && (
            <Panel title="历史风险画像" subtitle="全可用区间 · 252 日年化">
              <div className="risk-grid">
                {[
                  ["区间收益", percent(detail.data.metrics.totalReturn)],
                  ["年化波动", percent(detail.data.metrics.volatility)],
                  ["最大回撤", percent(detail.data.metrics.maxDrawdown)],
                  ["Sharpe", number(detail.data.metrics.sharpe)],
                ].map(([label, value]) => (
                  <div key={label}>
                    <label>{label}</label>
                    <strong>{value}</strong>
                  </div>
                ))}
              </div>
            </Panel>
          )}
        </div>
      </div>
      <div className="desk-bottom-grid">
        <Panel
          title="板块表现"
          subtitle="当前样本末日涨跌的等权均值；点击筛选观察池"
          action={<span className="panel-code">SECTOR MAP</span>}
        >
          <div className="sector-map">
            {sectors.map((s) => (
              <button
                key={s.name}
                onClick={() =>
                  setSector(sector === s.name ? "全部行业" : s.name)
                }
                aria-pressed={sector === s.name}
                className={`${s.change !== null && s.change >= 0 ? "sector-up" : "sector-down"} ${sector === s.name ? "sector-active" : ""}`}
              >
                <span>{s.name}</span>
                <strong>{s.change === null ? "—" : percent(s.change)}</strong>
                <small>{s.stocks.length} 个标的</small>
              </button>
            ))}
          </div>
        </Panel>
        <Panel
          title="涨跌榜"
          subtitle="样本末日较前日 · 非全市场排行"
          action={<Activity size={14} className="text-slate-500" />}
        >
          <div className="movers-grid">
            {[ranked.slice(0, 4), [...ranked].reverse().slice(0, 4)].map(
              (list, i) => (
                <div key={i}>
                  <div className="movers-label">
                    {i === 0 ? "涨幅排序" : "跌幅排序"}
                  </div>
                  {list.map((s) => (
                    <button
                      key={s.symbol}
                      onClick={() => {
                        selectStock(s.symbol);
                        window.scrollTo({ top: 0, behavior: "smooth" });
                      }}
                    >
                      <strong>{s.symbol}</strong>
                      <span>{number(s.close)}</span>
                      <em
                        className={s.changePct >= 0 ? "positive" : "negative"}
                      >
                        {percent(s.changePct)}
                      </em>
                    </button>
                  ))}
                </div>
              ),
            )}
          </div>
        </Panel>
      </div>
      <details className="data-disclosure">
        <summary>数据范围与来源 · 32 个精选标的 · 点击查看</summary>
        <p>
          由源分钟行情聚合日线，复权状态未知，未计分红；成交量不代表全市场成交量。未提供财报，不展示虚构的估值或财务指标。不同标的可用日期不同，涨跌按各自最后两个观测计算。
        </p>
        <p className="break-all font-mono">
          {market.provenance.release} / {market.provenance.asset} · SHA256{" "}
          {market.provenance.sha256}
        </p>
      </details>
    </>
  );
}
