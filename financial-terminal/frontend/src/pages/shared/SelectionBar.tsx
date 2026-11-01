import { useMarket } from "../../stores/research";
export function SelectionBar({
  symbols,
  setSymbols,
  start,
  end,
  setStart,
  setEnd,
}: {
  symbols: string[];
  setSymbols: (v: string[]) => void;
  start: string;
  end: string;
  setStart: (v: string) => void;
  setEnd: (v: string) => void;
}) {
  const market = useMarket()!;
  return (
    <div className="space-y-3 border-y border-slate-800 py-3">
      <div className="flex flex-wrap gap-4 text-xs">
        <label>
          开始日期{" "}
          <input
            aria-label="分析开始日期"
            type="date"
            value={start}
            onChange={(e) => setStart(e.target.value)}
          />
        </label>
        <label>
          结束日期{" "}
          <input
            aria-label="分析结束日期"
            type="date"
            value={end}
            onChange={(e) => setEnd(e.target.value)}
          />
        </label>
        <span className="text-slate-500">最多选择5只证券 · 共同日期对齐</span>
      </div>
      <div className="flex flex-wrap gap-x-4 gap-y-2 text-xs">
        {market.stocks.map((s) => (
          <label key={s.symbol} className="flex items-center gap-1">
            <input
              type="checkbox"
              aria-label={`选择 ${s.symbol}`}
              checked={symbols.includes(s.symbol)}
              disabled={!symbols.includes(s.symbol) && symbols.length >= 5}
              onChange={(e) =>
                setSymbols(
                  e.target.checked
                    ? [...symbols, s.symbol]
                    : symbols.filter((v) => v !== s.symbol),
                )
              }
            />
            {s.symbol}
          </label>
        ))}
      </div>
    </div>
  );
}
