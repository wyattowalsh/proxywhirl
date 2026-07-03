# Legacy Docs and Generated Assets Guidelines

> Scope: `docs/` — commitizen changelog, design reference, and generated proxy-list/stats assets.

## Current Role

`web/content/docs/` (Fumadocs) is the sole active published docs framework. The legacy Sphinx source tree (`docs/source/`) and duplicate hand-written guides that used to live under `docs/` have been removed in favor of the published docs site — do not recreate them.

The contributor guide is canonical at the repo root ([`CONTRIBUTING.md`](../CONTRIBUTING.md)); `web/content/docs/project/contributing.mdx` links to it. The FAQ is canonical at [`web/content/docs/project/faq.mdx`](../web/content/docs/project/faq.mdx) (published at `/docs/project/faq`).

## Canonical Project Docs

| Path | Purpose |
| ---- | ------- |
| `docs/CHANGELOG.md` | Release history (`commitizen` source of truth) |
| `docs/DESIGN.md` | Web/docs design system (canonical; root `DESIGN.md` is a pointer stub) |

## Generated Assets

| Path | Source of Truth |
| ---- | --------------- |
| `docs/proxy-lists/*.txt` | `uv run proxywhirl fetch` / `uv run proxywhirl export` flows |
| `docs/proxy-lists/*.json` | Generated export metadata and rich proxy data |
| `docs/assets/stats*.svg` / stats data | Generated project/readme assets |

## Commands

| Task | Command |
| ---- | ------- |
| Active docs generation | `pnpm --dir web run docs:generate` |
| Active docs build | `pnpm --dir web run build` |
| Strict source validation | `uv run proxywhirl sources --validate --fail-on-unhealthy --timeout 5 --concurrency 5` |

## Boundaries

**Always:**

- Preserve generated proxy-list data unless the task explicitly regenerates proxy exports.
- Keep generated proxy-list README wording consistent between `docs/proxy-lists/README.md` and `web/public/proxy-lists/README.md`.
- Make published docs changes in `web/content/docs/` (Fumadocs MDX), not by adding new files under `docs/`.

**Never:**

- Recreate a Sphinx source tree, standalone deployment/troubleshooting/quickstart guides, or other duplicate narrative docs under `docs/`; those belong in `web/content/docs/`.
- Hand-edit generated proxy-list data files to fake freshness or health.
- Commit `.DS_Store`, build output, local caches, or generated reports.
