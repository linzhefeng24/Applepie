import type { Bar } from "../../../objects/market";
export function alignPrices(series: Record<string, Bar[]>, symbols: string[]) {
  const maps = symbols.map(
    (s) => new Map((series[s] || []).map((b) => [b.date, b.close])),
  );
  const dates = (series[symbols[0]] || [])
    .map((b) => b.date)
    .filter((d) => maps.every((m) => m.has(d)))
    .sort();
  return { dates, prices: maps.map((m) => dates.map((d) => m.get(d)!)) };
}
const mean = (v: number[]) => v.reduce((a, b) => a + b, 0) / v.length;
export function portfolioRisk(prices: number[][], weights: number[]) {
  if (
    !prices.length ||
    prices[0].length < 3 ||
    prices.some((p) => p.length !== prices[0].length)
  )
    throw new Error("至少需要三个共同价格日");
  if (
    weights.length !== prices.length ||
    weights.some((w) => !Number.isFinite(w) || w < 0) ||
    Math.abs(weights.reduce((a, b) => a + b, 0) - 1) > 1e-6
  )
    throw new Error("权重需非负且合计100%");
  const returns = prices.map((p) => p.slice(1).map((v, i) => v / p[i] - 1));
  const averages = returns.map(mean),
    n = returns[0].length;
  const covariance = returns.map((row, i) =>
    returns.map(
      (other, j) =>
        row.reduce(
          (s, v, k) => s + (v - averages[i]) * (other[k] - averages[j]),
          0,
        ) /
        (n - 1),
    ),
  );
  const portfolio = returns[0].map((_, t) =>
    returns.reduce((s, r, i) => s + weights[i] * r[t], 0),
  );
  const variance = weights.reduce(
    (s, w, i) =>
      s + w * covariance[i].reduce((v, c, j) => v + c * weights[j], 0),
    0,
  );
  const volatility = Math.sqrt(Math.max(variance, 0) * 252);
  const contributions = weights.map((w, i) =>
    volatility
      ? (252 * w * covariance[i].reduce((v, c, j) => v + c * weights[j], 0)) /
        volatility
      : 0,
  );
  const sorted = [...portfolio].sort((a, b) => a - b),
    tail = sorted.slice(0, Math.max(1, Math.ceil(n * 0.05)));
  let peak = 1,
    value = 1;
  const curve = [
    { value: 1, drawdown: 0 },
    ...portfolio.map((r) => {
      value *= 1 + r;
      peak = Math.max(peak, value);
      return { value, drawdown: value / peak - 1 };
    }),
  ];
  return {
    observations: n,
    volatility,
    contributions,
    correlation: covariance.map((row, i) =>
      row.map((v, j) =>
        covariance[i][i] && covariance[j][j]
          ? v / Math.sqrt(covariance[i][i] * covariance[j][j])
          : i === j
            ? 1
            : 0,
      ),
    ),
    var95: Math.max(0, -sorted[Math.max(0, Math.ceil(n * 0.05) - 1)]),
    es95: Math.max(0, -mean(tail)),
    maxDrawdown: Math.min(...curve.map((p) => p.drawdown)),
    totalReturn: value - 1,
    curve,
  };
}
