# Proposal

## Problem

ProxyWhirl documentation stewardship now spans the active Fumadocs site, legacy
`docs/` assets, README badges, proxy-list publication, and agent instructions.
Several docs surfaces still described stale Sphinx-era workflows or omitted the
strict source, CLI, CI, and website proxy-list checks maintainers now use before
claiming production readiness.

## Intent

Synchronize docs and agent guidance around the current published docs surface:
Next.js + Fumadocs under `web/`, generated references from
`web/scripts/generate-docs.mjs`, and proxy-list assets mirrored from
`docs/proxy-lists/` into `web/public/proxy-lists/`.

## Scope

- Refresh root and nested `AGENTS.md` guidance for the active docs framework,
  docs-steward usage, ShieldCN README badges, source validation, CI log
  assurance, and generated-path boundaries.
- Update README badges to use ShieldCN SVG endpoints with actual
  owner/repository/package links.
- Improve active docs pages for production gates, CLI smoke tests, proxy-list
  website verification, and testing-gap closure.
- Keep proxy-list READMEs synchronized between source assets and public website
  assets.
- Adjust docs generation so every public proxy-list artifact documented for the
  website is mirrored by the generator.
- Fix the verified API startup warning where a new configured SQLite storage
  path was loaded before schema initialization.

## Out Of Scope

- Python runtime behavior beyond the narrow API storage initialization fix, REST
  routes, database schema changes, package dependencies, workflow contract
  changes, or public API changes.
- Regenerating live proxy data or modifying generated proxy data to fake source
  health.
- Adding legacy Sphinx as the active documentation path again.

## Risks

- Documentation can overstate production readiness if local and remote gates are
  not actually rerun after the docs refresh.
- Proxy-list website docs can drift if generated public assets are hand-edited
  instead of mirrored from `docs/proxy-lists/`.
