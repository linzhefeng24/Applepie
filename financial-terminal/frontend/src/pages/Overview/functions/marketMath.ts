import type { Bar, Stock, StockResult } from "../../../objects/market";
export const assetType = (stock: Pick<Stock, "name" | "sector">) =>
  /ETF/i.test(stock.sector)
    ? "ETF"
    : /\bADR\b/i.test(stock.name)
      ? "ADR"
      : "股票";
export function sma(values: number[], period: number): (number | null)[] {
  let sum = 0;
  return values.map((value, i) => {
    sum += value;
    if (i >= period) sum -= values[i - period];
    return i < period - 1 ? null : sum / period;
  });
}
export function ema(values: number[], period: number): number[] {
  const alpha = 2 / (period + 1);
  let last = values[0] ?? 0;
  return values.map((v, i) => (last = i ? alpha * v + (1 - alpha) * last : v));
}
export function rsi(values: number[], period = 14): (number | null)[] {
  let gain = 0,
    loss = 0;
  return values.map((value, i) => {
    if (!i) return null;
    const delta = value - values[i - 1];
    if (i <= period) {
      gain += Math.max(0, delta);
      loss += Math.max(0, -delta);
      if (i < period) return null;
      gain /= period;
      loss /= period;
    } else {
      gain = (gain * (period - 1) + Math.max(0, delta)) / period;
      loss = (loss * (period - 1) + Math.max(0, -delta)) / period;
    }
    return loss === 0 ? (gain === 0 ? 50 : 100) : 100 - 100 / (1 + gain / loss);
  });
}
export function technical(bars: Bar[]) {
  const prices = bars.map((b) => b.close),
    ma20 = sma(prices, 20),
    ma60 = sma(prices, 60),
    fast = ema(prices, 12),
    slow = ema(prices, 26),
    dif = fast.map((v, i) => v - slow[i]),
    dea = ema(dif, 9);
  const std = prices.map((_, i) =>
    i < 19
      ? null
      : Math.sqrt(
          prices
            .slice(i - 19, i + 1)
            .reduce((sum, p) => sum + (p - ma20[i]!) ** 2, 0) / 20,
        ),
  );
  return {
    ma20,
    ma60,
    rsi: rsi(prices),
    dif,
    dea,
    macd: dif.map((v, i) => 2 * (v - dea[i])),
    upper: ma20.map((v, i) => (v === null ? null : v + 2 * std[i]!)),
    lower: ma20.map((v, i) => (v === null ? null : v - 2 * std[i]!)),
  };
}
export function snapshot(
  result: StockResult | undefined,
  start: string,
  end: string,
) {
  if (!result) return {} as Record<string, number | undefined>;
  const history = result.bars.filter((b) => b.date <= end),
    bars = history.filter((b) => b.date >= start),
    last = history.at(-1),
    previous = history.at(-2);
  if (!last) return {} as Record<string, number | undefined>;
  const n = bars.length - 1,
    returns = bars.slice(1).map((b, i) => b.close / bars[i].close - 1),
    mean = n > 0 ? returns.reduce((a, b) => a + b, 0) / n : 0,
    variance =
      n > 1
        ? returns.reduce((sum, r) => sum + (r - mean) ** 2, 0) / (n - 1)
        : 0;
  let peak = bars[0]?.close ?? 1,
    drawdown = 0;
  for (const bar of bars) {
    peak = Math.max(peak, bar.close);
    drawdown = Math.min(drawdown, bar.close / peak - 1);
  }
  const m2 =
      n > 0 ? returns.reduce((sum, r) => sum + (r - mean) ** 2, 0) / n : 0,
    ta = technical(history);
  const trailing = (days: number) =>
    history.length > days
      ? last.close / history[history.length - days - 1].close - 1
      : undefined;
  return {
    close: last.close,
    change: previous ? last.close / previous.close - 1 : undefined,
    volume: last.volume,
    return: bars.length > 1 ? last.close / bars[0].close - 1 : undefined,
    return1m: trailing(22),
    return3m: trailing(63),
    return1y: trailing(252),
    annualReturn:
      n > 0 ? (last.close / bars[0].close) ** (252 / n) - 1 : undefined,
    volatility: n > 1 ? Math.sqrt(variance * 252) : undefined,
    sharpe:
      n > 1 && variance > 0
        ? (mean / Math.sqrt(variance)) * Math.sqrt(252)
        : undefined,
    maxDrawdown: n > 0 ? drawdown : undefined,
    skewness:
      m2 > 0
        ? returns.reduce((sum, r) => sum + (r - mean) ** 3, 0) / n / m2 ** 1.5
        : undefined,
    kurtosis:
      m2 > 0
        ? returns.reduce((sum, r) => sum + (r - mean) ** 4, 0) / n / m2 ** 2 - 3
        : undefined,
    high252:
      history.length >= 252
        ? Math.max(...history.slice(-252).map((b) => b.high))
        : undefined,
    low252:
      history.length >= 252
        ? Math.min(...history.slice(-252).map((b) => b.low))
        : undefined,
    ma20: ta.ma20.at(-1) ?? undefined,
    ma60: ta.ma60.at(-1) ?? undefined,
    rsi14: ta.rsi.at(-1) ?? undefined,
    ma20Gap: ta.ma20.at(-1) ? last.close / ta.ma20.at(-1)! - 1 : undefined,
    observations: Math.max(0, n),
  } as Record<string, number | undefined>;
}
export type Field = {
  id: string;
  label: string;
  group: string;
  format: "number" | "percent" | "volume";
  signed?: boolean;
  description: string;
};
export const fields: Field[] = [
  ["close", "收盘价", "行情", "number", false, "截至日最后可用源收盘价，USD"],
  ["change", "日涨跌", "行情", "percent", true, "截至日最后两个可用价格的收益"],
  [
    "volume",
    "源成交量",
    "行情",
    "volume",
    false,
    "源分钟记录聚合，并非全市场成交量",
  ],
  [
    "high252",
    "252日高",
    "行情",
    "number",
    false,
    "截至日最近252个观测的最高价；不足则留空",
  ],
  [
    "low252",
    "252日低",
    "行情",
    "number",
    false,
    "截至日最近252个观测的最低价；不足则留空",
  ],
  [
    "return",
    "区间收益",
    "收益",
    "percent",
    true,
    "所选起止区间的价格收益，未含分红",
  ],
  ["return1m", "近1月", "收益", "percent", true, "最近22个收益观测的价格收益"],
  ["return3m", "近3月", "收益", "percent", true, "最近63个收益观测的价格收益"],
  ["return1y", "近1年", "收益", "percent", true, "最近252个收益观测的价格收益"],
  [
    "annualReturn",
    "年化收益",
    "收益",
    "percent",
    true,
    "所选区间几何收益按252期年化",
  ],
  [
    "volatility",
    "年化波动",
    "风险",
    "percent",
    false,
    "所选区间日收益样本标准差乘以√252",
  ],
  [
    "maxDrawdown",
    "最大回撤",
    "风险",
    "percent",
    true,
    "所选区间从价格高点的最大跌幅",
  ],
  [
    "sharpe",
    "Sharpe",
    "风险",
    "number",
    false,
    "所选区间日收益均值/样本标准差×√252，无风险利率0",
  ],
  [
    "skewness",
    "偏度",
    "风险",
    "number",
    false,
    "所选区间收益的标准化三阶中心矩",
  ],
  [
    "kurtosis",
    "超额峰度",
    "风险",
    "number",
    false,
    "所选区间收益的标准化四阶中心矩减3",
  ],
  [
    "ma20",
    "MA20",
    "技术",
    "number",
    false,
    "截至日20日简单移动平均，使用区间前历史预热",
  ],
  ["ma60", "MA60", "技术", "number", false, "截至日60日简单移动平均"],
  ["ma20Gap", "MA20乖离", "技术", "percent", true, "收盘价相对20日均线的偏离"],
  ["rsi14", "RSI14", "技术", "number", false, "Wilder 平滑14日相对强弱指标"],
  [
    "observations",
    "收益观测",
    "风险",
    "number",
    false,
    "所选区间内可用价格收益观测数量",
  ],
].map(([id, label, group, format, signed, description]) => ({
  id,
  label,
  group,
  format,
  signed,
  description,
})) as Field[];
export const presets: Record<string, string[]> = {
  行情: [
    "close",
    "change",
    "volume",
    "return1m",
    "return1y",
    "volatility",
    "maxDrawdown",
    "sharpe",
  ],
  收益风险: [
    "return",
    "annualReturn",
    "volatility",
    "maxDrawdown",
    "sharpe",
    "skewness",
    "kurtosis",
    "observations",
  ],
  技术指标: [
    "close",
    "change",
    "ma20",
    "ma60",
    "ma20Gap",
    "rsi14",
    "high252",
    "low252",
  ],
};

export function curves(history: Bar[], start: string) {
  const bars = history.filter((b) => b.date >= start),
    base = bars[0]?.close ?? 1;
  let peak = base;
  const returns = history
    .slice(1)
    .map((b, i) => b.close / history[i].close - 1);
  return {
    bars,
    cumulative: bars.map((b) => (b.close / base - 1) * 100),
    drawdown: bars.map((b) => {
      peak = Math.max(peak, b.close);
      return (b.close / peak - 1) * 100;
    }),
    volatility: bars.map((b) => {
      const index = history.findIndex((h) => h.date === b.date);
      if (index < 20) return null;
      const sample = returns.slice(index - 20, index),
        mean = sample.reduce((a, r) => a + r, 0) / 20;
      return (
        Math.sqrt(
          (sample.reduce((a, r) => a + (r - mean) ** 2, 0) / 19) * 252,
        ) * 100
      );
    }),
  };
}
