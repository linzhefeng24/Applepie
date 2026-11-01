import { test, expect } from "./fixtures";
test("证券筛选：资产、可选指标、条件、排序、持久化及联动", async ({
  page,
  request,
}) => {
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "证券筛选" })).toBeVisible();
  await expect(
    page.getByRole("status").filter({ hasText: "指标 32 / 32" }),
  ).toBeVisible({timeout: 30000});
  await expect(page.locator(".screen-table tbody tr")).toHaveCount(32);
  await page.getByLabel("资产类别", { exact: true }).selectOption("ETF");
  await expect(page.locator(".screen-table tbody tr")).toHaveCount(1);
  await expect(page.locator(".screen-table tbody")).toContainText("GLD");
  await page.getByLabel("资产类别", { exact: true }).selectOption("ADR");
  await expect(page.locator(".screen-table tbody tr")).toHaveCount(1);
  await expect(page.locator(".screen-table tbody")).toContainText("BP");
  await page.getByLabel("资产类别", { exact: true }).selectOption("全部证券");
  await page.getByLabel("行业筛选").selectOption("医疗");
  await expect(page.locator(".screen-table tbody tr")).toHaveCount(4);
  await page.getByLabel("行业筛选").selectOption("全部行业");
  await page.getByRole("button", { name: "字段设置", exact: true }).click();
  await page.getByLabel("显示 RSI14", { exact: true }).check();
  await page.getByLabel("显示 超额峰度", { exact: true }).check();
  await page.getByRole("button", { name: "关闭字段设置" }).click();
  await expect(page.locator(".screen-table th")).toContainText([
    "RSI14",
    "超额峰度",
  ]);
  await page.reload();
  await expect(
    page.getByRole("status").filter({ hasText: "指标 32 / 32" }),
  ).toBeVisible({timeout: 30000});
  await expect(page.locator(".screen-table th")).toContainText([
    "RSI14",
    "超额峰度",
  ]);
  await page.getByRole("button", { name: "条件筛选", exact: true }).click();
  await page.getByRole("button", { name: "添加条件" }).click();
  await page.getByLabel("筛选指标", { exact: true }).selectOption("rsi14");
  await page.getByLabel("筛选运算符", { exact: true }).selectOption("gte");
  await page.getByLabel("筛选阈值", { exact: true }).fill("60");
  const rsiValues = await page
    .locator("td[data-field=rsi14]")
    .allTextContents();
  expect(rsiValues.length).toBeGreaterThan(0);
  expect(rsiValues.every((v) => Number(v) >= 59.995)).toBeTruthy();
  await page.getByRole("button", { name: "清空", exact: true }).click();
  await page.getByRole("button", { name: "日涨跌", exact: true }).click();
  const changes = (
    await page.locator("td[data-field=change]").allTextContents()
  ).map((v) => Number(v.replace("%", "")));
  expect(changes).toEqual([...changes].sort((a, b) => b - a));
  // Compare the new screener's period metrics to the existing Scala statistics API.
  const start = await page.getByLabel("筛选起始日期").inputValue(),
    end = await page.getByLabel("筛选截止日期").inputValue();
  const response = await request.post("/api/statistics/getstock", {
    data: { symbol: "AAPL", start, end },
  });
  const data = await response.json();
  const row = page
    .locator(".screen-table tbody tr")
    .filter({ has: page.getByRole("button", { name: "AAPL", exact: true }) });
  const volatility = Number(
    (await row.locator("[data-field=volatility]").textContent())!.replace(
      "%",
      "",
    ),
  );
  expect(volatility).toBeCloseTo(data.metrics.volatility * 100, 2);
  const download = page.waitForEvent("download");
  await page.getByLabel("导出行情 CSV").click();
  const exported = await download;
  expect(exported.suggestedFilename()).toBe("aperture-market.csv");
  const path = await exported.path();
  const fs = await import("node:fs/promises");
  const csv = await fs.readFile(path!, "utf8");
  expect(csv).toContain("RSI14");
  expect(csv).toContain("超额峰度");
  await page
    .locator(".screen-table tbody tr")
    .filter({ hasText: "AMZN" })
    .click();
  await expect(page.locator(".dock-title")).toContainText("AMZN");
  await page.getByLabel("主图指标").selectOption("BOLL");
  await page.getByLabel("副图指标").selectOption("RSI");
  await expect(
    page.getByRole("img", { name: "联动历史行情图" }).locator("canvas"),
  ).toHaveCount(1);
  await page.getByLabel("副图指标").selectOption("MACD");
  for (const curve of ["return", "drawdown", "volatility", "price"]) {
    await page.getByLabel("曲线指标").selectOption(curve);
    await expect(
      page.getByRole("img", { name: "联动历史行情图" }).locator("canvas"),
    ).toHaveCount(1);
  }
  const png = page.waitForEvent("download");
  await page.getByLabel("导出图表 PNG").click();
  expect((await png).suggestedFilename()).toMatch(/\.png$/);
  await page.getByLabel("隐藏联动图表").click();
  await expect(page.locator(".security-dock")).toHaveCount(0);
  await page.getByLabel("显示联动图表").click();
  await expect(page.locator(".security-dock")).toBeVisible();
  await page.keyboard.press("Control+k");
  await page.getByLabel("全局搜索股票").fill("GOOG");
  await page.keyboard.press("Enter");
  await expect(page.getByLabel("研究标的")).toHaveValue("GOOG");
  await page.keyboard.press("Alt+1");
  await expect(page.getByRole("heading", { name: "证券筛选" })).toBeVisible();
  await expect(
    page.getByRole("status").filter({ hasText: "指标 32 / 32" }),
  ).toBeVisible({timeout: 30000});
  await page.getByRole("button", { name: "行情", exact: true }).click();
  await page.screenshot({
    path: "../docs/screenshots/terminal-desktop.png",
    fullPage: true,
  });
  await page.setViewportSize({ width: 390, height: 844 });
  await page.screenshot({
    path: "../docs/screenshots/terminal-mobile.png",
    fullPage: true,
  });
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBeTruthy();
  expect(errors).toEqual([]);
});
