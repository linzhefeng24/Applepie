import { test, expect } from "@playwright/test";
import {
  assetType,
  sma,
  rsi,
  technical,
  snapshot,
  curves,
} from "../src/pages/Overview/functions/marketMath";
import type { Bar, StockResult } from "../src/objects/market";
const bar = (date: string, close: number): Bar => ({
  date,
  close,
  open: close,
  high: close,
  low: close,
  volume: 10,
  minutes: 390,
});
test("技术指标：预热、平价边界及 Wilder RSI", () => {
  expect(sma([1, 2, 3, 4], 3)).toEqual([null, null, 2, 3]);
  expect(rsi(Array.from({ length: 20 }, (_, i) => i + 1)).at(-1)).toBe(100);
  expect(rsi(Array.from({ length: 20 }, (_, i) => 20 - i)).at(-1)).toBe(0);
  expect(rsi(Array(20).fill(10)).at(-1)).toBe(50);
  expect(rsi([10, 11, 12])).toEqual([null, null, null]);
  const t = technical(
    Array.from({ length: 65 }, (_, i) => bar(String(i), 100)),
  );
  expect(t.ma60.at(-1)).toBe(100);
  expect(t.upper.at(-1)).toBe(100);
  expect(t.lower.at(-1)).toBe(100);
  expect(t.macd.at(-1)).toBe(0);
});
test("筛选指标：区间收益、回撤、缺失与截止日无未来数据", () => {
  const data = {
    bars: [
      bar("2024-01-01", 100),
      bar("2024-01-02", 120),
      bar("2024-01-03", 60),
      bar("2024-01-04", 90),
    ],
  } as StockResult;
  const result = snapshot(data, "2024-01-01", "2024-01-04");
  expect(result.return).toBeCloseTo(-0.1);
  expect(result.maxDrawdown).toBe(-0.5);
  expect(result.observations).toBe(3);
  expect(result.high252).toBeUndefined();
  expect(result.return1y).toBeUndefined();
  const future = { ...data, bars: [...data.bars, bar("2025-01-01", 99999)] };
  expect(snapshot(future, "2024-01-01", "2024-01-04")).toEqual(result);
  expect(snapshot(undefined, "2024-01-01", "2024-01-04")).toEqual({});
});
test("资产分类仅使用已有元数据", () => {
  expect(
    assetType({ sector: "黄金ETF", name: "SPDR Gold Shares" } as never),
  ).toBe("ETF");
  expect(assetType({ sector: "能源", name: "BP ADR" } as never)).toBe("ADR");
  expect(assetType({ sector: "科技", name: "Apple" } as never)).toBe("股票");
});

test("曲线以所选区间为基期并正确预热滚动波动", () => {
  const history = Array.from({ length: 30 }, (_, i) =>
    bar("2024-01-" + String(i + 1).padStart(2, "0"), 100),
  );
  const path = curves(history, "2024-01-21");
  expect(path.cumulative[0]).toBe(0);
  expect(path.drawdown.every((v) => v === 0)).toBeTruthy();
  expect(path.volatility.every((v) => v === 0)).toBeTruthy();
});
