import { useState } from "react";
import { useSymbols, useMarket } from "../../../stores/research";
import type { Parameters } from "../../../objects/analysis";
export function useParameters() {
  const symbols = useSymbols();
  const market = useMarket()!;
  const [fields, setFields] = useState<Omit<Parameters, "symbols">>({
    start: market.stocks.reduce(
      (d, s) => (s.firstDate < d ? s.firstDate : d),
      "9999",
    ),
    end: market.stocks.reduce((d, s) => (s.lastDate > d ? s.lastDate : d), ""),
    maxWeight: 0.4,
    riskAversion: 3,
    skewPreference: 1,
    kurtosisAversion: 1,
    lookback: 126,
    rebalance: 21,
    costBps: 10,
    model: "mvsk",
  });
  return {
    parameters: { ...fields, symbols },
    update: <K extends keyof Omit<Parameters, "symbols">>(
      key: K,
      value: Parameters[K],
    ) => setFields((s) => ({ ...s, [key]: value })),
  };
}
