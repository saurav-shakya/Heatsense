import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react()],
  server: { port: 5173 },
  // maplibre-gl v6 loads its worker via a URL relative to its own module; pre-bundling breaks that path.
  optimizeDeps: { exclude: ["maplibre-gl"] },
  // The lazily loaded map chunk is almost all maplibre-gl (~1 MB, ~280 KB gzipped); the first paint doesn't wait for it.
  build: { chunkSizeWarningLimit: 1100 },
});
