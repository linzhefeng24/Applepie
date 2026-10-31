import { useEffect, useRef, useState } from "react";
import type {
  AnalysisResult,
  BacktestResult,
  Parameters,
} from "../../../objects/analysis";
import { RunAnalysisMessage } from "../../../apis/analysis/RunAnalysisMessage";
import { RunBacktestMessage } from "../../../apis/analysis/RunBacktestMessage";
export type Experiment<T> =
  | { status: "idle" }
  | { status: "running" }
  | { status: "error"; error: string }
  | { status: "ready"; data: T; parameters: Parameters };
export function useExperiment<T extends AnalysisResult | BacktestResult>(
  kind: "analysis" | "backtest",
) {
  const [state, setState] = useState<Experiment<T>>({ status: "idle" });
  const controller = useRef<AbortController | null>(null);
  useEffect(() => () => controller.current?.abort(), []);
  async function run(parameters: Parameters) {
    controller.current?.abort();
    const abort = new AbortController();
    controller.current = abort;
    setState({ status: "running" });
    try {
      const request =
        kind === "analysis"
          ? new RunAnalysisMessage(parameters)
          : new RunBacktestMessage(parameters);
      const data = await request.send(abort.signal);
      if (!abort.signal.aborted)
        setState({
          status: "ready",
          data: data as T,
          parameters: structuredClone(parameters),
        });
    } catch (e) {
      if (!abort.signal.aborted)
        setState({ status: "error", error: (e as Error).message });
    }
  }
  return { state, run };
}
