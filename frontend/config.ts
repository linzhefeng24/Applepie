import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { loadEnv } from "vite";
export const projectRoot = fileURLToPath(new URL("../", import.meta.url));
export function readConfig(mode = "development"): Record<string, string> {
  const defaults = JSON.parse(
    readFileSync(new URL("../config/defaults.json", import.meta.url), "utf8"),
  ) as Record<string, string>;
  const result = {
    ...defaults,
    ...loadEnv(mode, projectRoot, ""),
    ...Object.fromEntries(
      Object.entries(process.env).filter(
        (p): p is [string, string] => p[1] !== undefined,
      ),
    ),
  };
  const explicit = { ...loadEnv(mode, projectRoot, ""), ...process.env };
  for (const [next, old] of [
    ["WATCHLIST", "PORTFOLIO"],
    ["OPTIMIZATION", "ANALYSIS"],
    ["CATALOG", "MARKET"], ["DAILY", "HISTORY"], ["QUANT_OPTIMIZER", "QUANT"],
  ]) {
    for (const suffix of ["_PORT", "_URL"]) {
      if (!explicit[next + suffix] && explicit[old + suffix])
        result[next + suffix] = explicit[old + suffix]!;
    }
  }
  return result;
}
