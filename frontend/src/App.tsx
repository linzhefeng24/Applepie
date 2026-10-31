import { useEffect, useState } from "react";
import {
  NavLink,
  Routes,
  Route,
  useLocation,
  Link,
  useNavigate,
} from "react-router-dom";
import {
  Aperture,
  LayoutDashboard,
  ChartNoAxesCombined,
  FlaskConical,
  History,
  Files,
  Database,
  Menu,
  Search,
  Command,
} from "lucide-react";
import { CommandSearch } from "./components/CommandSearch";
import { selectStock } from "./stores/research";
import { number, percent } from "./utils/format";
import { ListStocksMessage } from "./apis/market/ListStocksMessage";
import { ListWatchlistMessage } from "./apis/portfolio/ListWatchlistMessage";
import { setMarket, setWatchlist, useMarket } from "./stores/research";
import { ErrorBox, Loading } from "./components/ui/Panel";
import { OverviewPage } from "./pages/Overview";
import { StockPage } from "./pages/Stock";
import { LabPage } from "./pages/Lab";
import { BacktestPage } from "./pages/Backtest";
import { ReportsPage } from "./pages/Reports";
const navigation = [
  {
    path: "/",
    name: "行情工作台",
    en: "Market monitor",
    icon: LayoutDashboard,
  },
  {
    path: "/stocks",
    name: "个股研究",
    en: "Market research",
    icon: ChartNoAxesCombined,
  },
  {
    path: "/lab",
    name: "量化实验室",
    en: "Quant laboratory",
    icon: FlaskConical,
  },
  { path: "/backtest", name: "策略回测", en: "Backtesting", icon: History },
  { path: "/reports", name: "研究档案", en: "Research archive", icon: Files },
];
export function App() {
  const market = useMarket();
  const [error, setError] = useState("");
  const [watchError, setWatchError] = useState("");
  const [menu, setMenu] = useState(false);
  const [nonce, setNonce] = useState(0);
  const location = useLocation();
  useEffect(() => {
    setMenu(false);
  }, [location.pathname]);
  useEffect(() => {
    const abort = new AbortController();
    setError("");
    new ListStocksMessage()
      .send(abort.signal)
      .then(setMarket)
      .catch((e) => {
        if (e.name !== "AbortError") setError(e.message);
      });
    new ListWatchlistMessage()
      .send(abort.signal)
      .then((r) => setWatchlist(r.symbols))
      .catch((e) => {
        if (e.name !== "AbortError")
          setWatchError("自选服务暂不可用：" + e.message);
      });
    return () => abort.abort();
  }, [nonce]);
  const navigate = useNavigate();
  const [command, setCommand] = useState(false);
  const [now, setNow] = useState(new Date());
  useEffect(() => {
    const timer = window.setInterval(() => setNow(new Date()), 1000);
    function keys(event: KeyboardEvent) {
      if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        setCommand((v) => !v);
      }
      if (event.altKey && /^[1-5]$/.test(event.key)) {
        event.preventDefault();
        navigate(navigation[Number(event.key) - 1].path);
      }
    }
    window.addEventListener("keydown", keys);
    return () => {
      clearInterval(timer);
      window.removeEventListener("keydown", keys);
    };
  }, [navigate]);
  const last = market?.stocks.reduce(
    (date, s) => (s.lastDate > date ? s.lastDate : date),
    "",
  );
  return (
    <div className="terminal-shell">
      {command && <CommandSearch close={() => setCommand(false)} />}
      <header className="terminal-topbar">
        <Link to="/" className="terminal-brand">
          <Aperture size={22} />
          <strong>
            APERTURE<span>TERMINAL</span>
          </strong>
        </Link>
        <button className="terminal-search" onClick={() => setCommand(true)}>
          <Search size={14} />
          <span>搜索证券 / 公司 / 行业</span>
          <kbd>Ctrl K</kbd>
        </button>
        <div className="ml-auto hidden items-center gap-4 text-[10px] sm:flex">
          <span className="historical-badge">历史数据</span>
          <span className="font-mono text-slate-400">USD</span>
          <span className="font-mono text-slate-500">
            {now.toISOString().slice(11, 19)} UTC
          </span>
        </div>
        <button
          aria-label="展开导航"
          className="ml-2 lg:hidden"
          onClick={() => setMenu(!menu)}
        >
          <Menu size={18} />
        </button>
      </header>
      <aside className={`terminal-sidebar ${menu ? "mobile-open" : ""}`}>
        <div className="sidebar-label">RESEARCH WORKSPACE</div>
        <nav>
          {navigation.map(({ path, name, en, icon: Icon }, i) => (
            <NavLink
              key={path}
              to={path}
              end={path === "/"}
              className={({ isActive }) =>
                `terminal-nav ${isActive ? "active" : ""}`
              }
            >
              <Icon size={16} />
              <span>
                <strong>{name}</strong>
                <small>{en}</small>
              </span>
              <kbd>{i + 1}</kbd>
            </NavLink>
          ))}
        </nav>
        <div className="sidebar-bottom">
          <Database size={14} />
          <span>本地历史数据库</span>
          <p>
            {market?.stocks.length || "—"} 个标的 ·{" "}
            {market?.provenance.rows.toLocaleString() || "—"} 日线
          </p>
          <button onClick={() => setCommand(true)}>
            <Command size={12} /> 全局搜索 <kbd>Ctrl K</kbd>
          </button>
          <small>Alt + 1—5 切换工作区</small>
        </div>
      </aside>
      <div className="terminal-body">
        <div className="terminal-ticker" aria-label="历史行情快照">
          {market?.stocks.slice(0, 9).map((s) => {
            const q = market.quotes[s.symbol];
            return (
              <button
                key={s.symbol}
                onClick={() => {
                  selectStock(s.symbol);
                  navigate("/stocks");
                }}
              >
                <strong>{s.symbol}</strong>
                <span>{number(q?.close)}</span>
                <em className={q?.changePct >= 0 ? "positive" : "negative"}>
                  {q?.changePct >= 0 ? "+" : ""}
                  {percent(q?.changePct)}
                </em>
              </button>
            );
          })}
        </div>
        <div className="workspace-tabs">
          {navigation.map(({ path, name }, i) => (
            <NavLink
              end={path === "/"}
              key={path}
              to={path}
              className={({ isActive }) => (isActive ? "active" : "")}
            >
              <span className="font-mono opacity-50">0{i + 1}</span>
              {name}
            </NavLink>
          ))}
          <span className="ml-auto hidden text-[10px] text-slate-600 xl:block">
            历史快照 / {last || "载入中"}
          </span>
        </div>
        <main className="terminal-main">
          {watchError && (
            <div className="mb-3">
              <ErrorBox error={watchError} />
            </div>
          )}
          {error ? (
            <ErrorBox error={error} retry={() => setNonce((n) => n + 1)} />
          ) : !market ? (
            <Loading />
          ) : (
            <Routes>
              <Route path="/" element={<OverviewPage />} />
              <Route path="/stocks" element={<StockPage />} />
              <Route path="/lab" element={<LabPage />} />
              <Route path="/backtest" element={<BacktestPage />} />
              <Route path="/reports" element={<ReportsPage />} />
              <Route
                path="*"
                element={
                  <div>
                    页面不存在 <Link to="/">返回行情工作台</Link>
                  </div>
                }
              />
            </Routes>
          )}
        </main>
        <footer className="terminal-status">
          <span>
            <i className={market ? "connected" : ""} />
            {error
              ? "行情连接失败"
              : market
                ? "历史行情已载入"
                : "正在连接数据服务"}
          </span>
          <span>截至 {last || "—"} · 各标的末日可能不同</span>
          <span className="ml-auto">
            APERTURE / RESEARCH · 历史研究，不含实盘交易
          </span>
        </footer>
      </div>
    </div>
  );
}
