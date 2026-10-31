import { APIMessage } from "../APIMessage";

export class SetWatchlistMessage extends APIMessage<{ symbols: string[] }> {
  readonly service = "portfolio" as const;
  constructor(
    public symbol: string,
    public selected: boolean,
  ) {
    super();
  }
}
