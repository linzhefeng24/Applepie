import { APIMessage } from "../APIMessage";
import type { Parameters, AnalysisResult } from "../../objects/analysis";
export class RunAnalysisMessage extends APIMessage<AnalysisResult> {
  readonly service = "optimization" as const;
  constructor(public parameters: Parameters) {
    super();
  }
}
