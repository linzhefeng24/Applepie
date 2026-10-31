import { ResearchStandby } from "../shared/ResearchStandby";
import { PageTitle } from "../../components/ui/PageTitle";
import { ErrorBox } from "../../components/ui/Panel";
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
        eyebrow="PORTFOLIO OPTIMIZATION"
        title="组合优化"
        description="五模型配置、权重约束与高阶矩分析。"
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
            <ResearchStandby
              parameters={parameters}
              running={state.status === "running"}
              backtest={false}
            />
          )}
        </div>
      </div>
    </>
  );
}
