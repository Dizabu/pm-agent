import react from "@vitejs/plugin-react"
import { defineConfig } from "vite"

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/agent": "http://localhost:8001",
      "/tasks": "http://localhost:8001",
    },
  },
})