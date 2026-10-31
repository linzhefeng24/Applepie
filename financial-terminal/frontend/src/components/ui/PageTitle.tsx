import type { ReactNode } from "react";
export function PageTitle({
  eyebrow,
  title,
  description,
  action,
}: {
  eyebrow: string;
  title: string;
  description: string;
  action?: ReactNode;
}) {
  return (
    <div className="mb-4 flex flex-wrap items-end justify-between gap-4">
      <div>
        <div className="mb-2 font-mono text-[10px] tracking-[.22em] text-[#e9b45b]">
          {eyebrow}
        </div>
        <h1 className="text-xl font-semibold tracking-tight text-white">
          {title}
        </h1>
        <p className="mt-2 text-xs text-slate-500">{description}</p>
      </div>
      {action}
    </div>
  );
}
