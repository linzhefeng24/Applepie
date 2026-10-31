import { useState } from "react";
import type {
  AnalysisResult,
  BacktestResult,
  Parameters,
} from "../../objects/analysis";
import { SaveReportMessage } from "../../apis/portfolio/SaveReportMessage";
import { ErrorBox } from "../../components/ui/Panel";
export function SaveResult({
  kind,
  parameters,
  result,
}: {
  kind: "analysis" | "backtest";
  parameters: Parameters;
  result: AnalysisResult | BacktestResult;
}) {
  const [title, setTitle] = useState(
    `${kind === "analysis" ? "组合研究" : "策略回测"} · ${result.symbols.join("/")}`,
  );
  const [state, setState] = useState("");
  const [busy, setBusy] = useState(false);
  async function save() {
    setBusy(true);
    setState("");
    try {
      await new SaveReportMessage(title, kind, parameters, result).send();
      setState("saved");
    } catch (e) {
      setState((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <div className="mb-4 rounded-lg border border-white/10 bg-[#111823] p-4">
      <div className="flex flex-wrap gap-2">
        <input
          aria-label="报告名称"
          placeholder="为这次研究命名"
          maxLength={160}
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          className="flex-1"
        />
        <button
          className="btn-primary"
          disabled={busy || !title.trim()}
          onClick={save}
        >
          {busy ? "保存中…" : "保存到研究档案"}
        </button>
      </div>
      {state === "saved" ? (
        <p role="status" className="mt-2 text-xs text-[#b7ed77]">
          已保存参数与完整结果，可在「研究档案」中查看和导出。
        </p>
      ) : (
        state && <ErrorBox error={state} />
      )}
    </div>
  );
}
