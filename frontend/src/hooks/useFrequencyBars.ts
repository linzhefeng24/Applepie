import { useEffect, useState } from "react";
import type { Bar } from "../objects/market";
import type { FrequencyOption } from "../objects/frequency";
import { ListFrequenciesMessage } from "../apis/resampling/ListFrequenciesMessage";
import { GetBarsMessage } from "../apis/resampling/GetBarsMessage";
const cache = new Map<string, FrequencyOption[]>();
export function useFrequencyBars(
  symbol: string,
  base: Bar[],
  start: string,
  end: string,
) {
  const [frequency, setFrequency] = useState("1d"),
    [meta, setMeta] = useState<{ symbol: string; options: FrequencyOption[] }>({
      symbol: "",
      options: [],
    });
  const [remote, setRemote] = useState<{
    key: string;
    bars: Bar[];
    error: string;
    loading: boolean;
    incomplete: number;
  }>({ key: "", bars: [], error: "", loading: false, incomplete: 0 });
  useEffect(() => {
    const abort = new AbortController();
    const known = cache.get(symbol);
    if (known) {
      setMeta({ symbol, options: known });
      return;
    }
    new ListFrequenciesMessage(symbol)
      .send(abort.signal)
      .then((r) => {
        cache.set(symbol, r.frequencies);
        setMeta({ symbol, options: r.frequencies });
      })
      .catch((e) => {
        if (e.name !== "AbortError") setMeta({ symbol, options: [] });
      });
    return () => abort.abort();
  }, [symbol]);
  const options = meta.symbol === symbol ? meta.options : [],
    selected = options.find((f) => f.code === frequency),
    minute = frequency.endsWith("min");
  let queryStart = frequency === "1y" && selected ? selected.start : start,
    queryEnd = end;
  if (minute && selected) {
    queryEnd =
      end < selected.end.slice(0, 10) ? end : selected.end.slice(0, 10);
    const date = new Date(queryEnd + "T00:00:00Z");
    if (Number.isFinite(date.getTime())) {
      date.setUTCDate(date.getUTCDate() - 6);
      queryStart = [
        start,
        selected.start.slice(0, 10),
        date.toISOString().slice(0, 10),
      ]
        .sort()
        .at(-1)!;
    }
  }
  const key = [symbol, frequency, queryStart, queryEnd].join(":");
  useEffect(() => {
    if (frequency === "1d" || !selected) return;
    const abort = new AbortController();
    if (
      !selected.available ||
      !queryStart ||
      !queryEnd ||
      queryStart > queryEnd
    ) {
      setRemote({
        key,
        bars: [],
        error: "该区间没有此频率的真实数据，请调整日期或选择日线。",
        loading: false,
        incomplete: 0,
      });
      return;
    }
    setRemote({ key, bars: [], error: "", loading: true, incomplete: 0 });
    new GetBarsMessage(symbol, queryStart, queryEnd, frequency)
      .send(abort.signal)
      .then((r) =>
        setRemote({
          key,
          bars: r.bars,
          error: "",
          loading: false,
          incomplete: r.incompleteBars,
        }),
      )
      .catch((e) => {
        if (e.name !== "AbortError")
          setRemote({
            key,
            bars: [],
            error: e.message,
            loading: false,
            incomplete: 0,
          });
      });
    return () => abort.abort();
  }, [symbol, frequency, queryStart, queryEnd, selected, key]);
  const daily = base.filter((b) => b.date.slice(0, 10) <= end);
  return {
    frequency,
    setFrequency,
    options: options.filter((f) => f.available || f.code !== "1y"),
    bars: frequency === "1d" ? daily : remote.key === key ? remote.bars : [],
    loading:
      frequency !== "1d" && (!selected || remote.key !== key || remote.loading),
    error: remote.key === key ? remote.error : "",
    queryStart,
    queryEnd,
    selected,
    incomplete: remote.key === key ? remote.incomplete : 0,
    minute,
  };
}
