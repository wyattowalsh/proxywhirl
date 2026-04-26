# Claude Code Agents

Custom agents for the proxywhirl project.

## Agent Index

| Agent | File | Description |
|-------|------|-------------|
| `source-curator` | [`source-curator.md`](source-curator.md) | Curates proxy sources — prunes broken/stale/duplicate sources, discovers new ones, and syncs all downstream files (tests, docs, reference inventories) |

## source-curator

**Trigger:** Invoke directly or via the `curate-sources` skill.

**Purpose:** Orchestrates a 3-agent team (pruner, discoverer, integrator) to maintain the proxy source list in `proxywhirl/sources.py` and all downstream files. The pruner analyzes existing sources for health issues, the discoverer finds new sources via GitHub and web research, and the integrator applies approved changes across sources.py, tests, docs, and reference inventories.

**Prerequisites:**
- `scripts/curate_sources.py` must exist (validation + candidate checking)
- `.claude/skills/curate-sources/` skill and references must exist

**Usage:**
```
/agent source-curator
```
