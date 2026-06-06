# Legacy Docs and Generated Assets Guidelines

> Scope: `docs/` — legacy Sphinx source, architecture notes, and generated proxy-list assets.

## Current Role

`web/` is the active published docs framework. Files under `docs/source/` are legacy Sphinx-era content and reference material unless a task explicitly targets Sphinx.

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
| Legacy docs alias | `cd docs && make html` delegates to the active web build |
| Strict source validation | `uv run proxywhirl sources --validate --fail-on-unhealthy --timeout 5 --concurrency 5` |

## Boundaries

**Always:**

- Preserve generated proxy-list data unless the task explicitly regenerates proxy exports.
- Keep generated proxy-list README wording consistent between `docs/proxy-lists/README.md` and `web/public/proxy-lists/README.md`.
- Prefer updating active Fumadocs pages in `web/content/docs/` for published docs changes.

**Never:**

- Treat `docs/Makefile` or Sphinx config as the active docs build path without verifying the user explicitly requested Sphinx.
- Hand-edit generated proxy-list data files to fake freshness or health.
- Commit `.DS_Store`, Sphinx build output, local caches, or generated reports.
