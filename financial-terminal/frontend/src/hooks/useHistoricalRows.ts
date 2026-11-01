import { useEffect, useState } from "react";
import type { Bar, StockResult } from "../objects/market";
import { GetBarsMessage } from "../apis/resampling/GetBarsMessage";
export function useHistoricalRows(
  symbols: string[],
  start: string,
  end: string,
  frequency: string,
  daily: Record<string, StockResult>,
) {
  const key =
    [...symbols].sort().join(",") + ":" + start + ":" + end + ":" + frequency;
  const [remote, setRemote] = useState<{
    key: string;
    data: Record<string, Bar[]>;
    errors: string[];
  }>({ key: "", data: {}, errors: [] });
  useEffect(() => {
    if (frequency === "1d" || !symbols.length || !start || !end || start > end)
      return;
    const abort = new AbortController(),
      data: Record<string, Bar[]> = {},
      errors: string[] = [];
    let cursor = 0;
    setRemote({ key, data: {}, errors: [] });
    async function worker() {
      while (cursor < symbols.length && !abort.signal.aborted) {
        const symbol = symbols[cursor++];
        try {
          const r = await new GetBarsMessage(
            symbol,
            start,
            end,
            frequency,
          ).send(abort.signal);
          data[symbol] = r.bars;
        } catch (e) {
          if (abort.signal.aborted) return;
          errors.push(symbol + ": " + (e as Error).message);
        }
        if (!abort.signal.aborted)
          setRemote({ key, data: { ...data }, errors: [...errors] });
      }
    }
    Promise.all(Array.from({ length: 4 }, worker));
    return () => abort.abort();
  }, [key]);
  return frequency === "1d"
    ? {
        data: Object.fromEntries(
          Object.entries(daily).map(([symbol, value]) => [symbol, value.bars]),
        ),
        errors: [],
      }
    : remote.key === key
      ? remote
      : { data: {}, errors: [] };
}
