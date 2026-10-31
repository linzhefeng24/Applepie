import { APIMessage } from "../APIMessage";

export class ListWatchlistMessage extends APIMessage<{ symbols: string[] }> {
  readonly service = "watchlist" as const;
  constructor() {
    super();
  }
}
