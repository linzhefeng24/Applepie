import { useEffect, useState } from "react";
import { GetStockMessage } from "../../../apis/market/GetStockMessage";
import type { StockResult } from "../../../objects/market";
export type StockState =
  | { status: "loading" }
  | { status: "error"; error: string }
  | { status: "ready"; data: StockResult; comparison: StockResult | null };
export function useStock(
  symbol: string,
  start: string,
  end: string,
  compare: string,
) {
  const [state, setState] = useState<StockState>({ status: "loading" });
  useEffect(() => {
    const controller = new AbortController();
    setState({ status: "loading" });
    Promise.all([
      new GetStockMessage(symbol, start, end).send(controller.signal),
      compare
        ? new GetStockMessage(compare, start, end).send(controller.signal)
        : Promise.resolve(null),
    ])
      .then(([data, comparison]) =>
        setState({ status: "ready", data, comparison }),
      )
      .catch((e) => {
        if (e.name !== "AbortError")
          setState({ status: "error", error: e.message });
      });
    return () => controller.abort();
  }, [symbol, start, end, compare]);
  return state;
}
