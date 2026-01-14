import path from "path"
import react from "@vitejs/plugin-react"
import { defineConfig } from "vite"
import type { Connect } from "vite"
import fs from "fs"

export default defineConfig(({ command }) => ({
  plugins: [
    react(),
    // Serve Sphinx docs from /docs/ path in dev mode
    command === "serve" && {
      name: "serve-sphinx-docs",
      configureServer(server) {
        server.middlewares.use((req, res, next) => {
          // Serve Sphinx docs for /docs/ paths (maps to docs/build/)
          if (req.url?.startsWith("/docs")) {
            const urlPath = req.url.replace(/\?.*$/, "").replace(/^\/docs/, "/build")
            let filePath = path.join(__dirname, "../docs", urlPath)
            
            // Handle directory requests - serve index.html
            if (filePath.endsWith("/") || !path.extname(filePath)) {
              const indexPath = filePath.endsWith("/") 
                ? path.join(filePath, "index.html")
                : filePath + "/index.html"
              if (fs.existsSync(indexPath)) {
                filePath = indexPath
              } else if (fs.existsSync(filePath + ".html")) {
                filePath = filePath + ".html"
              }
            }

            if (fs.existsSync(filePath) && fs.statSync(filePath).isFile()) {
              const ext = path.extname(filePath)
              const contentTypes: Record<string, string> = {
                ".html": "text/html",
                ".css": "text/css",
                ".js": "application/javascript",
                ".json": "application/json",
                ".png": "image/png",
                ".jpg": "image/jpeg",
                ".svg": "image/svg+xml",
                ".woff": "font/woff",
                ".woff2": "font/woff2",
              }
              res.setHeader("Content-Type", contentTypes[ext] || "application/octet-stream")
              fs.createReadStream(filePath).pipe(res)
              return
            }
          }
          next()
        })
      },
    },
  ].filter(Boolean),
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
