import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";
export default defineConfig({
  plugins: [react()],
  server: { proxy: { "/api": "http://127.0.0.1:8102" } },
  preview: { port: 5182, strictPort: true, host: "127.0.0.1", proxy: { "/api": "http://127.0.0.1:8102" } },
  test: { environment: "jsdom", globals: true },
});
