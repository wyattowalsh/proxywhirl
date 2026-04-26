---
name: curate-sources
description: >
  Curate proxywhirl proxy sources — prune broken/stale/duplicate sources and discover
  new high-quality ones via web research. Syncs all downstream files: sources.py, tests,
  docs, and reference inventories. Use when asked to update, clean up, audit, curate,
  or refresh proxy sources.
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

## Quick Start

Invoke the `source-curator` agent:
```
/agent source-curator
```

Or run the validation script directly:
```bash
uv run python scripts/curate_sources.py validate          # Full validation report (JSON)
uv run python scripts/curate_sources.py check-candidate URL  # Check a candidate source
```

## Workflow

1. **Validate** — Run `scripts/curate_sources.py validate` to get health status of all sources
2. **Prune** — Remove or disable sources that are broken, stale, or duplicates
3. **Discover** — Search GitHub and the web for new proxy list repos/APIs
4. **Integrate** — Add new sources and remove pruned ones in `sources.py`
5. **Sync downstream** — Update reference inventory, tests, and docs
6. **Verify** — Run lint + all source-related tests to ensure nothing is broken

## Files That Must Stay in Sync

See the full file inventory in [`.claude/agents/source-curator.md`](../../agents/source-curator.md#files-affected-by-source-changes).

Key files: `proxywhirl/sources.py` (primary), `references/known-sources.md` (inventory), `tests/unit/test_sources.py`, `tests/contract/test_proxy_sources.py`, `tests/unit/test_sources_audit.py`, `README.md` (feature card count), and all code that imports sources (`cli.py`, `tui.py`, `exports.py`, `__init__.py`).

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
| `RECOMMENDED_SOURCES` | Only the most reliable, fast, pre-validated sources (user approval required) |
| `API_SOURCES` | Only API-based sources (GeoNode, etc.) |

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
