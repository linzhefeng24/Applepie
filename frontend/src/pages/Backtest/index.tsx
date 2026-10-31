import { ResearchStandby } from "../shared/ResearchStandby";
import { PageTitle } from "../../components/ui/PageTitle";
import { ErrorBox } from "../../components/ui/Panel";
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
        description="滚动窗口、样本外评估与交易成本审计。"
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
            <ResearchStandby
              parameters={parameters}
              running={state.status === "running"}
              backtest={true}
            />
          )}
        </div>
      </div>
    </>
  );
}
