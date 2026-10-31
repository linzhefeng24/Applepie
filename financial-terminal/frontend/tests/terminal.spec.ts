import { test, expect } from "@playwright/test";
test("行情终端：联动、排序、导出、板块筛选与命令搜索", async ({ page }) => {
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "行情工作台" })).toBeVisible();
  await page.locator("tbody tr").filter({ hasText: "AMZN" }).click();
  await expect(
    page.getByText("SECURITY / AMZN", { exact: true }),
  ).toBeVisible();
  await expect(
    page.getByRole("img", { name: "历史价格与股票比较" }).locator("canvas"),
  ).toHaveCount(1);
  await page.getByRole("button", { name: "涨跌幅" }).click();
  const changes = await page
    .locator("tbody tr td:nth-child(5)")
    .allTextContents();
  const values = changes.map((v) => Number(v.replace(/[+%,]/g, "")));
  expect(values.length).toBeGreaterThan(2);
  expect(values).toEqual([...values].sort((a, b) => b - a));
  const download = page.waitForEvent("download");
  await page.getByRole("button", { name: "导出行情 CSV" }).click();
  expect((await download).suggestedFilename()).toBe("aperture-market.csv");
  const sector = page.locator(".sector-map button").first();
  await sector.click();
  await expect(sector).toHaveAttribute("aria-pressed", "true");
  await expect(page.getByLabel("行业筛选")).not.toHaveValue("全部行业");
  await sector.click();
  await expect(page.getByLabel("行业筛选")).toHaveValue("全部行业");
  await page.keyboard.press("Control+k");
  await expect(
    page.getByRole("dialog", { name: "全局证券搜索" }),
  ).toBeVisible();
  await page.getByLabel("全局搜索股票").fill("GOOG");
  await page.keyboard.press("Enter");
  await expect(page.getByLabel("研究标的")).toHaveValue("GOOG");
  await expect(
    page.getByRole("heading", { name: "历年行情指标" }),
  ).toBeVisible();
  await page.getByRole("button", { name: "日 K", exact: true }).click();
  await expect(
    page.getByRole("button", { name: "折线", exact: true }),
  ).toBeVisible();
  await page.keyboard.press("Alt+1");
  await expect(page.getByRole("heading", { name: "行情工作台" })).toBeVisible();
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
      () => document.documentElement.scrollWidth <= window.innerWidth,
    ),
  ).toBeTruthy();
  expect(errors).toEqual([]);
});
