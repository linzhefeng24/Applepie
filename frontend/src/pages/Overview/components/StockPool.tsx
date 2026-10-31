import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Search,
  ArrowUpRight,
  Star,
  Download,
  ArrowDownUp,
} from "lucide-react";
import {
  useMarket,
  useWatchlist,
  setWatchlist,
  selectStock,
  useSelectedStock,
} from "../../../stores/research";
import { SetWatchlistMessage } from "../../../apis/portfolio/SetWatchlistMessage";
import { Panel, ErrorBox, Empty, Tag } from "../../../components/ui/Panel";
import { number, percent, compact } from "../../../utils/format";
export function StockPool({
  sector,
  setSector,
}: {
  sector: string;
  setSector: (value: string) => void;
}) {
  const selected = useSelectedStock();
  const [sort, setSort] = useState("symbol");
  const [ascending, setAscending] = useState(true);
  const market = useMarket()!;
  const watch = useWatchlist();
  const [q, setQ] = useState("");
  const [onlyWatch, setOnlyWatch] = useState(false);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState<string | null>(null);
  const nav = useNavigate();
  const stocks = useMemo(
    () =>
      [...market.stocks]
        .sort((a, b) => {
          const qa = market.quotes[a.symbol],
            qb = market.quotes[b.symbol];
          const value =
            sort === "symbol"
              ? a.symbol.localeCompare(b.symbol)
              : sort === "close"
                ? (qa?.close || 0) - (qb?.close || 0)
                : sort === "volume"
                  ? (qa?.volume || 0) - (qb?.volume || 0)
                  : (qa?.changePct || 0) - (qb?.changePct || 0);
          return ascending ? value : -value;
        })
        .filter(
          (s) =>
            (!onlyWatch || watch.includes(s.symbol)) &&
            (sector === "全部行业" || s.sector === sector) &&
            `${s.symbol} ${s.name}`.toLowerCase().includes(q.toLowerCase()),
        ),
    [market, q, sector, onlyWatch, watch, sort, ascending],
  );
  async function toggle(symbol: string) {
    setBusy(symbol);
    setError("");
    try {
      setWatchlist(
        (await new SetWatchlistMessage(symbol, !watch.includes(symbol)).send())
          .symbols,
      );
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(null);
    }
  }
  function exportRows() {
    const csv =
      "\uFEFF代码,公司,行业,收盘价,涨跌幅(%),源成交量,数据日\n" +
      stocks
        .map((s) => {
          const quote = market.quotes[s.symbol];
          return [
            s.symbol,
            s.name,
            s.sector,
            quote?.close,
            quote ? quote.changePct * 100 : undefined,
            quote?.volume,
            quote?.date,
          ]
            .map((v) => '"' + String(v ?? "").replaceAll('"', '""') + '"')
            .join(",");
        })
        .join("\n");
    const a = document.createElement("a");
    a.href = URL.createObjectURL(
      new Blob([csv], { type: "text/csv;charset=utf-8" }),
    );
    a.download = "aperture-market.csv";
    a.click();
    setTimeout(() => URL.revokeObjectURL(a.href), 1000);
  }
  function column(key: string, label: string) {
    return (
      <button
        onClick={() => {
          setSort(key);
          setAscending(sort === key ? !ascending : key === "symbol");
        }}
        className="sort-heading"
      >
        {label}
        <ArrowDownUp size={10} />
        {sort === key ? <span>{ascending ? "↑" : "↓"}</span> : null}
      </button>
    );
  }
  return (
    <Panel
      title="行情观察池"
      subtitle="点击行联动图表 · 点击代码进入研究"
      action={
        <div className="flex gap-2">
          <button
            className={`btn ${onlyWatch ? "!text-[#b7ed77]" : ""}`}
            onClick={() => setOnlyWatch(!onlyWatch)}
          >
            <Star size={12} />
            {onlyWatch ? "我的自选" : "全部标的"}
          </button>
          <button
            className="btn"
            aria-label="导出行情 CSV"
            onClick={exportRows}
          >
            <Download size={12} /> CSV
          </button>
          <Tag>{stocks.length} SYMBOLS</Tag>
        </div>
      }
    >
      <div className="flex flex-wrap gap-3 border-b border-white/[.05] px-5 pb-4">
        <label className="relative flex-1">
          <Search size={14} className="absolute left-3 top-3 text-slate-500" />
          <input
            aria-label="搜索股票"
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="搜索股票代码 / 公司名称"
            className="w-full pl-9"
          />
        </label>
        <select
          aria-label="行业筛选"
          value={sector}
          onChange={(e) => setSector(e.target.value)}
        >
          {["全部行业", ...new Set(market.stocks.map((s) => s.sector))].map(
            (s) => (
              <option key={s}>{s}</option>
            ),
          )}
        </select>
      </div>
      {error && <ErrorBox error={error} />}
      <div className="table-scroll quote-table-scroll">
        <table className="w-full">
          <thead>
            <tr>
              <th></th>
              <th>{column("symbol", "标的 / SYMBOL")}</th>
              <th>行业</th>
              <th>{column("close", "收盘 / USD")}</th>
              <th>{column("change", "涨跌幅")}</th>
              <th>{column("volume", "源成交量")}</th>
              <th>交易日</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {stocks.map((s) => {
              const quote = market.quotes[s.symbol];
              return (
                <tr
                  key={s.symbol}
                  className={`quote-row ${selected === s.symbol ? "selected" : ""}`}
                  onClick={() => selectStock(s.symbol)}
                >
                  <td>
                    <button
                      aria-label={`${watch.includes(s.symbol) ? "移除" : "添加"}自选 ${s.symbol}`}
                      disabled={busy !== null}
                      onClick={(e) => {
                        e.stopPropagation();
                        toggle(s.symbol);
                      }}
                      className={
                        watch.includes(s.symbol)
                          ? "text-[#b7ed77]"
                          : "text-slate-700 hover:text-slate-400"
                      }
                    >
                      <Star
                        size={13}
                        fill={
                          watch.includes(s.symbol) ? "currentColor" : "none"
                        }
                      />
                    </button>
                  </td>
                  <td>
                    <button
                      onClick={() => {
                        selectStock(s.symbol);
                        nav("/stocks");
                      }}
                      className="text-left"
                    >
                      <span className="font-mono font-semibold text-slate-100">
                        {s.symbol}
                      </span>
                      <div className="mt-1 text-[10px] text-slate-500">
                        {s.name}
                      </div>
                    </button>
                  </td>
                  <td className="text-slate-500">{s.sector}</td>
                  <td className="font-mono text-slate-200">
                    {number(quote?.close)}
                  </td>
                  <td
                    className={`font-mono ${quote?.changePct >= 0 ? "text-[#55c9a3]" : "text-rose-300"}`}
                  >
                    {quote?.changePct >= 0 ? "+" : ""}
                    {percent(quote?.changePct)}
                  </td>
                  <td className="font-mono text-slate-500">
                    {quote ? compact(quote.volume) : "—"}
                  </td>
                  <td className="font-mono text-[10px] text-slate-500">
                    {quote?.date}
                  </td>
                  <td>
                    <button
                      aria-label={`研究 ${s.symbol}`}
                      onClick={() => {
                        selectStock(s.symbol);
                        nav("/stocks");
                      }}
                      className="text-slate-600 hover:text-[#b7ed77]"
                    >
                      <ArrowUpRight size={14} />
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
        {!stocks.length && <Empty text="没有符合条件的标的，试试调整筛选。" />}
      </div>
    </Panel>
  );
}
