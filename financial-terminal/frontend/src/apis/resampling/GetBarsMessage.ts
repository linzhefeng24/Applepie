import { APIMessage } from "../APIMessage";
import type { Bar } from "../../objects/market";
export class GetBarsMessage extends APIMessage<{
  symbol: string;
  frequency: string;
  sourceResolution: string;
  bars: Bar[];
  queryStart: string;
  queryEnd: string;
  incompleteBars: number;
}> {
  readonly service = "resampling" as const;
  constructor(
    public symbol: string,
    public start: string,
    public end: string,
    public frequency: string,
  ) {
    super();
  }
}
