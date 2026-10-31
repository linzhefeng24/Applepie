import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Star, ArrowUpRight } from "lucide-react";
import type { StockResult } from "../../../objects/market";
import {
  useWatchlist,
  useSymbols,
  useSelectedStock,
  setSymbols,
  selectStock,
  setWatchlist,
} from "../../../stores/research";
import { SetWatchlistMessage } from "../../../apis/watchlist/SetWatchlistMessage";
import { ErrorBox } from "../../../components/ui/Panel";
import { number, percent, compact } from "../../../utils/format";
import { assetType, type Field } from "../functions/marketMath";
import type { ScreenerRow } from "../objects/ScreenerRow";
export function ScreenerTable({
  rows,
  columns,
  data,
  end,
  invalid,
  sortKey,
  ascending,
  sort,
}: {
  rows: ScreenerRow[];
  columns: Field[];
  data: Record<string, StockResult>;
  end: string;
  invalid: boolean;
  sortKey: string;
  ascending: boolean;
  sort: (id: string) => void;
}) {
  const watch = useWatchlist(),
    basket = useSymbols(),
    selected = useSelectedStock(),
    nav = useNavigate();
  const [busy, setBusy] = useState(false),
    [error, setError] = useState("");
  function format(field: Field, value: number | undefined) {
    return value === undefined
      ? "—"
      : field.format === "percent"
        ? percent(value)
        : field.format === "volume"
          ? compact(value)
          : number(value, field.id === "observations" ? 0 : 2);
  }
  async function toggleWatch(symbol: string) {
    setBusy(true);
    setError("");
    try {
      setWatchlist(
        (await new SetWatchlistMessage(symbol, !watch.includes(symbol)).send())
          .symbols,
      );
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <>
      {error && <ErrorBox error={error} />}
      <div
        className="screen-table-scroll"
        role="region"
        aria-label="证券数据表"
        tabIndex={0}
      >
        <table className="screen-table">
          <thead>
            <tr>
              <th className="row-number">#</th>
              <th className="basket-column" title="选择组合成分">
                组合
              </th>
              <th className="star-column" />
              <th
                className="symbol-column"
                aria-sort={
                  sortKey === "symbol"
                    ? ascending
                      ? "ascending"
                      : "descending"
                    : "none"
                }
              >
                <button onClick={() => sort("symbol")}>
                  代码 {sortKey === "symbol" ? (ascending ? "↑" : "↓") : ""}
                </button>
              </th>
              <th className="name-column">公司</th>
              <th>类别</th>
              <th>行业</th>
              {columns.map((f) => (
                <th
                  key={f.id}
                  aria-sort={
                    sortKey === f.id
                      ? ascending
                        ? "ascending"
                        : "descending"
                      : "none"
                  }
                  title={f.description}
                >
                  <button onClick={() => sort(f.id)}>
                    {f.label}
                    {sortKey === f.id ? (ascending ? " ↑" : " ↓") : ""}
                  </button>
                </th>
              ))}
              <th>价格日期</th>
              <th />
            </tr>
          </thead>
          <tbody>
            {!invalid &&
              rows.map(({ stock, values }, i) => (
                <tr
                  key={stock.symbol}
                  aria-selected={selected === stock.symbol}
                  className={selected === stock.symbol ? "selected" : ""}
                  onClick={() => selectStock(stock.symbol)}
                  onDoubleClick={() => {
                    selectStock(stock.symbol);
                    nav("/stocks");
                  }}
                >
                  <td className="row-number">{i + 1}</td>
                  <td className="basket-column">
                    <input
                      aria-label={`组合成分 ${stock.symbol}`}
                      type="checkbox"
                      checked={basket.includes(stock.symbol)}
                      disabled={
                        !basket.includes(stock.symbol) && basket.length >= 10
                      }
                      onClick={(e) => e.stopPropagation()}
                      onChange={() =>
                        setSymbols(
                          basket.includes(stock.symbol)
                            ? basket.filter((s) => s !== stock.symbol)
                            : [...basket, stock.symbol],
                        )
                      }
                    />
                  </td>
                  <td className="star-column">
                    <button
                      aria-label={`${watch.includes(stock.symbol) ? "移除" : "添加"}自选 ${stock.symbol}`}
                      disabled={busy}
                      onClick={(e) => {
                        e.stopPropagation();
                        toggleWatch(stock.symbol);
                      }}
                      className={
                        watch.includes(stock.symbol) ? "star-selected" : ""
                      }
                    >
                      <Star
                        size={10}
                        fill={
                          watch.includes(stock.symbol) ? "currentColor" : "none"
                        }
                      />
                    </button>
                  </td>
                  <td className="symbol-column">
                    <button onClick={() => selectStock(stock.symbol)}>
                      {stock.symbol}
                    </button>
                  </td>
                  <td className="name-column" title={stock.name}>
                    {stock.name}
                  </td>
                  <td>{assetType(stock)}</td>
                  <td>{stock.sector}</td>
                  {columns.map((f) => (
                    <td
                      key={f.id}
                      data-field={f.id}
                      className={`numeric ${f.signed && values[f.id] !== undefined ? (values[f.id]! >= 0 ? "positive" : "negative") : ""}`}
                    >
                      {format(f, values[f.id])}
                    </td>
                  ))}
                  <td className="data-date">
                    {data[stock.symbol]?.bars
                      .filter((b) => b.date <= end)
                      .at(-1)?.date ?? "—"}
                  </td>
                  <td>
                    <button
                      aria-label={`研究 ${stock.symbol}`}
                      onClick={() => {
                        selectStock(stock.symbol);
                        nav("/stocks");
                      }}
                    >
                      <ArrowUpRight size={10} />
                    </button>
                  </td>
                </tr>
              ))}
          </tbody>
        </table>
        {!rows.length && !invalid && (
          <div className="screen-empty">
            没有符合条件的证券
            {Object.keys(data).length === 0 ? "，指标正在载入…" : "。"}
          </div>
        )}
      </div>
    </>
  );
}
