import type { StockResult, Audit } from "../../../objects/market";
import { Panel, Tag } from "../../../components/ui/Panel";
import { Chart } from "../../../components/ui/Chart";
import { priceChart, distribution } from "../functions/charts";
import { number, percent, compact } from "../../../utils/format";
export function AnnualTable({ data }: { data: StockResult }) {
  return (
    <Panel
      title="历年行情指标"
      subtitle="按所选日期区间统计；首尾不足 240 个观测日标记为部分年度"
    >
      <div className="table-scroll">
        <table className="w-full">
          <thead>
            <tr>
              <th>年度</th>
              <th>区间价格收益</th>
              <th>年化收益</th>
              <th>年化波动</th>
              <th>最大回撤</th>
              <th>Sharpe</th>
              <th>偏度</th>
              <th>超额峰度</th>
              <th>源成交量</th>
              <th>日数</th>
            </tr>
          </thead>
          <tbody>
            {data.annual.map((y) => (
              <tr key={y.year}>
                <td className="font-mono text-slate-100">
                  {y.year}{" "}
                  {y.partial && (
                    <span className="text-[9px] text-amber-200/60">部分</span>
                  )}
                </td>
                <td
                  className={`font-mono ${y.totalReturn >= 0 ? "text-[#b7ed77]" : "text-rose-300"}`}
                >
                  {percent(y.totalReturn)}
                </td>
                <td>{percent(y.annualReturn)}</td>
                <td>{percent(y.volatility)}</td>
                <td>{percent(y.maxDrawdown)}</td>
                <td>{number(y.sharpe)}</td>
                <td>{number(y.skewness)}</td>
                <td>{number(y.excessKurtosis)}</td>
                <td>{compact(y.volume)}</td>
                <td>{y.sessions}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Panel>
  );
}
