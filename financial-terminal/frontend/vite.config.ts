import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwind from "@tailwindcss/vite";
import { readConfig } from "./config";
export default defineConfig(({ mode }) => {
  const cfg = readConfig(mode);
  const proxy = Object.fromEntries(
    ["market", "portfolio", "analysis"].map((service) => [
      `/api/${service}`,
      {
        target:
          cfg[service.toUpperCase() + "_URL"] ||
          `http://${cfg.SERVICE_HOST}:${cfg[service.toUpperCase() + "_PORT"]}`,
        changeOrigin: true,
        timeout: 180000,
      },
    ]),
  );
  return {
    plugins: [react(), tailwind()],
    server: {
      host: cfg.FRONTEND_HOST,
      port: Number(cfg.DEV_PORT),
      strictPort: true,
      proxy,
    },
    preview: {
      host: cfg.FRONTEND_HOST,
      port: Number(cfg.FRONTEND_PORT),
      strictPort: true,
      proxy,
    },
    build: { minify: false },
  };
});
