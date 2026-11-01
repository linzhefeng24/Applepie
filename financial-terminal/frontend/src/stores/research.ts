import { create } from "zustand";
import type { Market } from "../objects/market";
interface ResearchStore {
  market: Market | null;
  watchlist: string[];
  symbols: string[];
  selectedStock: string;
  setMarket: (market: Market) => void;
  setWatchlist: (watchlist: string[]) => void;
  setSymbols: (symbols: string[]) => void;
  selectStock: (symbol: string) => void;
}
const useResearchStore = create<ResearchStore>((set) => ({
  market: null,
  watchlist: [],
  symbols: ["AAPL", "AMZN", "GOOG", "BAC", "GLD"],
  selectedStock: "AAPL",
  setMarket: (market) => set({ market }),
  setWatchlist: (watchlist) => set({ watchlist }),
  setSymbols: (symbols) => set({ symbols }),
  selectStock: (selectedStock) => set({ selectedStock }),
}));
export const useMarket = () => useResearchStore((s) => s.market);
export const useWatchlist = () => useResearchStore((s) => s.watchlist);
export const useSymbols = () => useResearchStore((s) => s.symbols);
export const useSelectedStock = () => useResearchStore((s) => s.selectedStock);
export const setMarket = (v: Market) =>
  useResearchStore.getState().setMarket(v);
export const setWatchlist = (v: string[]) =>
  useResearchStore.getState().setWatchlist(v);
export const setSymbols = (v: string[]) =>
  useResearchStore.getState().setSymbols(v);
export const selectStock = (v: string) =>
  useResearchStore.getState().selectStock(v);

export const clearResearch = () => useResearchStore.setState({market:null,watchlist:[],symbols:["AAPL","AMZN","GOOG","BAC","GLD"],selectedStock:"AAPL"});
