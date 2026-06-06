# Validation Matrix

| Surface | Command | Expected Result |
| ------- | ------- | --------------- |
| OpenSpec | `npx -y @fission-ai/openspec@latest validate --all --json` | Change artifacts validate. |
| Docs generation | `pnpm --dir web run docs:generate` | Generated references and public proxy-list assets match source files. |
| Docs lint | `pnpm --dir web run lint` | ESLint exits with `--max-warnings 0`. |
| Docs tests | `pnpm --dir web run test:run` | Vitest tests pass. |
| Docs build | `pnpm --dir web run build` | Next.js + Fumadocs build succeeds without actionable warnings. |
| README badges | `uv run python <badge-check>` | ShieldCN badge endpoints return successful SVG responses. |
| Source validation | `uv run proxywhirl sources --validate --fail-on-unhealthy --timeout 5 --concurrency 5` | Enabled source catalog is healthy, or any external-network blocker is documented explicitly. |
