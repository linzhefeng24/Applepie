import { APIMessage } from "../APIMessage";
import type { Parameters, BacktestResult } from "../../objects/analysis";
export class RunBacktestMessage extends APIMessage<BacktestResult> {
  readonly service = "backtest" as const;
  constructor(public parameters: Parameters) {
    super();
  }
}
