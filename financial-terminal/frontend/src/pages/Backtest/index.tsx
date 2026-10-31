import { PageTitle } from "../../components/ui/PageTitle";
import { Panel, ErrorBox } from "../../components/ui/Panel";
import { useParameters } from "../shared/hooks/useParameters";
import { useExperiment } from "../shared/hooks/useExperiment";
import { ParameterForm } from "../shared/ParameterForm";
import { BacktestView } from "../shared/BacktestView";
import { SaveResult } from "../shared/SaveResult";
import type { BacktestResult } from "../../objects/analysis";
export function BacktestPage() {
  const { parameters, update } = useParameters();
  const { state, run } = useExperiment<BacktestResult>("backtest");
  return (
    <>
      <PageTitle
        eyebrow="STRATEGY VALIDATION"
        title="策略回测"
        description="让策略走出估计区间，接受历史数据的检验。"
      />
      <div className="grid items-start gap-5 xl:grid-cols-[280px_minmax(0,1fr)]">
        <ParameterForm
          parameters={parameters}
          update={update}
          backtest={true}
          running={state.status === "running"}
          onRun={() => run(parameters)}
        />
        <div className="min-w-0">
          {state.status === "ready" ? (
            <>
              <SaveResult
                key={JSON.stringify(state.parameters)}
                kind="backtest"
                parameters={state.parameters}
                result={state.data}
              />
              <BacktestView data={state.data} />
            </>
          ) : state.status === "error" ? (
            <ErrorBox error={state.error} retry={() => run(parameters)} />
          ) : (
            <Panel
              title="样本之外，策略还有效吗？"
              subtitle="ROLLING WINDOW / NO LOOK-AHEAD"
            >
              <div className="flex min-h-[480px] flex-col items-center justify-center px-8 text-center">
                <div className="font-mono text-7xl font-thin tracking-tighter text-[#b7ed77]/40">
                  t → t+1
                </div>
                <h3 className="mt-8 text-lg text-slate-200">
                  {state.status === "running"
                    ? "正在计算真实历史数据…"
                    : "验证一个可以复现的交易假设"}
                </h3>
                <p className="mt-3 max-w-sm text-xs leading-7 text-slate-500">
                  使用固定滚动窗口估计参数，延迟一个收盘执行交易。对照等权和经典优化组合，计入权重漂移与交易成本。
                </p>
                {state.status === "running" && (
                  <div
                    role="status"
                    className="mt-6 h-1 w-40 animate-pulse rounded bg-[#b7ed77]/50"
                  />
                )}
              </div>
            </Panel>
          )}
        </div>
      </div>
    </>
  );
}
