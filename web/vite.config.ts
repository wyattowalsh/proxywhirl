import path from "path"
import react from "@vitejs/plugin-react"
import { defineConfig } from "vite"
import type { Connect, ViteDevServer } from "vite"
import type { IncomingMessage, ServerResponse } from "http"
import fs from "fs"
import { VitePWA } from "vite-plugin-pwa"

export default defineConfig(({ command }) => ({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'vendor-charts': ['recharts'],
          'vendor-maps': ['react-simple-maps', 'topojson-client'],
          'vendor-motion': ['motion'],
          'vendor-radix': ['@radix-ui/react-dropdown-menu', '@radix-ui/react-slot', '@radix-ui/react-tabs'],
        },
      },
    },
  },
  plugins: [
    react(),
    VitePWA({
      registerType: "autoUpdate",
      includeAssets: ["favicon.svg", "robots.txt"],
      manifest: {
        name: "ProxyWhirl",
        short_name: "ProxyWhirl",
        description: "High-quality free proxy lists updated every 2 hours",
        theme_color: "#0f172a",
        background_color: "#0f172a",
        display: "standalone",
        icons: [
          {
            src: "favicon.svg",
            sizes: "any",
            type: "image/svg+xml",
            purpose: "any maskable"
          }
        ]
      },
      workbox: {
        globPatterns: ["**/*.{js,css,html,ico,png,svg,json}"],
        globIgnores: ["**/proxies*.json", "proxy-lists/**", "docs/**", "**/all.txt", "**/http.txt", "**/https.txt", "**/socks*.txt"],
        navigateFallbackDenylist: [/^\/docs/],
        maximumFileSizeToCacheInBytes: 3000000 // 3MB (geo-data is ~100kb, but just in case)
      }
    }),
    // Serve Sphinx docs from /docs/ path in dev mode
    command === "serve" && {
      name: "serve-sphinx-docs",
      configureServer(server: ViteDevServer) {
        server.middlewares.use((req: Connect.IncomingMessage, res: ServerResponse, next: Connect.NextFunction) => {
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
