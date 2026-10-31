import { test, expect } from "@playwright/test";
test("真实数据库：股票、自选、比较、量化、回测、报告和导出", async ({
  page,
  request,
}) => {
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "行情工作台" })).toBeVisible();
  await expect(
    page.locator("table").getByText("Apple", { exact: true }),
  ).toBeVisible();
  await page.screenshot({
    path: "../docs/screenshots/overview.png",
    fullPage: true,
  });
  const watchBefore = await (
    await request.post("/api/portfolio/listwatchlist", { data: {} })
  ).json();
  const wasSelected = watchBefore.symbols.includes("AAPL");
  await page
    .getByRole("button", {
      name: wasSelected ? "移除自选 AAPL" : "添加自选 AAPL",
      exact: true,
    })
    .click();
  await expect(
    page.getByRole("button", {
      name: wasSelected ? "添加自选 AAPL" : "移除自选 AAPL",
      exact: true,
    }),
  ).toBeVisible();
  await request.post("/api/portfolio/setwatchlist", {
    data: { symbol: "AAPL", selected: wasSelected },
  });
  await page.getByRole("textbox", { name: "搜索股票" }).fill("AAPL");
  await expect(page.locator("tbody tr")).toHaveCount(1);
  await page.getByRole("button", { name: "研究 AAPL", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "历年行情指标" }),
  ).toBeVisible();
  await expect(page.getByText("未提供", { exact: true })).toHaveCount(6);
  await page.getByLabel("比较标的").selectOption("GOOG");
  await expect(
    page.getByRole("heading", { name: "同区间指标对比" }),
  ).toBeVisible();
  await expect(
    page.getByRole("img", { name: "历史价格与股票比较" }).locator("canvas"),
  ).toHaveCount(1);
  await page.screenshot({
    path: "../docs/screenshots/stock.png",
    fullPage: true,
  });
  await page.goto("/lab");
  await page.getByRole("button", { name: "运行五模型分析 →" }).click();
  await expect(
    page.getByRole("heading", { name: "模型横向对照" }),
  ).toBeVisible();
  await expect(page.getByText("已收敛", { exact: true })).toHaveCount(5);
  await page.screenshot({
    path: "../docs/screenshots/lab.png",
    fullPage: true,
  });
  const title = "E2E " + Date.now();
  await page.getByLabel("报告名称").fill(title);
  await page.getByRole("button", { name: "保存到研究档案" }).click();
  await expect(
    page.getByText("已保存参数与完整结果，可在「研究档案」中查看和导出。"),
  ).toBeVisible();
  await page.goto("/reports");
  await page.getByRole("button").filter({ hasText: title }).click();
  await expect(
    page.getByRole("heading", { name: title, exact: true }),
  ).toBeVisible();
  const downloadPromise = page.waitForEvent("download");
  await page.getByRole("button", { name: "导出 Markdown" }).click();
  const file = await downloadPromise;
  expect(file.suggestedFilename()).toMatch(/research-.*\.md/);
  await page.goto("/backtest");
  await page.getByLabel("调仓间隔", { exact: true }).fill("63");
  await page.getByRole("button", { name: "运行样本外回测 →" }).click();
  await expect(page.getByRole("heading", { name: "组合净值" })).toBeVisible();
  await expect(
    page.getByRole("heading", { name: "MVSK / 调仓审计" }),
  ).toBeVisible();
  await expect(
    page.getByRole("img", { name: "样本外组合净值" }).locator("canvas"),
  ).toHaveCount(1);
  await page.screenshot({
    path: "../docs/screenshots/backtest.png",
    fullPage: true,
  });
  const csvPromise = page.waitForEvent("download");
  await page.getByRole("button", { name: "导出 CSV" }).click();
  expect((await csvPromise).suggestedFilename()).toBe("backtest-curves.csv");
  const all = await (
    await request.post("/api/portfolio/listreports", { data: {} })
  ).json();
  const created = all.reports.find((r: { title: string }) => r.title === title);
  expect(created).toBeTruthy();
  expect(
    (
      await request.post("/api/portfolio/deletereport", {
        data: { id: created.id },
      })
    ).ok(),
  ).toBeTruthy();
  expect(errors).toEqual([]);
});
test("空区间、无效日期与手机布局", async ({ page, request }) => {
  await page.goto("/stocks");
  await expect(
    page.getByRole("heading", { name: "历年行情指标" }),
  ).toBeVisible();
  await page.getByLabel("起始日期", { exact: true }).fill("2027-01-01");
  await page.getByLabel("截止日期", { exact: true }).fill("2027-12-31");
  await expect(page.getByText("当前区间没有行情，请调整日期。")).toBeVisible();
  const invalid = await request.post("/api/market/getstock", {
    data: { symbol: "AAPL", start: "2026-01-01", end: "2022-01-01" },
  });
  expect(invalid.status()).toBe(400);
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "行情工作台" })).toBeVisible();
  await page.getByLabel("展开导航").click();
  await page.getByRole("link", { name: "量化实验室 Quant laboratory" }).click();
  await expect(
    page.getByRole("heading", { name: "量化实验室", exact: true }),
  ).toBeVisible();
  await page.screenshot({
    path: "../docs/screenshots/mobile.png",
    fullPage: true,
  });
});
