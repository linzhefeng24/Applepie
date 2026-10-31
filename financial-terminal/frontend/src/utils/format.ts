export const number = (n: number | undefined, d = 2) =>
  n === undefined || !Number.isFinite(n)
    ? "—"
    : n.toLocaleString("en-US", {
        minimumFractionDigits: d,
        maximumFractionDigits: d,
      });
export const percent = (n: number | undefined, d = 2) =>
  n === undefined ? "—" : `${number(n * 100, d)}%`;
export const compact = (n: number) =>
  new Intl.NumberFormat("en-US", {
    notation: "compact",
    maximumFractionDigits: 1,
  }).format(n);
export const palette = ["#b7ed77", "#67c8f1", "#c1a0ff", "#f4bd73", "#f08c9d"];
export const modelNames = {
  equal: "等权组合",
  minvariance: "最小方差",
  meanvariance: "均值—方差",
  mvsk: "MVSK",
  riskparity: "风险平价",
};
