import { test, expect } from "@playwright/test";
import { readFile } from "node:fs/promises";
test("历史数据访问、精度、JSON/CSV 下载及 OpenAPI", async ({
  page,
  request,
}) => {
  const errors: string[] = [];
  page.on("pageerror", (error) => errors.push(error.message));
  await page.goto("/data");
  await expect(page.getByRole("heading", { name: "数据中心" })).toBeVisible();
  const downloadButton = page.getByRole("button", { name: /下载数据/ });
  await expect(downloadButton).toBeEnabled();
  await expect(page.locator(".data-grid-scroll tbody tr")).toHaveCount(100);
  await page.getByLabel("数据起始日期").fill("2026-01-01");
  await page.getByLabel("数据截止日期").fill("2026-10-23");
  await page.getByLabel("包含技术指标").check();
  const result = await request.post("/api/statistics/getstock", {
    data: { symbol: "AAPL", start: "2026-01-01", end: "2026-10-23" },
  });
  const source = await result.json();
  await page.getByLabel("数据下载格式").selectOption("JSON");
  let pending = page.waitForEvent("download");
  await downloadButton.click();
  const file = await pending;
  const payload = JSON.parse(await readFile((await file.path())!, "utf8"));
  expect(payload.query.symbols).toEqual(["AAPL"]);
  expect(payload.rows).toHaveLength(source.bars.length);
  expect(payload.rows[0].close).toBe(source.bars[0].close);
  expect(payload.rows[0].ma20).not.toBeNull();
  expect(payload.provenance.sha256).toMatch(/^[0-9a-f]{64}$/);
  await page.getByRole("button", { name: "组合成分", exact: true }).click();
  await page.getByLabel("数据下载格式").selectOption("CSV");
  await expect(downloadButton).toBeEnabled();
  pending = page.waitForEvent("download");
  await downloadButton.click();
  const csv = await readFile((await (await pending).path())!, "utf8");
  expect(csv).toContain("ma20");
  expect(csv).toContain("AAPL");
  expect(csv).toContain("GLD");
  await page.getByRole("button", { name: "数据质量", exact: true }).click();
  await expect(page.getByText("来源与计算口径", { exact: true })).toBeVisible();
  await expect(page.locator(".data-quality tbody tr")).toHaveCount(32);
  await page.getByRole("button", { name: "API 访问", exact: true }).click();
  await expect(page.locator(".api-reference pre")).toContainText(
    "/api/statistics/getstock",
  );
  for (const service of [
    "market",
    "history",
    "statistics",
    "watchlist",
    "reports",
    "optimization",
    "backtest",
  ]) {
    const spec = await (
      await request.get(`/api/${service}/openapi.json`)
    ).json();
    expect(spec.openapi).toBe("3.0.3");
    expect(Object.keys(spec.paths).length).toBeGreaterThan(0);
  }
  await page.screenshot({
    path: "../docs/screenshots/data.png",
    fullPage: true,
  });
  expect(errors).toEqual([]);
});
