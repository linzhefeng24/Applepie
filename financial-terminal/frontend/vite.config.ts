import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwind from "@tailwindcss/vite";
const proxy = Object.fromEntries(
  [
    ["market", 8101],
    ["portfolio", 8102],
    ["analysis", 8103],
  ].map(([s, p]) => [
    `/api/${s}`,
    { target: `http://127.0.0.1:${p}`, changeOrigin: true, timeout: 180000 },
  ]),
);
export default defineConfig({
  plugins: [react(), tailwind()],
  server: { port: 5173, strictPort: true, proxy },
  preview: { port: 4173, strictPort: true, proxy },
  build: { minify: false },
});
