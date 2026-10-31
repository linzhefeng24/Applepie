import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Search, CornerDownLeft } from "lucide-react";
import { selectStock, useMarket } from "../stores/research";
export function CommandSearch({ close }: { close: () => void }) {
  const market = useMarket();
  const navigate = useNavigate();
  const [query, setQuery] = useState("");
  const [active, setActive] = useState(0);
  const input = useRef<HTMLInputElement>(null);
  const results = (market?.stocks || [])
    .filter((s) =>
      `${s.symbol} ${s.name} ${s.sector}`
        .toLowerCase()
        .includes(query.toLowerCase()),
    )
    .slice(0, 12);
  useEffect(() => {
    const previous = document.activeElement as HTMLElement | null;
    input.current?.focus();
    return () => previous?.focus();
  }, []);
  function open(symbol: string) {
    selectStock(symbol);
    navigate("/stocks");
    close();
  }
  return (
    <div className="command-backdrop" onClick={close}>
      <section
        role="dialog"
        aria-modal="true"
        aria-label="全局证券搜索"
        className="command-dialog"
        onClick={(e) => e.stopPropagation()}
        onKeyDown={(e) => {
          if (e.key === "Escape") close();
          if (e.key === "Tab") {
            const items = Array.from(
              e.currentTarget.querySelectorAll<HTMLElement>("button,input"),
            );
            const first = items[0],
              last = items.at(-1);
            if (e.shiftKey && document.activeElement === first) {
              e.preventDefault();
              last?.focus();
            } else if (!e.shiftKey && document.activeElement === last) {
              e.preventDefault();
              first?.focus();
            }
          }
          if (e.key === "ArrowDown") {
            e.preventDefault();
            setActive((i) => Math.min(i + 1, results.length - 1));
          }
          if (e.key === "ArrowUp") {
            e.preventDefault();
            setActive((i) => Math.max(0, i - 1));
          }
          if (e.key === "Enter" && results[active]) {
            e.preventDefault();
            open(results[active].symbol);
          }
        }}
      >
        <div className="flex items-center gap-3 border-b border-white/10 p-4">
          <Search size={18} />
          <input
            ref={input}
            aria-label="全局搜索股票"
            placeholder="输入代码、公司或行业…"
            value={query}
            onChange={(e) => {
              setQuery(e.target.value);
              setActive(0);
            }}
            className="!border-0 !bg-transparent flex-1 !p-0 !text-sm"
          />
          <kbd>ESC</kbd>
        </div>
        <div className="max-h-[420px] overflow-y-auto p-2">
          {results.map((s, i) => (
            <button
              key={s.symbol}
              className={`command-result ${i === active ? "selected" : ""}`}
              onMouseEnter={() => setActive(i)}
              onClick={() => open(s.symbol)}
            >
              <strong className="w-20 font-mono text-white">{s.symbol}</strong>
              <span className="flex-1 text-left">{s.name}</span>
              <span className="text-xs text-slate-500">{s.sector}</span>
              <CornerDownLeft size={12} />
            </button>
          ))}
          {!results.length && (
            <div className="p-8 text-center text-sm text-slate-500">
              当前数据库没有匹配标的
            </div>
          )}
        </div>
        <div className="border-t border-white/10 p-3 text-[11px] text-slate-500">
          ↑ ↓ 选择 · Enter 打开个股 · 仅搜索已导入的历史证券
        </div>
      </section>
    </div>
  );
}
