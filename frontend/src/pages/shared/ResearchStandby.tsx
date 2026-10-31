import type { Parameters } from "../../objects/analysis";
import { useMarket } from "../../stores/research";
import { Panel } from "../../components/ui/Panel";
import { number, percent } from "../../utils/format";
export function ResearchStandby({
  parameters: p,
  running,
  backtest = false,
}: {
  parameters: Parameters;
  running: boolean;
  backtest?: boolean;
}) {
  const market = useMarket()!;
  return (
    <div className="space-y-4">
      <Panel
        title={backtest ? "回测任务 / 待执行" : "组合分析 / 待执行"}
        subtitle={
          running
            ? "计算中，请保留当前工作区"
            : "配置左侧参数后运行，结果仅由真实历史数据计算"
        }
        action={
          <span className="panel-code">
            {running ? "COMPUTING" : "READY TO RUN"}
          </span>
        }
      >
        <div className="grid grid-cols-3 gap-3 border-y border-white/5 px-4 py-4 text-xs">
          <div>
            <span className="text-slate-500">估计区间</span>
            <p className="mt-2 font-mono text-[11px]">
              {p.start} → {p.end}
            </p>
          </div>
          <div>
            <span className="text-slate-500">配置标的</span>
            <p className="mt-2 font-mono">{p.symbols.length} SECURITIES</p>
          </div>
          <div>
            <span className="text-slate-500">权重上限</span>
            <p className="mt-2 font-mono">{percent(p.maxWeight)}</p>
          </div>
        </div>
        <div className="table-scroll">
          <table className="w-full">
            <thead>
              <tr>
                <th>标的</th>
                <th>公司</th>
                <th>末日源价格</th>
                <th>末日涨跌</th>
                <th>历史覆盖</th>
              </tr>
            </thead>
            <tbody>
              {p.symbols.map((symbol) => {
                const stock = market.stocks.find((s) => s.symbol === symbol),
                  q = market.quotes[symbol];
                return (
                  <tr key={symbol}>
                    <td className="font-mono text-[#e9b45b]">{symbol}</td>
                    <td>{stock?.name}</td>
                    <td className="font-mono">{number(q?.close)}</td>
                    <td className={q?.changePct >= 0 ? "positive" : "negative"}>
                      {percent(q?.changePct)}
                    </td>
                    <td className="font-mono text-[10px] text-slate-500">
                      {stock?.firstDate} — {stock?.lastDate}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
        {running && (
          <div
            role="status"
            className="mx-4 my-4 animate-pulse border-l-2 border-[#e9b45b] bg-[#e9b45b]/5 p-3 text-xs text-[#e9b45b]"
          >
            正在计算真实历史数据…
          </div>
        )}
      </Panel>
      <Panel
        title={backtest ? "执行与评估规则" : "模型配置与研究目标"}
        subtitle={
          backtest ? "ROLLING WINDOW · OUT-OF-SAMPLE" : "MODEL SPECIFICATION"
        }
      >
        <div className="table-scroll">
          <table className="w-full">
            <thead>
              <tr>
                <th>{backtest ? "环节" : "模型"}</th>
                <th>方法说明</th>
                <th>评估输出</th>
              </tr>
            </thead>
            <tbody>
              {(backtest
                ? [
                    [
                      "01 / 估计",
                      "滚动训练窗口，使用当时可用的历史数据",
                      "训练期 / 样本数",
                    ],
                    [
                      "02 / 执行",
                      "信号延迟一个收盘执行，计入权重漂移",
                      "调仓权重 / 审计",
                    ],
                    [
                      "03 / 成本",
                      "按照配置的交易成本扣减净值",
                      "换手率 / 净收益",
                    ],
                    [
                      "04 / 对照",
                      "与等权及经典模型使用同一评估区间",
                      "净值 / 回撤 / Sharpe",
                    ],
                  ]
                : [
                    [
                      "MVSK",
                      "联合考虑均值、方差、偏度与峰度",
                      "组合权重 / 高阶矩",
                    ],
                    [
                      "MVO",
                      "均值与方差之间的风险收益权衡",
                      "组合权重 / 风险收益",
                    ],
                    [
                      "MIN VAR",
                      "在权重约束下寻求较低组合方差",
                      "组合权重 / 波动率",
                    ],
                    [
                      "RISK PARITY",
                      "平衡各标的对组合风险的贡献",
                      "组合权重 / 风险贡献",
                    ],
                    [
                      "EQUAL WEIGHT",
                      "等权分配，作为配置基准",
                      "基准权重 / 对照指标",
                    ],
                  ]
              ).map(([name, description, result]) => (
                <tr key={name}>
                  <td className="font-mono text-[#e9b45b]">{name}</td>
                  <td className="text-slate-400">{description}</td>
                  <td className="text-slate-500">{result}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Panel>
    </div>
  );
}
