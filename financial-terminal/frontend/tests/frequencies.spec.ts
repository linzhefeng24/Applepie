import { test, expect } from "./fixtures";
import { readFile } from "node:fs/promises";
test("分钟、月年曲线与按所选频率下载真实数据", async ({ page, request }) => {
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await page.goto("/");
  await expect(page.getByLabel("K线频率").locator("option")).toHaveCount(6);
  for (const value of ["1min", "2min", "5min", "1mo", "1y", "1d"]) {
    await page.getByLabel("K线频率").selectOption(value);
    await expect(
      page.getByRole("img", { name: "联动历史行情图" }).locator("canvas"),
    ).toHaveCount(1);
    if(value==="1min")await expect(page.getByRole("status").filter({hasText:"指标 32 / 32"})).toBeVisible();
    if(value==="1min")await page.screenshot({path:"../docs/screenshots/minute.png",fullPage:true});
    if (value.endsWith("min"))
      await expect(page.locator(".frequency-note")).toContainText("2026-07-31");
  }
  await page.goto("/data");
  await expect(page.getByLabel("数据频率").locator("option")).toHaveCount(6);
  await page.getByLabel("数据频率").selectOption("2min");
  await page.getByLabel("数据起始日期").fill("2026-10-23");
  await page.getByLabel("数据截止日期").fill("2026-10-23");
  await page.getByLabel("数据下载格式").selectOption("JSON");
  const button = page.getByRole("button", { name: /下载数据/ });
  await expect(button).toBeEnabled();
  const expected = await (
    await request.post("/api/resampling/getbars", {
      data: {
        symbol: "AAPL",
        start: "2026-10-23",
        end: "2026-10-23",
        frequency: "2min",
      },
    })
  ).json();
  const download = page.waitForEvent("download");
  await button.click();
  const file = await download;
  const payload = JSON.parse(await readFile((await file.path())!, "utf8"));
  expect(payload.query.frequency).toBe("2min");
  expect(payload.rows).toHaveLength(expected.bars.length);
  expect(payload.rows[0].date).toMatch(/2026-10-23 09:30:00/);
  expect(payload.rows[0].close).toBe(expected.bars[0].close);
  // A clipped monthly query still includes the bucket labelled with the month's first day.
  await page.getByLabel("数据频率").selectOption("1mo");
  await expect(button).toBeEnabled();
  await expect(page.locator(".data-grid-scroll tbody tr")).toHaveCount(1);
  await expect(page.locator(".data-grid-scroll tbody")).toContainText(
    "2026-10-01",
  );
  expect(errors).toEqual([]);
});
