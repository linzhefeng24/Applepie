import type {
  ResearchReport,
  BacktestResult,
  AnalysisResult,
} from "../objects/analysis";
import { percent, number } from "./format";
export function download(name: string, text: string, type = "text/plain") {
  const url = URL.createObjectURL(new Blob([text], { type }));
  const a = document.createElement("a");
  a.href = url;
  a.download = name;
  a.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
export function exportReport(r: ResearchReport) {
  const base = `# ${r.title}\n\n${r.kind === "analysis" ? "量化实验" : "滚动样本外回测"} · ${r.result.start} — ${r.result.end}\n\n标的：${r.result.symbols.join(", ")}\n\n## 参数\n\n\`\`\`json\n${JSON.stringify(r.parameters, null, 2)}\n\`\`\`\n\n## 结果\n\n`;
  const rows =
    r.kind === "analysis"
      ? (r.result as AnalysisResult).models
      : (r.result as BacktestResult).results;
  const table =
    "| 模型 | 年化收益 | 年化波动 | Sharpe | 最大回撤 |\n|---|---|---|---|---|\n" +
    rows
      .map(
        (x) =>
          `| ${x.label} | ${percent(x.metrics.annualReturn)} | ${percent(x.metrics.volatility)} | ${number(x.metrics.sharpe)} | ${percent(x.metrics.maxDrawdown)} |`,
      )
      .join("\n");
  download(
    `research-${r.id}.md`,
    base +
      table +
      "\n\n## 方法与限制\n\n" +
      r.result.methodology +
      "\n\n" +
      r.result.warnings.map((x) => "- " + x).join("\n"),
    "text/markdown;charset=utf-8",
  );
}
