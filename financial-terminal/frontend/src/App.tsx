import { useEffect, useState } from "react";
import { NavLink, Routes, Route, useLocation, Link } from "react-router-dom";
import {
  Aperture,
  LayoutDashboard,
  ChartNoAxesCombined,
  FlaskConical,
  History,
  Files,
  ArrowUpRight,
  Database,
  Menu,
} from "lucide-react";
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
  { path: "/", name: "研究概览", en: "Overview", icon: LayoutDashboard },
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
  return (
    <div className="min-h-screen">
      <aside
        className={`${menu ? "flex" : "hidden"} fixed inset-y-0 left-0 z-40 w-60 flex-col border-r border-white/[.07] bg-[#0d141e] lg:flex`}
      >
        <Link to="/" className="flex items-center gap-3 px-6 py-8">
          <div className="rounded-lg bg-[#b7ed77] p-2 text-[#17231e]">
            <Aperture size={23} />
          </div>
          <div>
            <div className="text-sm font-bold tracking-[.17em] text-white">
              APERTURE
            </div>
            <div className="mt-1 font-mono text-[8px] tracking-[.22em] text-slate-500">
              FINANCIAL RESEARCH
            </div>
          </div>
        </Link>
        <div className="px-6 pb-3 pt-6 text-[9px] tracking-[.22em] text-slate-600">
          WORKSPACE / 研究空间
        </div>
        <nav className="space-y-1 px-3">
          {navigation.map(({ path, name, en, icon: Icon }) => (
            <NavLink
              key={path}
              to={path}
              end={path === "/"}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-lg px-4 py-3.5 ${isActive ? "bg-[#b7ed77]/10 text-[#b7ed77]" : "text-slate-500 hover:bg-white/[.03] hover:text-slate-300"}`
              }
            >
              <Icon size={17} />
              <div>
                <div className="text-xs font-medium">{name}</div>
                <div className="mt-1 font-mono text-[9px] opacity-50">{en}</div>
              </div>
            </NavLink>
          ))}
        </nav>
        <div className="mt-auto p-5">
          <div className="rounded-lg border border-white/[.07] bg-white/[.02] p-4">
            <Database size={15} className="text-[#b7ed77]" />
            <div className="mt-3 text-xs text-slate-300">
              你的数据，你的研究
            </div>
            <div className="mt-2 text-[10px] leading-5 text-slate-600">
              真实历史行情 · 本地数据库
              <br />
              课程项目 / 独立微服务
            </div>
          </div>
          <div className="mt-5 flex justify-between font-mono text-[9px] text-slate-600">
            <span>APERTURE v1.0</span>
            <span>LOCAL</span>
          </div>
        </div>
      </aside>
      <div className="lg:ml-60">
        <header className="sticky top-0 z-30 flex h-16 items-center justify-between border-b border-white/[.07] bg-[#0b1018]/95 px-5 backdrop-blur md:px-8">
          <div className="flex items-center gap-3">
            <button
              aria-label="展开导航"
              onClick={() => setMenu(!menu)}
              className="lg:hidden"
            >
              <Menu size={19} />
            </button>
            <div className="font-mono text-[10px] tracking-wider text-slate-600">
              WORKSPACE <span className="mx-2 text-slate-700">/</span>
              <span className="text-slate-300">
                {navigation.find((n) => n.path === location.pathname)?.en ||
                  "Research"}
              </span>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <span className="hidden font-mono text-[10px] text-slate-500 sm:block">
              HISTORICAL DATA · USD
            </span>
            <span className="flex items-center gap-2 rounded-full border border-[#b7ed77]/15 bg-[#b7ed77]/5 px-3 py-1 text-[10px] text-[#b7ed77]">
              <span className="h-1 w-1 rounded-full bg-current" />
              {market ? "数据已载入" : "连接中"}
            </span>
          </div>
        </header>
        <main className="mx-auto max-w-[1600px] p-5 md:p-8">
          {watchError && (
            <div className="mb-4">
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
                    页面不存在{" "}
                    <Link to="/" className="underline">
                      返回概览
                    </Link>
                  </div>
                }
              />
            </Routes>
          )}
          <footer className="mt-10 flex flex-wrap justify-between gap-2 border-t border-white/[.05] pt-4 text-[9px] text-slate-600">
            <span>APERTURE / 从数据出发，让研究有据可循。</span>
            <span>
              历史研究工具 · 不含实盘交易 · 不构成投资建议{" "}
              <ArrowUpRight size={10} className="inline" />
            </span>
          </footer>
        </main>
      </div>
    </div>
  );
}
