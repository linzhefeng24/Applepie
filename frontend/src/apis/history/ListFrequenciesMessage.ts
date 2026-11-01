import { APIMessage } from "../APIMessage";
import type { FrequencyOption } from "../../objects/frequency";
export class ListFrequenciesMessage extends APIMessage<{
  symbol: string;
  frequencies: FrequencyOption[];
  maxBars: number;
  timezone: string;
}> {
  readonly service = "history" as const;
  constructor(public symbol: string) {
    super();
  }
}
