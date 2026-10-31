export interface Stock {
  symbol: string;
  name: string;
  sector: string;
  currency: string;
  firstDate: string;
  lastDate: string;
  sessions: number;
  source: string;
}
export interface Bar {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  minutes: number;
}
export interface Metrics {
  observations: number;
  totalReturn: number;
  annualReturn: number;
  volatility: number;
  sharpe: number;
  maxDrawdown: number;
  mean: number;
  variance: number;
  skewness: number;
  excessKurtosis: number;
  sortino?: number;
  var95?: number;
}
export interface Annual extends Metrics {
  year: string;
  sessions: number;
  volume: number;
  open: number;
  close: number;
  partial: boolean;
}
export interface StockResult {
  stock: Stock;
  bars: Bar[];
  metrics: Metrics;
  annual: Annual[];
}
export interface Audit {
  symbol: string;
  rawMinutes: number;
  rejectedMinutes: number;
  duplicates: number;
  sources: string[];
  dailyRows: number;
  sessionsUnder300Minutes: number;
  dailyMovesOver25Pct: number;
}
export interface Provenance {
  release: string;
  asset: string;
  sha256: string;
  symbols: number;
  rows: number;
  audits: Audit[];
  adjustment: string;
  volume: string;
  timezone: string;
}
export interface Market {
  stocks: Stock[];
  quotes: Record<
    string,
    { date: string; close: number; volume: number; changePct: number }
  >;
  provenance: Provenance;
}
