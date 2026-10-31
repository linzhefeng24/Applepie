import { StockPool } from "./components/StockPool";
import { useMemo, useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import {
  Search,
  ArrowUpRight,
  Star,
  ArrowRight,
  Layers,
  FlaskConical,
} from "lucide-react";
import {
  useMarket,
  useWatchlist,
  setWatchlist,
  selectStock,
} from "../../stores/research";
import { SetWatchlistMessage } from "../../apis/portfolio/SetWatchlistMessage";
import { Panel, Notice, ErrorBox, Empty, Tag } from "../../components/ui/Panel";
import { PageTitle } from "../../components/ui/PageTitle";
import { Metric } from "../../components/ui/Metrics";
import { number, percent, compact } from "../../utils/format";
export function OverviewPage() {
  const market = useMarket()!;
  const first = market.stocks.reduce(
    (a, b) => (a < b.firstDate ? a : b.firstDate),
    "9999",
  );
  const last = market.stocks.reduce(
    (a, b) => (a > b.lastDate ? a : b.lastDate),
    "",
  );
  return (
    <>
      <PageTitle
        eyebrow="MARKET INTELLIGENCE"
        title="把市场，变成你的研究。"
        description="从一只股票开始，探索收益、风险与组合的更多可能。"
        action={
          <Link to="/lab" className="btn-primary">
            开启量化实验 <ArrowUpRight size={14} />
          </Link>
        }
      />
      <div className="mb-6 grid grid-cols-2 gap-3 xl:grid-cols-4">
        <Metric
          label="研究标的"
          value={String(market.stocks.length).padStart(2, "0")}
          note="美股 / ADR / 黄金 ETF · 精选子集"
        />
        <Metric
          label="日线数据"
          value={compact(market.provenance.rows)}
          note="由真实分钟行情聚合"
        />
        <Metric
          label="历史覆盖"
          value="2022 — 2026"
          note={`${first} → ${last}`}
        />
        <Metric label="量化模型" value="05" note="MVSK / MVO / 风险平价等" />
      </div>
      <div className="mb-6 grid gap-4 xl:grid-cols-[1.8fr_1fr]">
        <div className="relative overflow-hidden rounded-xl border border-[#b7ed77]/15 bg-gradient-to-br from-[#19291f] via-[#13221f] to-[#111823] p-6">
          <div className="absolute -right-5 top-1 font-mono text-[135px] font-thin tracking-[-.15em] text-[#b7ed77]/[.045]">
            μσ
          </div>
          <Tag>RESEARCH NOTE / 001</Tag>
          <h2 className="relative mt-5 text-xl leading-relaxed text-white">
            收益之外，
            <br />
            还有分布的形状。
          </h2>
          <p className="relative mt-3 max-w-sm text-xs leading-6 text-slate-400">
            用均值、方差、偏度与峰度观察组合。将 MVSK
            与经典模型放在同一组历史数据上，检验想法。
          </p>
          <Link
            to="/lab"
            className="relative mt-5 inline-flex items-center gap-2 text-xs text-[#b7ed77]"
          >
            进入量化实验室 <ArrowRight size={14} />
          </Link>
        </div>
        <Panel
          title="一条完整的研究路径"
          subtitle="FROM OBSERVATION TO VALIDATION"
        >
          <div className="space-y-5 px-5 pb-6">
            {[
              ["01", "观察个股", "价格趋势与年度收益分布", "/stocks"],
              ["02", "构建组合", "五种模型与权重约束", "/lab"],
              ["03", "检验与记录", "滚动回测，保存研究结论", "/backtest"],
            ].map(([n, t, d, path]) => (
              <Link key={n} to={path} className="flex items-center gap-4">
                <span className="font-mono text-lg text-slate-700">{n}</span>
                <div className="flex-1">
                  <div className="text-xs text-slate-200">{t}</div>
                  <div className="mt-1 text-[10px] text-slate-500">{d}</div>
                </div>
                <ArrowUpRight size={14} className="text-slate-600" />
              </Link>
            ))}
          </div>
        </Panel>
      </div>
      <StockPool />
      <div className="mt-5">
        <Notice>
          <strong>数据边界：</strong>当前使用 data_v1 / part1.zip 中的 32
          个精选标的。未导入的股票不可查询；未提供财报、复权说明及分红。分钟成交量并非全市场成交量。
          <details className="mt-2">
            <summary className="cursor-pointer">查看数据校验与来源</summary>
            <div className="mt-2 break-all font-mono text-[10px]">
              SHA256: {market.provenance.sha256}
              <br />
              {market.provenance.rows.toLocaleString()} 行日线 · 无插值 · OHLCV
              聚合
            </div>
          </details>
        </Notice>
      </div>
    </>
  );
}
