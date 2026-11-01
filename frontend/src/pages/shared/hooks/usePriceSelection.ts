import { useEffect, useState } from "react";
import { GetPricesMessage } from "../../../apis/daily/GetPricesMessage";
import type { Bar } from "../../../objects/market";
export function usePriceSelection(
  symbols: string[],
  start: string,
  end: string,
) {
  const [state, setState] = useState<{
    data: Record<string, Bar[]>;
    loading: boolean;
    error: string;
  }>({ data: {}, loading: true, error: "" });
  const key = symbols.join(",");
  useEffect(() => {
    const abort = new AbortController();
    setState({ data: {}, loading: true, error: "" });
    if (!symbols.length) {
      setState({ data: {}, loading: false, error: "请至少选择一只证券" });
      return;
    }
    new GetPricesMessage(key.split(","), start, end)
      .send(abort.signal)
      .then((r) => setState({ data: r.series, loading: false, error: "" }))
      .catch((e) => {
        if (e.name !== "AbortError")
          setState({ data: {}, loading: false, error: e.message });
      });
    return () => abort.abort();
  }, [key, start, end]);
  return state;
}
