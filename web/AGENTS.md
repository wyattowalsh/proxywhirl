# Web Docs Agent Guidelines

> Scope: `web/` — active Next.js + Fumadocs documentation site.

## Stack

| Surface | Tooling |
| ------- | ------- |
| Framework | Next.js App Router + Fumadocs |
| Package manager | `pnpm` |
| Content | `web/content/docs/**/*.mdx` |
| Generated docs | `web/content/docs/generated/` |
| Generated data | `web/content/generated/` |
| Public proxy assets | `web/public/proxy-lists/` mirrored from `docs/proxy-lists/` |

## Commands

| Task | Command |
| ---- | ------- |
| Generate references | `pnpm --dir web run docs:generate` |
| Lint | `pnpm --dir web run lint` |
| Unit tests | `pnpm --dir web run test:run` |
| Build | `pnpm --dir web run build` |
| E2E | `pnpm --dir web run test:e2e` |

## Boundaries

**Always:**

- Edit source docs in `web/content/docs/**/*.mdx`.
- Treat `web/content/docs/generated/` and `web/content/generated/` as script-owned outputs from `web/scripts/generate-docs.mjs`.
- Treat `web/public/proxy-lists/` as mirrored output; edit `docs/proxy-lists/` source files, then run `pnpm --dir web run docs:generate`.
- Run `pnpm --dir web run docs:generate` after Python API, REST API, CLI, strategy, or source-catalog changes.
- Keep docs build logs free of actionable warnings and errors before claiming production readiness.

**Never:**

- Edit `web/node_modules/`.
- Commit local `.next/`, coverage, Playwright reports, or cache output.
- Change framework dependencies or lockfiles unless the user explicitly asks or a verified docs gate requires it.

## Docs Steward

Use docs-steward for README, AGENTS, public docs, generated-reference, and documentation-pipeline changes. If multiple docs frameworks are present, treat this `web/` Fumadocs site as the active published docs framework unless the user explicitly targets legacy Sphinx.
