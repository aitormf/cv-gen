import { defineConfig } from 'vite'

const backendUrl = process.env.VITE_BACKEND_URL ?? 'http://localhost:8000'

export default defineConfig({
  server: {
    proxy: {
      '/api': backendUrl,
    },
  },
})
