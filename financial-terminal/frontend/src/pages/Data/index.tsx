import { useMemo, useState } from "react";
import { useMarket, useSelectedStock, useSymbols } from "../../stores/research";
import { useUniverse } from "../Overview/hooks/useUniverse";
import { technical, assetType } from "../Overview/functions/marketMath";
import { download } from "../../utils/download";
import { number } from "../../utils/format";
import { ErrorBox } from "../../components/ui/Panel";
export function DataPage() {
  const market = useMarket()!,
    active = useSelectedStock(),
    basket = useSymbols(),
    universe = useUniverse(market);
  const [selected, setSelected] = useState([active]),
    [tab, setTab] = useState("历史数据"),
    [include, setInclude] = useState(false),
    [page, setPage] = useState(0),
    [format, setFormat] = useState("CSV"),
    [message, setMessage] = useState("");
  const first = market.stocks.reduce(
      (d, s) => (s.firstDate < d ? s.firstDate : d),
      "9999",
    ),
    last = market.stocks.reduce(
      (d, s) => (s.lastDate > d ? s.lastDate : d),
      "",
    );
  const [start, setStart] = useState(first),
    [end, setEnd] = useState(last);
  const invalid = !start || !end || start > end;
  const records = useMemo(
    () =>
      market.stocks
        .filter((s) => selected.includes(s.symbol))
        .flatMap((stock) => {
          const history = universe.data[stock.symbol]?.bars || [],
            t = include ? technical(history) : null;
          return history.flatMap((bar, i) =>
            bar.date >= start && bar.date <= end
              ? [
                  {
                    symbol: stock.symbol,
                    ...bar,
                    ...(t
                      ? { ma20: t.ma20[i], ma60: t.ma60[i], rsi14: t.rsi[i] }
                      : {}),
                  },
                ]
              : [],
          );
        }),
    [market, selected, universe.data, start, end, include],
  );
  const ready =
    selected.every((s) => universe.data[s]) && selected.length > 0 && !invalid;
  const display = useMemo(
    () =>
      [...records].sort(
        (a, b) =>
          b.date.localeCompare(a.date) || a.symbol.localeCompare(b.symbol),
      ),
    [records],
  );
  const pages = Math.max(1, Math.ceil(display.length / 100)),
    current = Math.min(page, pages - 1);
  const headers = [
    "symbol",
    "date",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "minutes",
    ...(include ? ["ma20", "ma60", "rsi14"] : []),
  ];
  function exportData() {
    if (!ready) return;
    const base = `aperture-history-${selected.length === 1 ? selected[0] : "multi"}-${start}-${end}`;
    if (format === "JSON") {
      download(
        base + ".json",
        JSON.stringify(
          {
            query: {
              symbols: selected,
              start,
              end,
              includeIndicators: include,
            },
            provenance: market.provenance,
            rows: records,
          },
          null,
          2,
        ),
        "application/json",
      );
      return;
    }
    const csv = [
      headers,
      ...records.map((row) =>
        headers.map(
          (key) => (row as unknown as Record<string, unknown>)[key] ?? "",
        ),
      ),
    ]
      .map((row) =>
        row
          .map((value) => '"' + String(value).replaceAll('"', '""') + '"')
          .join(","),
      )
      .join("\n");
    download(base + ".csv", "\uFEFF" + csv, "text/csv;charset=utf-8");
  }
  const request = { symbol: selected[0] || active, start, end },
    example = `curl '${location.origin}/api/statistics/getstock' \\\n  -H 'Content-Type: application/json' \\\n  --data '${JSON.stringify(request)}'`;
  return (
    <div className="data-workspace">
      <h1 className="sr-only">数据中心</h1>
      <aside className="data-securities">
        <div className="universe-heading">导出证券 / {selected.length}</div>
        <div className="data-selection-actions">
          <button
            onClick={() => {
              setSelected(market.stocks.map((s) => s.symbol));
              setPage(0);
            }}
          >
            全选
          </button>
          <button
            onClick={() => {
              setSelected([]);
              setPage(0);
            }}
          >
            清空
          </button>
          <button
            onClick={() => {
              setSelected(basket);
              setPage(0);
            }}
          >
            组合成分
          </button>
        </div>
        {market.stocks.map((s) => (
          <label key={s.symbol}>
            <input
              type="checkbox"
              aria-label={`下载 ${s.symbol}`}
              checked={selected.includes(s.symbol)}
              onChange={() => {
                setSelected((list) =>
                  list.includes(s.symbol)
                    ? list.filter((x) => x !== s.symbol)
                    : [...list, s.symbol],
                );
                setPage(0);
              }}
            />
            <strong>{s.symbol}</strong>
            <small>{assetType(s)}</small>
          </label>
        ))}
      </aside>
      <div className="data-main">
        <nav className="data-tabs">
          {["历史数据", "数据质量", "API 访问"].map((t) => (
            <button
              key={t}
              className={tab === t ? "active" : ""}
              onClick={() => setTab(t)}
            >
              {t}
            </button>
          ))}
        </nav>
        <div className="screen-toolbar">
          <label>起始</label>
          <input
            aria-label="数据起始日期"
            type="date"
            value={start}
            onChange={(e) => {
              setStart(e.target.value);
              setPage(0);
            }}
          />
          <label>截止</label>
          <input
            aria-label="数据截止日期"
            type="date"
            value={end}
            onChange={(e) => {
              setEnd(e.target.value);
              setPage(0);
            }}
          />
          <label className="data-indicator-check">
            <input
              aria-label="包含技术指标"
              type="checkbox"
              checked={include}
              onChange={(e) => setInclude(e.target.checked)}
            />
            附加 MA20 / MA60 / RSI14
          </label>
          <span className="ml-auto" />
          <select
            aria-label="数据下载格式"
            value={format}
            onChange={(e) => setFormat(e.target.value)}
          >
            <option>CSV</option>
            <option>JSON</option>
          </select>
          <button
            disabled={!ready}
            className="data-download"
            onClick={exportData}
          >
            下载数据 ({records.length.toLocaleString()})
          </button>
        </div>
        {invalid && <ErrorBox error="起始日期不能晚于截止日期。" />}
        {universe.errors.length > 0 && (
          <div className="screen-error">
            {universe.errors.join(", ")} 读取失败{" "}
            <button onClick={universe.retry}>重试</button>
          </div>
        )}
        {tab === "历史数据" ? (
          <>
            <div className="data-grid-scroll">
              <table className="screen-table">
                <thead>
                  <tr>
                    {headers.map((h) => (
                      <th key={h}>{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {!invalid &&
                    display
                      .slice(current * 100, (current + 1) * 100)
                      .map((row) => (
                        <tr key={row.symbol + row.date}>
                          {headers.map((key) => {
                            const value = (
                              row as unknown as Record<string, unknown>
                            )[key];
                            return (
                              <td key={key}>
                                {value === null || value === undefined
                                  ? "—"
                                  : typeof value === "number"
                                    ? number(
                                        value,
                                        ["volume", "minutes"].includes(key)
                                          ? 0
                                          : 4,
                                      )
                                    : String(value)}
                              </td>
                            );
                          })}
                        </tr>
                      ))}
                </tbody>
              </table>
              {!display.length && (
                <div className="screen-empty">
                  {ready
                    ? "当前区间没有记录"
                    : selected.length
                      ? "数据载入中…"
                      : "请选择证券"}
                </div>
              )}
            </div>
            <div className="screen-table-status">
              <span>
                {records.length.toLocaleString()} 行 · {selected.length} 个证券
              </span>
              <span>下载保留原始精度；界面价格显示4位小数</span>
              <span className="ml-auto" />
              <button
                disabled={current === 0}
                onClick={() => setPage(current - 1)}
              >
                上一页
              </button>
              <span>
                {current + 1} / {pages}
              </span>
              <button
                disabled={current + 1 >= pages}
                onClick={() => setPage(current + 1)}
              >
                下一页
              </button>
            </div>
          </>
        ) : tab === "数据质量" ? (
          <div className="data-quality">
            <div className="data-source">
              <strong>来源与计算口径</strong>
              <p>
                源分钟聚合日线；未知复权，未含分红。技术指标使用区间前历史预热，数据不足显示
                —。导出不进行插值或前向填充。
              </p>
              <p>
                当前数据库：{market.stocks.length} 个证券 /{" "}
                {market.provenance.rows.toLocaleString()} 条日线。
              </p>
              <p>
                源压缩包 SHA256：<code>{market.provenance.sha256}</code>
              </p>
              <a
                href={
                  market.provenance.release.startsWith("https://github.com/")
                    ? market.provenance.release
                    : undefined
                }
                target="_blank"
                rel="noreferrer"
              >
                访问源数据 Release / {market.provenance.asset} ↗
              </a>
              <button
                onClick={() =>
                  download(
                    "aperture-provenance.json",
                    JSON.stringify(market.provenance, null, 2),
                    "application/json",
                  )
                }
              >
                下载数据来源与审计 JSON
              </button>
            </div>
            <table className="screen-table">
              <thead>
                <tr>
                  <th>证券</th>
                  <th>原始分钟</th>
                  <th>重复记录</th>
                  <th>拒绝记录</th>
                  <th>日线数</th>
                  <th>不足300分钟日</th>
                  <th>日变动超过25%</th>
                  <th>来源</th>
                </tr>
              </thead>
              <tbody>
                {market.provenance.audits.map((a) => (
                  <tr key={a.symbol}>
                    <td>{a.symbol}</td>
                    <td>{a.rawMinutes.toLocaleString()}</td>
                    <td>{a.duplicates}</td>
                    <td>{a.rejectedMinutes}</td>
                    <td>{a.dailyRows}</td>
                    <td>{a.sessionsUnder300Minutes}</td>
                    <td>{a.dailyMovesOver25Pct}</td>
                    <td>{a.sources.join(", ")}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="api-reference">
            <h2>本地数据访问</h2>
            <div className="api-spec-links">
              {[
                "market",
                "history",
                "statistics",
                "watchlist",
                "reports",
                "optimization",
                "backtest",
              ].map((service) => (
                <a
                  key={service}
                  href={`/api/${service}/openapi.json`}
                  target="_blank"
                  rel="noreferrer"
                >
                  {service} / OpenAPI ↗
                </a>
              ))}
            </div>
            <p>
              在应用运行期间可通过同源 HTTP
              接口查询。不需要数据库密码。下列请求读取当前所选证券的价格、区间统计与年度指标。
            </p>
            <pre>{example}</pre>
            <button
              onClick={async () => {
                try {
                  await navigator.clipboard.writeText(example);
                  setMessage("已复制请求");
                } catch {
                  setMessage("无法自动复制，请选择上面的请求文本复制。");
                }
              }}
            >
              复制请求
            </button>
            <span>{message}</span>
            <table>
              <thead>
                <tr>
                  <th>POST 路径</th>
                  <th>输入</th>
                  <th>输出</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>/api/market/liststocks</td>
                  <td>{"{}"}</td>
                  <td>证券、末日行情、数据来源</td>
                </tr>
                <tr>
                  <td>/api/statistics/getstock</td>
                  <td>symbol, start, end</td>
                  <td>OHLCV、风险收益统计、年度指标</td>
                </tr>
                <tr>
                  <td>/api/history/getprices</td>
                  <td>symbols, start, end</td>
                  <td>多证券历史价格</td>
                </tr>
                <tr>
                  <td>/api/reports/listreports</td>
                  <td>{"{}"}</td>
                  <td>已保存的分析与回测结果</td>
                </tr>
              </tbody>
            </table>
            <p>
              此处仅提供只读查询示例。组合计算和回测可在对应工作区运行，结果可导出
              JSON / Markdown / CSV。
            </p>
          </div>
        )}
        <div className="data-footer">
          指标载入 {Object.keys(universe.data).length} / {market.stocks.length}{" "}
          · 数据为历史研究样本 · 不含财报、新闻、盘口或实时交易接口
        </div>
      </div>
    </div>
  );
}
