import { test, expect } from "./fixtures";
import {
  portfolioRisk,
  alignPrices,
} from "../src/pages/shared/functions/portfolio";
test("风险计算：波动贡献守恒、共线相关性与非法权重", () => {
  const p = [
    [100, 110, 99, 108.9],
    [100, 110, 99, 108.9],
  ];
  const r = portfolioRisk(p, [0.4, 0.6]);
  expect(r.contributions.reduce((a, b) => a + b, 0)).toBeCloseTo(
    r.volatility,
    12,
  );
  expect(r.correlation[0][1]).toBeCloseTo(1, 12);
  expect(r.maxDrawdown).toBeCloseTo(-0.1, 12);
  expect(r.var95).toBeCloseTo(0.1, 12);
  expect(r.es95).toBeCloseTo(0.1, 12);
  expect(() => portfolioRisk(p, [0.3, 0.6])).toThrow("100%");
  expect(alignPrices({}, ["AAPL"]).dates).toEqual([]);
});
test("三个独立页面：共同区间对比、组合风险与审计导出", async ({ page }) => {
  await page.goto("/compare");
  await expect(
    page.getByRole("heading", { name: "证券对比", exact: true }),
  ).toBeVisible();
  await expect(
    page.getByRole("img", { name: "多证券基期对比曲线" }).locator("canvas"),
  ).toHaveCount(1);
  let pending = page.waitForEvent("download");
  await page.getByRole("button", { name: "导出对比 CSV" }).click();
  expect((await pending).suggestedFilename()).toBe("security-comparison.csv");
  await page.getByLabel("选择 GOOG", { exact: true }).uncheck();
  await expect(page.locator("tbody tr")).toHaveCount(2);
  await page.goto("/risk");
  await expect(
    page.getByRole("heading", { name: "组合风险分析", exact: true }),
  ).toBeVisible();
  await expect(
    page.getByRole("img", { name: "组合历史回撤曲线" }).locator("canvas"),
  ).toHaveCount(1);
  await page.getByLabel("AAPL权重", { exact: true }).fill("20");
  await expect(page.getByRole("alert")).toContainText("100%");
  await expect(
    page.getByRole("button", { name: "导出风险 JSON" }),
  ).toBeDisabled();
  await page.getByRole("button", { name: "设为等权" }).click();
  await expect(page.getByRole("alert")).toHaveCount(0);
  pending = page.waitForEvent("download");
  await page.getByRole("button", { name: "导出风险 JSON" }).click();
  expect((await pending).suggestedFilename()).toBe("portfolio-risk.json");
  await page.goto("/quality");
  await expect(
    page.getByRole("heading", { name: "数据质量审计", exact: true }),
  ).toBeVisible();
  await expect(page.locator("tbody tr")).toHaveCount(32);
  await page.getByLabel("审计证券", { exact: true }).fill("AAPL");
  await expect(page.locator("tbody tr")).toHaveCount(1);
  pending = page.waitForEvent("download");
  await page.getByRole("button", { name: "导出审计 JSON" }).click();
  expect((await pending).suggestedFilename()).toBe("data-quality-audit.json");
  await page.setViewportSize({ width: 390, height: 844 });
  await page.getByLabel("展开导航").click();
  await expect(
    page.getByRole("link", { name: "证券对比 Security comparison" }),
  ).toBeVisible();
});
