import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Search, ArrowUpRight, Star } from "lucide-react";
import {
  useMarket,
  useWatchlist,
  setWatchlist,
  selectStock,
} from "../../../stores/research";
import { SetWatchlistMessage } from "../../../apis/portfolio/SetWatchlistMessage";
import { Panel, ErrorBox, Empty, Tag } from "../../../components/ui/Panel";
import { number, percent, compact } from "../../../utils/format";
export function StockPool() {
  const market = useMarket()!;
  const watch = useWatchlist();
  const [q, setQ] = useState("");
  const [sector, setSector] = useState("全部行业");
  const [onlyWatch, setOnlyWatch] = useState(false);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState<string | null>(null);
  const nav = useNavigate();
  const stocks = useMemo(
    () =>
      market.stocks.filter(
        (s) =>
          (!onlyWatch || watch.includes(s.symbol)) &&
          (sector === "全部行业" || s.sector === sector) &&
          `${s.symbol} ${s.name}`.toLowerCase().includes(q.toLowerCase()),
      ),
    [market, q, sector, onlyWatch, watch],
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
  return (
    <Panel
      title="股票观察池"
      subtitle="最后一个可用交易日的源行情 · 非实时价格"
      action={
        <div className="flex gap-2">
          <button
            className={`btn ${onlyWatch ? "!text-[#b7ed77]" : ""}`}
            onClick={() => setOnlyWatch(!onlyWatch)}
          >
            <Star size={12} />
            {onlyWatch ? "我的自选" : "全部标的"}
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
      <div className="table-scroll">
        <table className="w-full">
          <thead>
            <tr>
              <th></th>
              <th>标的 / SYMBOL</th>
              <th>行业</th>
              <th>最新源价格 / USD</th>
              <th>较前日</th>
              <th>源成交量</th>
              <th>交易日</th>
              <th>历史记录</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {stocks.map((s) => {
              const quote = market.quotes[s.symbol];
              return (
                <tr key={s.symbol} className="group hover:bg-white/[.025]">
                  <td>
                    <button
                      aria-label={`${watch.includes(s.symbol) ? "移除" : "添加"}自选 ${s.symbol}`}
                      disabled={busy !== null}
                      onClick={() => toggle(s.symbol)}
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
                    className={`font-mono ${quote?.changePct >= 0 ? "text-[#b7ed77]" : "text-rose-300"}`}
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
                  <td className="font-mono text-slate-500">{s.sessions} 日</td>
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
