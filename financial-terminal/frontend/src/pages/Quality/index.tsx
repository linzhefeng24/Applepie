import { useState } from "react";
import { useMarket } from "../../stores/research";
import { download } from "../../utils/download";
export function QualityPage() {
  const market = useMarket()!,
    [query, setQuery] = useState(""),
    [flagged, setFlagged] = useState(false);
  const p = market.provenance;
  const rows = p.audits.filter(
    (a) =>
      a.symbol.toLowerCase().includes(query.toLowerCase()) &&
      (!flagged ||
        a.rejectedMinutes > 0 ||
        a.duplicates > 0 ||
        a.sessionsUnder300Minutes > 0 ||
        a.dailyMovesOver25Pct > 0),
  );
  return (
    <section className="space-y-4">
      <div className="flex justify-between">
        <div>
          <h1 className="text-lg">数据质量审计</h1>
          <p className="text-xs text-slate-500">
            源数据清理记录、异常标记与可追溯来源
          </p>
        </div>
        <button
          onClick={() =>
            download(
              "data-quality-audit.json",
              JSON.stringify({ ...p, audits: rows }, null, 2),
              "application/json",
            )
          }
        >
          导出审计 JSON
        </button>
      </div>
      <div className="flex flex-wrap gap-5 text-xs">
        <label>
          审计证券{" "}
          <input
            aria-label="审计证券"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="例如 AAPL"
          />
        </label>
        <label>
          <input
            type="checkbox"
            checked={flagged}
            onChange={(e) => setFlagged(e.target.checked)}
          />{" "}
          仅显示有质量标记的证券
        </label>
        <span>
          显示 {rows.length} / {p.audits.length} 个证券
        </span>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-xs">
          <thead>
            <tr>
              <th>证券</th>
              <th>原始分钟记录</th>
              <th>剔除无效记录</th>
              <th>重复时间戳</th>
              <th>日线数</th>
              <th>不足300分钟日</th>
              <th>涨跌超过25%日</th>
              <th>源</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((a) => (
              <tr key={a.symbol}>
                <td>{a.symbol}</td>
                <td>{a.rawMinutes.toLocaleString()}</td>
                <td>{a.rejectedMinutes}</td>
                <td>{a.duplicates}</td>
                <td>{a.dailyRows}</td>
                <td>{a.sessionsUnder300Minutes}</td>
                <td>{a.dailyMovesOver25Pct}</td>
                <td>{a.sources.join(", ")}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {!rows.length && <p>没有匹配的审计记录。</p>}
      <dl className="space-y-3 text-xs text-slate-400">
        <dt>来源文件</dt>
        <dd>
          {p.asset} · {p.symbols} 个证券 · {p.rows.toLocaleString()} 条日线
        </dd>
        <dt>源压缩包 SHA256</dt>
        <dd className="break-all font-mono">{p.sha256}</dd>
        <dt>复权说明</dt>
        <dd>{p.adjustment}</dd>
        <dt>成交量口径</dt>
        <dd>{p.volume}</dd>
        <dt>时间戳口径</dt>
        <dd>{p.timezone}</dd>
      </dl>
      <p className="text-xs text-amber-200">
        此审计来自完整源分钟到日线的清理过程；默认安装包仅附最近60个记录交易日的分钟子集。异常标记用于复核，不代表已修正复权或填补缺失。
      </p>
      {p.release.startsWith("https://github.com/") && (
        <a
          className="text-blue-400 text-xs"
          href={p.release}
          target="_blank"
          rel="noreferrer"
        >
          访问原始数据 Release ↗
        </a>
      )}
    </section>
  );
}
