# Web Docs Agent Guidelines

> Scope: `web/` — active Next.js + Fumadocs documentation site.

## Stack

| Surface | Tooling |
| ------- | ------- |
| Framework | Next.js App Router + Fumadocs |
| Package manager | `pnpm` |
| Routes | `web/src/app/` |
| UI components | `web/src/components/`, `web/src/screens/` |
| Content | `web/content/docs/**/*.mdx` (guides, concepts, interfaces, reference) |
| Generated docs | `web/content/docs/generated/` (linked from `reference/`) |
| Generated data | `web/content/generated/` |
| Public proxy assets | `web/public/proxy-lists/` mirrored from `docs/proxy-lists/` |
| Design reference | `docs/DESIGN.md` (canonical); published overview at `/docs/project/design` |
| Project meta docs | `web/content/docs/project/` (contributing, changelog, design) |

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
- Inspect `web/package.json` before adding or importing third-party UI packages.
- Keep App Router server components as the default; isolate hooks, event handlers, browser APIs, and motion in client leaf components.
- Use Next `Link` for internal routes and native anchors for external URLs or downloadable static files.
- Give icon-only controls an accessible name, mark decorative icons/images with `aria-hidden` or empty `alt`, and preserve visible focus states.
- Honor `prefers-reduced-motion`, avoid `transition-all`, and animate `transform` or `opacity` unless a data bar explicitly requires a scoped property transition.
- Avoid emoji as UI icons or labels; use installed SVG icon libraries or text labels.

**Never:**

- Edit `web/node_modules/`.
- Commit local `.next/`, coverage, Playwright reports, or cache output.
- Change framework dependencies or lockfiles unless the user explicitly asks or a verified docs gate requires it.

## Docs Steward

Use docs-steward for README, AGENTS, public docs, generated-reference, and documentation-pipeline changes. If multiple docs frameworks are present, treat this `web/` Fumadocs site as the active published docs framework unless the user explicitly targets legacy Sphinx.

| Search | Orama via `web/src/app/api/search/route.ts` |
