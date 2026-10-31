import { APIMessage } from "../APIMessage";
import type { Market } from "../../objects/market";
export class ListStocksMessage extends APIMessage<Market> {
  readonly service = "market" as const;
  constructor() {
    super();
  }
}
