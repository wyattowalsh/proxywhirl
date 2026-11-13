import { createMDX } from "fumadocs-mdx/next"

const proxyListGithubBase =
  "https://raw.githubusercontent.com/wyattowalsh/proxywhirl/main/docs/proxy-lists"

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  experimental: {
    optimizePackageImports: ["lucide-react", "recharts"],
  },
  async rewrites() {
    if (process.env.VERCEL !== "1") {
      return []
    }
    return {
      beforeFiles: [
        {
          source: "/proxy-lists/:path*",
          destination: `${proxyListGithubBase}/:path*`,
        },
      ],
    }
  },
  turbopack: {
    root: import.meta.dirname,
  },
}

const withMDX = createMDX()

export default withMDX(nextConfig)
