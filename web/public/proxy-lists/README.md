# Generated Proxy List Bundle

This directory contains ProxyWhirl export artifacts generated from the built-in public source catalog. GitHub Actions refreshes the bundle on the scheduled proxy-generation workflow, and the active docs build mirrors these files to the website at `/proxy-lists/`.

Do not hand-edit generated proxy data to fake freshness or source health. Regenerate through the CLI/export workflow, then validate the source catalog separately.

## Available Files

| File | Description |
| ---- | ----------- |
| `http.txt` | HTTP proxies, one per line. |
| `https.txt` | HTTPS-capable proxies, one per line. |
| `socks4.txt` | SOCKS4 proxies, one per line. |
| `socks5.txt` | SOCKS5 proxies, one per line. |
| `all.txt` | Combined plain-text proxy list. |
| `proxies.json` | Compact JSON proxy records. |
| `proxies-rich.json` | Rich JSON proxy records with additional metadata. |
| `stats.json` | Export statistics for dashboards and docs. |
| `metadata.json` | Bundle generation metadata and timestamps. |

## Validation

Run the strict source-health gate before publishing or relying on the catalog:

```bash
uv run proxywhirl sources --validate --fail-on-unhealthy --timeout 5 --concurrency 5
```

Refresh the active website copy with:

```bash
pnpm --dir web run docs:generate
```

## Usage

Download files directly from the docs site, for example:

- `https://www.proxywhirl.com/proxy-lists/http.txt`
- `https://www.proxywhirl.com/proxy-lists/metadata.json`
- `https://www.proxywhirl.com/proxy-lists/proxies-rich.json`

Use the ProxyWhirl library or CLI when you need validated runtime behavior instead of static export files.
