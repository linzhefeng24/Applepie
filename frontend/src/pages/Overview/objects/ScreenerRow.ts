import type { Stock } from "../../../objects/market";
export type ScreenerRow = {
  stock: Stock;
  values: Record<string, number | undefined>;
};
