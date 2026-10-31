import { APIMessage } from "../APIMessage";
import type { Bar } from "../../objects/market";
export class GetPricesMessage extends APIMessage<{
  series: Record<string, Bar[]>;
}> {
  readonly service = "history" as const;
  constructor(
    public symbols: string[],
    public start: string,
    public end: string,
  ) {
    super();
  }
}
