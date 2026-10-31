import { APIMessage } from "../APIMessage";
import type {
  Parameters,
  AnalysisResult,
  BacktestResult,
} from "../../objects/analysis";
export class SaveReportMessage extends APIMessage<{ id: string }> {
  readonly service = "portfolio" as const;
  constructor(
    public title: string,
    public kind: "analysis" | "backtest",
    public parameters: Parameters,
    public result: AnalysisResult | BacktestResult,
  ) {
    super();
  }
}
