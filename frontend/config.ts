import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { loadEnv } from "vite";
export const projectRoot = fileURLToPath(new URL("../", import.meta.url));
export function readConfig(mode = "development"): Record<string, string> {
  const defaults = JSON.parse(
    readFileSync(new URL("../config/defaults.json", import.meta.url), "utf8"),
  ) as Record<string, string>;
  return {
    ...defaults,
    ...loadEnv(mode, projectRoot, ""),
    ...Object.fromEntries(
      Object.entries(process.env).filter(
        (p): p is [string, string] => p[1] !== undefined,
      ),
    ),
  };
}
