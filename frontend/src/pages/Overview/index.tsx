import { FieldSettings } from "./components/FieldSettings";
import { RuleBuilder } from "./components/RuleBuilder";
import { ScreenerTable } from "./components/ScreenerTable";
import type { Rule } from "./objects/ScreenerRule";
import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Settings2,
  Download,
  ArrowUpRight,
  PanelBottomClose,
  PanelBottomOpen,
} from "lucide-react";
import {
  useMarket,
  useSelectedStock,
  useWatchlist,
  useSymbols,
} from "../../stores/research";
import { download } from "../../utils/download";
import { useUniverse } from "./hooks/useUniverse";
import { assetType, fields, presets, snapshot } from "./functions/marketMath";
import { SecurityDock } from "./components/SecurityDock";

type Preferences = {
  columns: string[];
  asset: string;
  sector: string;
  onlyWatch: boolean;
  sort: string;
  ascending: boolean;
  dock: boolean;
  density: "compact" | "standard";
};
const initial: Preferences = {
  columns: presets["行情"],
  asset: "全部证券",
  sector: "全部行业",
  onlyWatch: false,
  sort: "symbol",
  ascending: true,
  dock: true,
  density: "compact",
};
function readPreferences(): Preferences {
  try {
    const saved = JSON.parse(
      localStorage.getItem("aperture-screener-v2") || "null",
    );
    return saved
      ? {
          ...initial,
          ...saved,
          columns:
            Array.isArray(saved.columns) &&
            saved.columns.some((id: string) => fields.some((f) => f.id === id))
              ? saved.columns.filter((id: string) =>
                  fields.some((f) => f.id === id),
                )
              : initial.columns,
        }
      : initial;
  } catch {
    return initial;
  }
}
export function OverviewPage() {
  const market = useMarket()!,
    selected = useSelectedStock(),
    watch = useWatchlist(),
    basket = useSymbols(),
    nav = useNavigate();
  const universe = useUniverse(market);
  const [prefs, setPrefs] = useState(readPreferences);
  const change = (update: Partial<Preferences>) =>
    setPrefs((old) => ({ ...old, ...update }));
  const [query, setQuery] = useState(""),
    [settings, setSettings] = useState(false),
    [rules, setRules] = useState<Rule[]>([]),
    [showRules, setShowRules] = useState(false);
  const first = market.stocks.reduce(
      (d, s) => (s.firstDate < d ? s.firstDate : d),
      "9999",
    ),
    last = market.stocks.reduce(
      (d, s) => (s.lastDate > d ? s.lastDate : d),
      "",
    );
  const [start, setStart] = useState(() => {
      const d = new Date(last + "T00:00:00Z");
      d.setUTCFullYear(d.getUTCFullYear() - 1);
      return d.toISOString().slice(0, 10);
    }),
    [end, setEnd] = useState(last);
  useEffect(() => {
    try {
      localStorage.setItem("aperture-screener-v2", JSON.stringify(prefs));
    } catch {
      /* Keep this session usable when browser storage is disabled. */
    }
  }, [prefs]);
  useEffect(() => {
    function key(e: KeyboardEvent) {
      if (e.key === "Escape") setSettings(false);
    }
    window.addEventListener("keydown", key);
    return () => window.removeEventListener("keydown", key);
  }, []);
  const rows = useMemo(
    () =>
      market.stocks.map((stock) => ({
        stock,
        values: snapshot(universe.data[stock.symbol], start, end),
      })),
    [market, universe.data, start, end],
  );
  const columns = prefs.columns
    .map((id) => fields.find((f) => f.id === id)!)
    .filter(Boolean);
  const visible = useMemo(
    () =>
      rows
        .filter(
          ({ stock, values }) =>
            (prefs.asset === "全部证券" || assetType(stock) === prefs.asset) &&
            (prefs.sector === "全部行业" || stock.sector === prefs.sector) &&
            (!prefs.onlyWatch || watch.includes(stock.symbol)) &&
            `${stock.symbol} ${stock.name}`
              .toLowerCase()
              .includes(query.toLowerCase()) &&
            rules.every((rule) => {
              if (rule.value.trim() === "") return true;
              const field = fields.find((f) => f.id === rule.field)!,
                value = values[rule.field],
                limit =
                  Number(rule.value) / (field.format === "percent" ? 100 : 1);
              return (
                value !== undefined &&
                Number.isFinite(limit) &&
                (rule.operator === "gte" ? value >= limit : value <= limit)
              );
            }),
        )
        .sort((a, b) => {
          if (prefs.sort === "symbol")
            return (
              a.stock.symbol.localeCompare(b.stock.symbol) *
              (prefs.ascending ? 1 : -1)
            );
          const av = a.values[prefs.sort],
            bv = b.values[prefs.sort];
          if (av === undefined) return bv === undefined ? 0 : 1;
          if (bv === undefined) return -1;
          return (av - bv) * (prefs.ascending ? 1 : -1);
        }),
    [rows, prefs, watch, query, rules],
  );
  const active =
    market.stocks.find((s) => s.symbol === selected) || market.stocks[0];
  const result = universe.data[active.symbol];
  function sort(id: string) {
    change({
      sort: id,
      ascending: prefs.sort === id ? !prefs.ascending : id === "symbol",
    });
  }
  function exportRows() {
    const headings = [
      "代码",
      "公司",
      "类别",
      "行业",
      ...columns.map((c) => c.label + (c.format === "percent" ? "(%)" : "")),
      "价格日期",
    ];
    const data = visible.map(({ stock, values }) => [
      stock.symbol,
      stock.name,
      assetType(stock),
      stock.sector,
      ...columns.map((c) =>
        values[c.id] === undefined
          ? ""
          : values[c.id]! * (c.format === "percent" ? 100 : 1),
      ),
      universe.data[stock.symbol]?.bars.filter((b) => b.date <= end).at(-1)
        ?.date ?? "",
    ]);
    const text = [headings, ...data]
      .map((row) =>
        row.map((v) => '"' + String(v).replaceAll('"', '""') + '"').join(","),
      )
      .join("\n");
    download("aperture-market.csv", "\uFEFF" + text, "text/csv;charset=utf-8");
  }
  function choosePeriod(period: string) {
    let d = new Date(end + "T00:00:00Z");
    if (!Number.isFinite(d.getTime())) return;
    if (period === "全部") {
      setStart(first);
      return;
    }
    if (period === "YTD") {
      setStart(end.slice(0, 4) + "-01-01");
      return;
    }
    d.setUTCMonth(d.getUTCMonth() - Number(period));
    setStart(d.toISOString().slice(0, 10));
  }
  const invalid = !start || !end || start > end;
  return (
    <div className={`securities-screen density-${prefs.density}`}>
      <h1 className="sr-only">证券筛选</h1>
      <aside className="universe-nav" aria-label="证券范围">
        <div className="universe-heading">证券分类</div>
        {["全部证券", "股票", "ADR", "ETF"].map((type) => (
          <button
            key={type}
            className={prefs.asset === type && !prefs.onlyWatch ? "active" : ""}
            onClick={() => change({ asset: type, onlyWatch: false })}
          >
            <span>{type}</span>
            <small>
              {
                market.stocks.filter(
                  (s) => type === "全部证券" || assetType(s) === type,
                ).length
              }
            </small>
          </button>
        ))}
        <button
          className={prefs.onlyWatch ? "active" : ""}
          onClick={() => change({ onlyWatch: !prefs.onlyWatch })}
        >
          <span>我的自选</span>
          <small>{watch.length}</small>
        </button>
        <div className="universe-heading">行业分类</div>
        {["全部行业", ...new Set(market.stocks.map((s) => s.sector))].map(
          (sector) => (
            <button
              key={sector}
              className={prefs.sector === sector ? "active" : ""}
              onClick={() => change({ sector })}
            >
              <span>{sector}</span>
              <small>
                {
                  market.stocks.filter(
                    (s) => sector === "全部行业" || s.sector === sector,
                  ).length
                }
              </small>
            </button>
          ),
        )}
        <div className="universe-note">
          当前仅导入美股、ADR 与黄金 ETF。A 股、债券、期货等资产尚未导入。
        </div>
      </aside>
      <div className="screen-content">
        <div className="screen-toolbar">
          <select
            aria-label="资产类别"
            value={prefs.asset}
            onChange={(e) => change({ asset: e.target.value })}
          >
            {["全部证券", "股票", "ADR", "ETF"].map((type) => (
              <option key={type}>{type}</option>
            ))}
          </select>
          <input
            aria-label="搜索股票"
            placeholder="代码 / 公司"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="screen-search"
          />
          <select
            aria-label="行业筛选"
            value={prefs.sector}
            onChange={(e) => change({ sector: e.target.value })}
          >
            {["全部行业", ...new Set(market.stocks.map((s) => s.sector))].map(
              (s) => (
                <option key={s}>{s}</option>
              ),
            )}
          </select>
          <span className="toolbar-divider" />
          {Object.keys(presets).map((name) => (
            <button
              key={name}
              className={
                JSON.stringify(prefs.columns) === JSON.stringify(presets[name])
                  ? "active"
                  : ""
              }
              onClick={() => change({ columns: presets[name] })}
            >
              {name}
            </button>
          ))}
          <button
            onClick={() => setSettings(!settings)}
            aria-expanded={settings}
          >
            <Settings2 size={12} />
            字段设置
          </button>
          <button
            onClick={() => setShowRules(!showRules)}
            aria-expanded={showRules}
          >
            条件筛选{rules.length > 0 ? ` (${rules.length})` : ""}
          </button>
          <button onClick={exportRows} aria-label="导出行情 CSV">
            <Download size={12} />
            导出
          </button>
          <button
            onClick={() => change({ dock: !prefs.dock })}
            aria-label={prefs.dock ? "隐藏联动图表" : "显示联动图表"}
          >
            {prefs.dock ? (
              <PanelBottomClose size={13} />
            ) : (
              <PanelBottomOpen size={13} />
            )}
          </button>
        </div>
        <div className="screen-period">
          <label>统计区间（日频）</label>
          <input
            aria-label="筛选起始日期"
            type="date"
            value={start}
            onChange={(e) => setStart(e.target.value)}
          />
          <span>—</span>
          <input
            aria-label="筛选截止日期"
            type="date"
            value={end}
            onChange={(e) => setEnd(e.target.value)}
          />
          {[
            ["1M", "1"],
            ["3M", "3"],
            ["1Y", "12"],
            ["YTD", "YTD"],
            ["全部", "全部"],
          ].map(([label, value]) => (
            <button key={label} onClick={() => choosePeriod(value)}>
              {label}
            </button>
          ))}
          <span className="ml-auto" />
          <label>行高</label>
          <select
            aria-label="显示密度"
            value={prefs.density}
            onChange={(e) =>
              change({ density: e.target.value as Preferences["density"] })
            }
          >
            <option value="compact">紧凑</option>
            <option value="standard">标准</option>
          </select>
          <button
            className="basket-action"
            disabled={basket.length < 2}
            onClick={() => nav("/lab")}
          >
            组合优化 ({basket.length}) <ArrowUpRight size={11} />
          </button>
        </div>
        {showRules && <RuleBuilder rules={rules} setRules={setRules} />}
        {invalid && (
          <div className="screen-error" role="alert">
            起始日期不能晚于截止日期。
          </div>
        )}
        <ScreenerTable
          rows={visible}
          columns={columns}
          data={universe.data}
          end={end}
          invalid={invalid}
          sortKey={prefs.sort}
          ascending={prefs.ascending}
          sort={sort}
        />{" "}
        <div className="screen-table-status">
          <span>
            {visible.length} / {market.stocks.length} 个证券
          </span>
          <span role="status">
            指标 {Object.keys(universe.data).length} / {market.stocks.length}
            {universe.errors.length > 0
              ? ` · ${universe.errors.length} 个失败`
              : ""}
          </span>
          {universe.errors.length > 0 && (
            <button onClick={universe.retry}>重试</button>
          )}
          <span>选中 {active.symbol} · 双击查看完整分析</span>
          <span className="ml-auto">
            百分比字段以 % 显示 · — 表示不足或缺失
          </span>
        </div>
        {prefs.dock && (
          <SecurityDock stock={active} data={result} start={start} end={end} />
        )}
      </div>
      {settings && (
        <FieldSettings
          ids={prefs.columns}
          onChange={(columns) => change({ columns })}
          close={() => setSettings(false)}
        />
      )}
    </div>
  );
}
