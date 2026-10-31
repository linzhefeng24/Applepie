import { useEffect, useState } from "react";
import type { Market, StockResult } from "../../../objects/market";
import { GetStockMessage } from "../../../apis/statistics/GetStockMessage";
const cache = new Map<string, StockResult>();
export function useUniverse(market: Market) {
  const [state, setState] = useState<{
    data: Record<string, StockResult>;
    errors: string[];
  }>({ data: {}, errors: [] });
  const [version, retry] = useState(0);
  useEffect(() => {
    const controller = new AbortController();
    let cursor = 0;
    const data: Record<string, StockResult> = {};
    const errors: string[] = [];
    setState({ data: {}, errors: [] });
    async function worker() {
      while (cursor < market.stocks.length && !controller.signal.aborted) {
        const stock = market.stocks[cursor++],
          key = `${market.provenance.sha256}:${stock.symbol}`;
        try {
          const result =
            cache.get(key) ||
            (await new GetStockMessage(
              stock.symbol,
              stock.firstDate,
              stock.lastDate,
            ).send(controller.signal));
          cache.set(key, result);
          data[stock.symbol] = result;
        } catch (e) {
          if (controller.signal.aborted) return;
          errors.push(stock.symbol);
        }
        if (!controller.signal.aborted)
          setState({ data: { ...data }, errors: [...errors] });
      }
    }
    Promise.all(Array.from({ length: 4 }, worker));
    return () => controller.abort();
  }, [market, version]);
  return { ...state, retry: () => retry((v) => v + 1) };
}
