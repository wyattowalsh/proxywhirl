---
name: curate-sources
description: >
  Curate proxywhirl proxy sources. Use when asked to audit, prune, or add sources
  in proxywhirl/sources.py. NOT for routine `proxywhirl sources --validate`.
  Empty requests and health checks stay read-only. Prune and add require an explicit yes.
triggers:
  - curate sources
  - update sources
  - prune sources
  - find new sources
  - audit sources
  - refresh source list
  - clean up sources
  - source health check
---

# Curate Sources

Maintain the proxy source list in `proxywhirl/sources.py` and keep all downstream files in sync: tests, docs, reference inventories, and exports.

## Dispatch

| Request | Action |
| --- | --- |
| Empty, "audit", "health", "what sources" | Local census only. No network and no edits. |
| "validate" or "check this URL" | Live fetch only after the user says yes. |
| "prune" or "add" | Recommend first. Edit `sources.py` only after an explicit yes. |

## Quick Start

Local census, no network:

```bash
uv run python -c "from proxywhirl.sources import ALL_SOURCES, RECOMMENDED_SOURCES, API_SOURCES; print(len(ALL_SOURCES), len(RECOMMENDED_SOURCES), len(API_SOURCES))"
```

Live checks, only after confirmation:

```bash
uv run python scripts/curate_sources.py validate
uv run python scripts/curate_sources.py check-candidate URL
```

The curator agent is [`.claude/agents/source-curator.md`](../../agents/source-curator.md).

## Workflow

1. **Census** — Read `proxywhirl/sources.py` and `references/known-sources.md`. Do not fetch.
2. **Recommend** — List prune or add candidates. Stop unless the user asked to change the registry.
3. **Edit** — After an explicit yes, change `sources.py`. Never prune `RECOMMENDED_SOURCES` without a separate yes.
4. **Sync** — Update the inventory, tests, and docs in the same change.
5. **Verify** — Run the source unit tests. Do not run the live validator as the default check.

## Files That Must Stay in Sync

See the full file inventory in [`.claude/agents/source-curator.md`](../../agents/source-curator.md#files-affected-by-source-changes).

Key files: `proxywhirl/sources.py` (primary), `references/known-sources.md` (inventory), `tests/unit/test_sources.py`, `tests/contract/test_proxy_sources.py`, `tests/unit/test_sources_audit.py`, `README.md` (feature card count), and importers in `proxywhirl/cli/_impl.py`, `proxywhirl/exports.py`, and `proxywhirl/__init__.py`.

## References

- [Source Schema](references/source-schema.md) — ProxySourceConfig model, naming conventions, collection rules
- [Known Sources](references/known-sources.md) — Current source inventory for deduplication

## Pruning Criteria

| Condition | Action |
|-----------|--------|
| HTTP 404/410 for 7+ days | Remove entirely |
| GitHub repo archived | Remove entirely |
| GitHub repo not pushed in 90+ days | Disable (`enabled=False`) |
| GitHub repo <10 stars | Flag for review |
| Empty response / no proxy data | Disable if persistent |
| Duplicate of existing source | Remove the lower-quality one |
| In `RECOMMENDED_SOURCES` | NEVER prune without user approval |
| In `API_SOURCES` | NEVER prune (high-value) |

## Adding New Sources

New sources must meet ALL criteria:
- Returns valid proxy data (IP:PORT format)
- Updated within the last 30 days
- For GitHub repos: >50 stars preferred, active maintenance
- Not a duplicate of an existing source (check `known-sources.md`)
- Plain text format preferred (simplest parsing)

### Variable Naming Convention

| Source Type | Pattern | Example |
|-------------|---------|---------|
| GitHub repo | `GITHUB_{OWNER}_{PROTOCOL}` | `GITHUB_MONOSANS_HTTP` |
| API service | `{SERVICE}_{PROTOCOL}` | `PROXY_SCRAPE_SOCKS5` |
| Web-hosted | `{DOMAIN}_{PROTOCOL}` | `PROXYSPACE_HTTP` |

### Collection Membership

| Collection | Criteria |
|------------|----------|
| `ALL_HTTP_SOURCES` | Any source providing HTTP/HTTPS proxies |
| `ALL_SOCKS4_SOURCES` | Any source providing SOCKS4 proxies |
| `ALL_SOCKS5_SOURCES` | Any source providing SOCKS5 proxies |
| `ALL_SOURCES` | Auto-computed: HTTP + SOCKS4 + SOCKS5 |
| `RECOMMENDED_SOURCES` | `GITHUB_MONOSANS_HTTP`, `JSDELIVR_PROXIFLY_ALL`, `GITHUB_PROXIFLY_HTTP`, `GITHUB_KOMUTAN_HTTP` |
| `API_SOURCES` | Enabled API sources only. The definitions are `PROXY_SCRAPE_HTTP` and `PROXY_SCRAPE_SOCKS4`; both are disabled, so the enabled collection is empty. |

### Code Style for New Definitions

```python
# owner/repo-name - Description (stars, update frequency)
GITHUB_OWNER_PROTOCOL = ProxySourceConfig(
    url="https://raw.githubusercontent.com/owner/repo/branch/file.txt",
    format="plain_text",
    protocol="socks5",  # omit for HTTP (default)
    trusted=True,  # only if source pre-validates proxies
)
```

## Consistency Checklist

See the full checklist in [`.claude/agents/source-curator.md`](../../agents/source-curator.md#consistency-checklist-lead-must-verify).

Quick verification:
```bash
uv run python -c "from proxywhirl.sources import ALL_SOURCES; print(f'{len(ALL_SOURCES)} sources loaded')"
uv run pytest tests/unit/test_sources.py tests/unit/test_sources_audit.py tests/contract/test_proxy_sources.py -v
```
