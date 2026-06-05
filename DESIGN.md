# ProxyWhirl Design System

## Direction

ProxyWhirl uses a technical editorial dashboard style: calm density, clear hierarchy, code-first readability, and subtle network/proxy identity. The product should feel like infrastructure documentation and a live data console in the same surface.

## Principles

| Principle             | Rule                                                                                                  |
| --------------------- | ----------------------------------------------------------------------------------------------------- |
| Source-grounded       | Documentation and data cards should point back to code, generated metadata, or operational artifacts. |
| Calm density          | Prefer compact tables, grouped cards, and strong headings over sparse marketing whitespace.           |
| Code readability      | Code blocks must have high contrast, generous line height, and enough context to run.                 |
| Network identity      | Use rings, routes, gradients, and subtle motion to evoke proxy rotation without visual noise.         |
| Accessible by default | Maintain keyboard support, visible focus, semantic landmarks, and AA contrast.                        |

## Tokens

| Token      | Light                    | Dark                     | Use                            |
| ---------- | ------------------------ | ------------------------ | ------------------------------ |
| Background | `hsl(0 0% 100%)`         | `hsl(222.2 84% 4.9%)`    | Page base                      |
| Foreground | `hsl(222.2 84% 4.9%)`    | `hsl(210 40% 98%)`       | Body text                      |
| Primary    | `hsl(221.2 83.2% 53.3%)` | `hsl(217.2 91.2% 59.8%)` | Links, buttons, active states  |
| Muted      | `hsl(210 40% 96.1%)`     | `hsl(217.2 32.6% 17.5%)` | Cards, callouts, table accents |
| Border     | `hsl(214.3 31.8% 91.4%)` | `hsl(217.2 32.6% 17.5%)` | Separators and card edges      |

## Typography

Use the system sans stack for UI and prose. Preserve a compact technical rhythm: short paragraphs, scannable tables, and explicit code examples. Headings should be direct and descriptive.

## Components

| Component  | Rule                                                                                                                                |
| ---------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| Data cards | Use small metric cards for source counts, strategy counts, API path counts, and live proxy stats.                                   |
| Tables     | Use tables for generated reference surfaces; keep columns stable and sortable only when interaction adds value.                     |
| Callouts   | Use Fumadocs-native callouts for warnings, migration notes, and operational caveats.                                                |
| Navigation | Keep `/docs/` IA organized by user surfaces: quickstart, guides, concepts, API, MCP, TUI, sources, strategies, operations, project. |

## Motion

Motion should support orientation, not decoration. Use subtle hover transitions, loading indicators, and network-inspired logo movement. Avoid long-running animations in dense docs content.

## Accessibility

All interactive controls need focus-visible states and text alternatives. Data visualizations must have textual summaries or adjacent tables. Color cannot be the only state indicator.

## Implementation Rules

| Area           | Rule                                                                                           |
| -------------- | ---------------------------------------------------------------------------------------------- |
| Docs           | Fumadocs MDX under `web/content/docs` is canonical.                                            |
| Generated docs | Run `pnpm --dir web run docs:generate` before build.                                           |
| Styling        | Use Tailwind tokens from `web/src/index.css`; avoid one-off hex colors except logo gradients.  |
| Dark mode      | Preserve class-based dark mode through the shared Fumadocs provider.                           |
| Runtime scope  | Design changes must not alter Python runtime behavior, database schema, or public Python APIs. |
