import { defineConfig } from "vite";
import { svelte } from "@sveltejs/vite-plugin-svelte";

const backendUrl = process.env.VITE_BACKEND_URL ?? "http://localhost:8000";

export default defineConfig({
  plugins: [svelte()],
  server: {
    proxy: {
      "/api": backendUrl,
    },
  },
});
