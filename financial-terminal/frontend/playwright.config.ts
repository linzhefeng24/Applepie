import { defineConfig } from "@playwright/test";
import { execFileSync } from "node:child_process";
import { readConfig } from "./config";
const cfg = readConfig("test");
function browserPath() {
  if (cfg.CHROMIUM_PATH) return cfg.CHROMIUM_PATH;
  for (const name of ["chromium", "chromium-browser", "google-chrome"]) {
    try {
      return execFileSync("which", [name], {
        encoding: "utf8",
        stdio: ["ignore", "pipe", "ignore"],
      }).trim();
    } catch {}
  }
  return undefined; // Use Playwright's installed browser: npx playwright install chromium.
}
export default defineConfig({
  testDir: "tests",
  workers: 1,
  timeout: 120000,
  use: {
    baseURL:
      cfg.FRONTEND_URL || `http://${cfg.FRONTEND_HOST}:${cfg.FRONTEND_PORT}`,
    headless: true,
    viewport: { width: 1536, height: 1024 },
    launchOptions: {
      executablePath: browserPath(),
      args: ["--no-sandbox", "--disable-dev-shm-usage"],
    },
  },
  reporter: "list",
});
