import { writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const webRoot = join(dirname(fileURLToPath(import.meta.url)), "..");
const baseUrl = process.env.PROXYWHIRL_SITE_URL ?? "https://www.proxywhirl.com";
const generatedAt = new Date().toISOString();

const content = `# ProxyWhirl

> Production-grade Python proxy rotation library with live proxy lists, REST API, MCP server, and canonical Fumadocs documentation.

Generated: ${generatedAt}

## Start Here

- [Documentation home](${baseUrl}/docs)
- [Quickstart](${baseUrl}/docs/quickstart)
- [Guides](${baseUrl}/docs/guides)
- [Concepts](${baseUrl}/docs/concepts)
- [Interfaces (REST + MCP)](${baseUrl}/docs/interfaces)
- [Reference](${baseUrl}/docs/reference)

## Generated Reference

- [Python API](${baseUrl}/docs/generated/python-api)
- [CLI reference](${baseUrl}/docs/generated/cli-reference)
- [REST API summary](${baseUrl}/docs/generated/rest-api)
- [OpenAPI endpoints](${baseUrl}/docs/api/openapi)
- [Proxy sources catalog](${baseUrl}/docs/generated/proxy-sources)
- [Rotation strategies](${baseUrl}/docs/generated/strategies)

## Key Guides

- [Clients (sync/async)](${baseUrl}/docs/guides/clients)
- [Configuration](${baseUrl}/docs/guides/configuration)
- [Custom strategies](${baseUrl}/docs/guides/custom-strategies)
- [Retry & failover](${baseUrl}/docs/guides/retry-failover)
- [Deployment](${baseUrl}/docs/guides/deployment)
- [Troubleshooting](${baseUrl}/docs/guides/troubleshooting)

## Live Assets

- [HTTP proxy list](${baseUrl}/proxy-lists/http.txt)
- [All proxies](${baseUrl}/proxy-lists/all.txt)
- [Rich JSON export](${baseUrl}/proxy-lists/proxies-rich.json)

## Repository

- [GitHub](https://github.com/wyattowalsh/proxywhirl)
- [AGENTS.md](https://github.com/wyattowalsh/proxywhirl/blob/main/AGENTS.md)
`;

writeFileSync(join(webRoot, "public", "llms.txt"), content);
console.log("Wrote public/llms.txt");
