import type { Metrics } from "./market";
export type Model =
  | "equal"
  | "minvariance"
  | "meanvariance"
  | "mvsk"
  | "riskparity";
export interface Parameters {
  symbols: string[];
  start: string;
  end: string;
  maxWeight: number;
  riskAversion: number;
  skewPreference: number;
  kurtosisAversion: number;
  lookback: number;
  rebalance: number;
  costBps: number;
  model: Model;
}
export interface Optimization {
  model: Model;
  label: string;
  weights: number[];
  converged: boolean;
  message: string;
  iterations: number;
  objective: number;
  metrics: Metrics;
  histogram: { edges: number[]; counts: number[] };
}
export interface AnalysisResult {
  symbols: string[];
  start: string;
  end: string;
  sessions: number;
  models: Optimization[];
  correlation: number[][];
  warnings: string[];
  methodology: string;
  alignment: string;
  droppedSessions: Record<string, number>;
}
export interface Trade {
  executionDate: string;
  signalEnd: string;
  estimateStart: string;
  returnDate: string;
  weights: number[];
  turnover: number;
  cost: number;
  converged: boolean;
}
export interface Simulation {
  model: Model;
  label: string;
  metrics: Metrics;
  curve: { date: string; value: number; drawdown: number }[];
  trades: Trade[];
  totalTurnover: number;
  tradingCostRateSum: number;
  failedRebalances: number;
}
export interface BacktestResult {
  symbols: string[];
  start: string;
  end: string;
  results: Simulation[];
  warnings: string[];
  methodology: string;
  alignment: string;
  droppedSessions: Record<string, number>;
}
export interface ResearchReport {
  id: string;
  title: string;
  kind: "analysis" | "backtest";
  createdAt: string;
  parameters: Parameters;
  result: AnalysisResult | BacktestResult;
}
