import { PageTitle } from "../../components/ui/PageTitle";
import { Panel, ErrorBox } from "../../components/ui/Panel";
import { useParameters } from "../shared/hooks/useParameters";
import { useExperiment } from "../shared/hooks/useExperiment";
import { ParameterForm } from "../shared/ParameterForm";
import { AnalysisView } from "../shared/AnalysisView";
import { SaveResult } from "../shared/SaveResult";
import type { AnalysisResult } from "../../objects/analysis";
export function LabPage() {
  const { parameters, update } = useParameters();
  const { state, run } = useExperiment<AnalysisResult>("analysis");
  return (
    <>
      <PageTitle
        eyebrow="QUANT LABORATORY"
        title="量化实验室"
        description="不只比较收益，也比较分布、风险与配置。"
      />
      <div className="grid items-start gap-5 xl:grid-cols-[280px_minmax(0,1fr)]">
        <ParameterForm
          parameters={parameters}
          update={update}
          backtest={false}
          running={state.status === "running"}
          onRun={() => run(parameters)}
        />
        <div className="min-w-0">
          {state.status === "ready" ? (
            <>
              <SaveResult
                key={JSON.stringify(state.parameters)}
                kind="analysis"
                parameters={state.parameters}
                result={state.data}
              />
              <AnalysisView data={state.data} />
            </>
          ) : state.status === "error" ? (
            <ErrorBox error={state.error} retry={() => run(parameters)} />
          ) : (
            <Panel title="从假设到组合" subtitle="FIVE MODELS / ONE DATASET">
              <div className="flex min-h-[480px] flex-col items-center justify-center px-8 text-center">
                <div className="font-mono text-7xl font-thin tracking-tighter text-[#b7ed77]/40">
                  μ σ s κ
                </div>
                <h3 className="mt-8 text-lg text-slate-200">
                  {state.status === "running"
                    ? "正在计算真实历史数据…"
                    : "构建你的第一个量化实验"}
                </h3>
                <p className="mt-3 max-w-sm text-xs leading-7 text-slate-500">
                  选择 2–10
                  个标的，设置权重约束和高阶矩偏好。五种模型会使用相同的估计区间，输出可检查的权重与指标。
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
