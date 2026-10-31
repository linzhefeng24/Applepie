import type { ReactNode } from "react";
export function Panel({
  title,
  subtitle,
  action,
  children,
  className = "",
}: {
  title: string;
  subtitle?: string;
  action?: ReactNode;
  children: ReactNode;
  className?: string;
}) {
  return (
    <section className={`terminal-panel ${className}`}>
      <div className="panel-heading">
        <div>
          <h2 className="text-sm font-semibold tracking-wide text-slate-100">
            {title}
          </h2>
          {subtitle && (
            <p className="mt-1 text-[11px] text-slate-500">{subtitle}</p>
          )}
        </div>
        {action}
      </div>
      {children}
    </section>
  );
}
export function Notice({ children }: { children: ReactNode }) {
  return (
    <div className="rounded-lg border border-amber-300/15 bg-amber-200/[.04] px-4 py-3 text-xs leading-relaxed text-amber-100/65">
      {children}
    </div>
  );
}
export function ErrorBox({
  error,
  retry,
}: {
  error: string;
  retry?: () => void;
}) {
  return (
    <div
      role="alert"
      className="rounded-lg border border-rose-400/30 bg-rose-400/5 p-4 text-sm text-rose-200"
    >
      {error}
      {retry && (
        <button onClick={retry} className="ml-4 underline">
          重试
        </button>
      )}
    </div>
  );
}
export function Empty({ text = "暂无数据" }: { text?: string }) {
  return (
    <div className="px-6 py-16 text-center text-sm text-slate-500">{text}</div>
  );
}
export function Loading() {
  return (
    <div
      role="status"
      className="animate-pulse p-12 text-center text-sm text-slate-400"
    >
      正在读取研究数据…
    </div>
  );
}
export function Tag({ children }: { children: ReactNode }) {
  return (
    <span className="rounded border border-white/10 px-2 py-1 font-mono text-[10px] text-slate-400">
      {children}
    </span>
  );
}
