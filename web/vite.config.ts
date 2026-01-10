import path from "path"
import react from "@vitejs/plugin-react"
import { defineConfig } from "vite"

export default defineConfig(({ command }) => ({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    fs: {
      // Allow serving files from docs directory for development
      allow: [".", "../docs"],
    },
  },
  // Serve proxy-lists from docs/ in dev mode
  publicDir: command === "serve" ? "../docs" : "public",
}))
