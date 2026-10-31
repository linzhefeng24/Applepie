import { APIMessage } from "../APIMessage";
import type { StockResult } from "../../objects/market";
export class GetStockMessage extends APIMessage<StockResult> {
  readonly service = "statistics" as const;
  constructor(
    public symbol: string,
    public start: string,
    public end: string,
  ) {
    super();
  }
}
