import { useState } from "react";
import { useSymbols } from "../../../stores/research";
import type { Parameters } from "../../../objects/analysis";
export function useParameters() {
  const symbols = useSymbols();
  const [fields, setFields] = useState<Omit<Parameters, "symbols">>({
    start: "2022-03-07",
    end: "2026-10-23",
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
