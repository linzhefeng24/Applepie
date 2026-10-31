import { useEffect, useState } from "react";
import { Files, Download, Trash2, ArrowLeft } from "lucide-react";
import { PageTitle } from "../../components/ui/PageTitle";
import {
  Panel,
  Empty,
  Loading,
  ErrorBox,
  Tag,
} from "../../components/ui/Panel";
import { ListReportsMessage } from "../../apis/reports/ListReportsMessage";
import { DeleteReportMessage } from "../../apis/reports/DeleteReportMessage";
import type {
  ResearchReport,
  AnalysisResult,
  BacktestResult,
} from "../../objects/analysis";
import { AnalysisView } from "../shared/AnalysisView";
import { BacktestView } from "../shared/BacktestView";
import { exportReport, download } from "../../utils/download";
export function ReportsPage() {
  const [reports, setReports] = useState<ResearchReport[] | null>(null);
  const [error, setError] = useState("");
  const [selected, setSelected] = useState<ResearchReport | null>(null);
  const [busy, setBusy] = useState("");
  const [nonce, setNonce] = useState(0);
  useEffect(() => {
    const c = new AbortController();
    setError("");
    new ListReportsMessage()
      .send(c.signal)
      .then((r) => setReports(r.reports))
      .catch((e) => {
        if (e.name !== "AbortError") setError(e.message);
      });
    return () => c.abort();
  }, [nonce]);
  async function remove(r: ResearchReport) {
    if (!window.confirm(`删除「${r.title}」？`)) return;
    setBusy(r.id);
    try {
      await new DeleteReportMessage(r.id).send();
      setReports((rs) => rs!.filter((x) => x.id !== r.id));
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy("");
    }
  }
  return (
    <>
      <PageTitle
        eyebrow="RESEARCH ARCHIVE"
        title="报告管理"
        description="保存的参数、结果与方法，共同构成一份可以复现的研究。"
      />
      {error && <ErrorBox error={error} retry={() => setNonce((n) => n + 1)} />}{" "}
      {selected ? (
        <>
          <div className="mb-5 flex flex-wrap justify-between gap-3">
            <button className="btn" onClick={() => setSelected(null)}>
              <ArrowLeft size={13} />
              返回档案
            </button>
            <div className="flex gap-2">
              <button className="btn" onClick={() => exportReport(selected)}>
                <Download size={13} />
                导出 Markdown
              </button>
              <button
                className="btn"
                onClick={() =>
                  download(
                    `research-${selected.id}.json`,
                    JSON.stringify(selected, null, 2),
                    "application/json",
                  )
                }
              >
                完整 JSON
              </button>
              <button className="btn" onClick={() => window.print()}>
                打印 / PDF
              </button>
            </div>
          </div>
          <h2 className="mb-2 text-lg text-white">{selected.title}</h2>
          <p className="mb-5 text-[10px] text-slate-500">
            {selected.createdAt} · 参数快照与结果已固化
          </p>
          <details className="mb-5 rounded-lg border border-white/10 p-4 text-xs text-slate-400">
            <summary className="cursor-pointer">查看参数快照</summary>
            <pre className="mt-3 overflow-auto text-[10px]">
              {JSON.stringify(selected.parameters, null, 2)}
            </pre>
          </details>
          {selected.kind === "analysis" ? (
            <AnalysisView data={selected.result as AnalysisResult} />
          ) : (
            <BacktestView data={selected.result as BacktestResult} />
          )}
        </>
      ) : reports === null ? (
        <Loading />
      ) : (
        <Panel
          title="最近研究"
          subtitle="本地共享研究空间 · 最近 50 份 · 不含账户隔离"
          action={<Tag>{reports.length} REPORTS</Tag>}
        >
          {!reports.length ? (
            <div className="py-14 text-center">
              <Files size={32} className="mx-auto text-slate-700" />
              <Empty text="还没有研究记录。在组合优化或回测中运行一次分析，再保存结果。" />
            </div>
          ) : (
            <div className="divide-y divide-white/5">
              {reports.map((r) => (
                <div key={r.id} className="flex items-center gap-4 p-5">
                  <div className="rounded-lg bg-[#b7ed77]/5 p-3 text-[#b7ed77]">
                    <Files size={18} />
                  </div>
                  <button
                    onClick={() => setSelected(r)}
                    className="min-w-0 flex-1 text-left"
                  >
                    <div className="truncate text-sm text-slate-200">
                      {r.title}
                    </div>
                    <div className="mt-2 text-[10px] text-slate-500">
                      {r.kind === "analysis" ? "量化分析" : "样本外回测"} ·{" "}
                      {r.result.symbols.join(" / ")} · {r.createdAt}
                    </div>
                  </button>
                  <button
                    aria-label={`导出 ${r.title}`}
                    className="btn"
                    onClick={() => exportReport(r)}
                  >
                    <Download size={14} />
                  </button>
                  <button
                    aria-label={`删除 ${r.title}`}
                    disabled={busy === r.id}
                    className="btn hover:!text-rose-300"
                    onClick={() => remove(r)}
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
              ))}
            </div>
          )}
        </Panel>
      )}
    </>
  );
}
