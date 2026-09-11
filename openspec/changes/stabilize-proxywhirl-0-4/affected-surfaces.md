# Affected Surfaces

## Baseline Authority

| Dimension | Exact baseline |
| --- | --- |
| Local branch | `main` |
| Local HEAD | `040fa6a001097bf21828687439a3ba206066a08c` |
| Collapsed status | 310 records: 201 modified, 16 deleted, 93 untracked |
| Expanded status | 327 paths: 201 modified, 16 deleted, 110 untracked files |
| Verified live `main` | `cba6e74875fba8181d70c33c843c4a55232a732a`; Vercel only, no Actions runs |
| Known failed security evidence | run `31285534474`, SHA `3a2222c47b589f36ce245fecd6f4dad9bc5f9147`, Safety job `93173499813`, 11 findings / 5 packages |
| Historical assurance | July W0-W7 results in `goals/codebase-sota-improvement/`; planning evidence only |

Expanded dirty paths by top-level surface:

| Surface | Paths | Notes |
| --- | ---: | --- |
| `proxywhirl/` | 125 | Package splits, runtime, adapters, storage, security |
| `tests/` | 85 | Unit, integration, property, API, contract proof |
| `web/` | 72 | Source MDX/UI plus generated OpenAPI/reference outputs |
| `deploy/` | 23 | Docker/Compose, Helm, Kubernetes, Terraform, local provider cache |
| `.github/` | 6 | CI, security, source, release, generation workflows |
| `docs/` | 3 | Design/spec source; not the active published framework |
| `examples/` | 2 | Public usage compatibility |
| `alembic/` | 2 | Runtime wiring and new migration revision |
| Root and one-file surfaces | 9 | `.gitignore`, `AGENTS.md`, `Dockerfile`, `README.md`, `docker-compose.yml`, `justfile`, `pyproject.toml`, `scripts/`, `uv.lock` |

## Program Ownership Map

| Lane | Primary surfaces | Depends on | Writer rule |
| --- | --- | --- | --- |
| B0-B6 control plane | Git metadata, instructions, goals ledger, OpenSpec, read-only inventories | None | Orchestrator records evidence; no product writes |
| F1 packaging/facades | `proxywhirl/__init__.py`, `models/`, `strategies/`, `fetchers/`, `cli/`, legacy monolith paths | B compatibility inventory | One facade integrator after package-internal writers finish |
| F2 configuration SSOT | `config_core.py`, `config.py`, `settings.py`, API/CLI/MCP settings | Security and public-default decisions | One configuration writer |
| F3 migrations | `alembic/**`, `migrations.py`, package migration resources | Model/storage contract | One Alembic writer; exactly one head |
| F4 storage foundation | `storage.py`, storage models/helpers, backend fixtures | F2, F3 contract | Serialize product edits; backend tests may shard |
| F5 quality harness | `justfile`, `pyproject.toml` test/coverage config, `tests/conftest.py`, hooks | B baseline | One harness/config writer |
| F6 dependency security | `pyproject.toml`, `uv.lock`, security evidence | Fresh advisory research | One manifest/lock writer; never hand-edit lock |
| F7 resource factories | httpx/browser/database client factories and lifecycle helpers | F1/F2 | One owner per shared factory |
| F8 docs/generator prerequisites | `web/package.json`, `web/pnpm-lock.yaml`, scripts and navigation prerequisites | Stable package/API inputs | One web toolchain writer |
| C1-C6 runtime behavior | rotators, orchestration, circuit breaker, retry, rate limiting, strategies, cache | Relevant F barriers | Disjoint modules parallel; shared state machines serialized |
| C7 sources/fetchers | `sources.py`, `fetchers/**`, browser/validator safety | F7, security policy | Parser/source/validator writers split only on disjoint files |
| C8 REST | `proxywhirl/api/**`, API tests | F2, C1/C7 | One API composition/auth writer |
| C9 CLI | `proxywhirl/cli/**`, CLI tests/examples | F1/F2, behavior stable | Serial command extraction/integration |
| C10 MCP | `proxywhirl/mcp/**`, MCP tests | F1/F2, auth policy | Strict serial server/auth/tools writer |
| C11 persistence/import/export | storage/export/import/migration integrations | F3/F4, C5/C7 | One cross-backend integrator |
| C12 cross-interface contracts | `tests/api/**`, `tests/contract/**`, public import/CLI/REST/MCP parity | C1-C11 | Contract writer after behavior stabilizes |
| Shared manifests | `pyproject.toml`, `uv.lock`, Docker/Compose, `deploy/**` | F/C decisions | Single writer per manifest family; common semantics serialized |
| Shared workflows/release | `.github/workflows/**`, version/release metadata | Canonical gates stable | One workflow writer, then one release writer |
| Shared generated/docs | `web/content/generated/**`, `web/content/docs/generated/**`, OpenAPI pages, `web/public/llms.txt` | Public contracts stable | Generator-only, single writer, second-run drift check |
| Shared proxy assets | `docs/proxy-lists/**`, `web/public/proxy-lists/**` | Authorized source generation | One generator writer; source/mirror pair |
| Modernization | bounded internals behind stable facades | C barriers green | Defer if scope or compatibility expands |
| J1-J9 assurance | read-only checks plus test/build artifacts | All intended writes complete | Orchestrator serializes final proof |

## Critical Shared Locks

1. `proxywhirl/__init__.py` and all public package `__init__.py` facades.
2. `pyproject.toml` with `uv.lock`.
3. Alembic versions, head, and migration packaging.
4. Configuration names/defaults across Python and adapters.
5. `proxywhirl/storage.py` and persisted schema semantics.
6. `proxywhirl/api/core.py`, auth middleware, and OpenAPI composition.
7. `proxywhirl/mcp/server.py` and MCP auth/tool registration.
8. `.github/workflows/**`.
9. release/version metadata.
10. Docker/Compose/Helm/Kubernetes shared runtime semantics.
11. `web/scripts/**` and every generated docs/OpenAPI output.
12. proxy-list source/mirror generated assets.

No two active writers may own the same lock. Test-only leaves may run in
parallel only when they do not rewrite shared fixtures, snapshots, or generated
outputs.

## Generated, Local, and Secret Boundaries

- `web/content/generated/**`, `web/content/docs/generated/**`, generated
  OpenAPI pages, and `web/public/llms.txt` are script-owned.
- `docs/proxy-lists/**` is the canonical generated proxy-asset source;
  `web/public/proxy-lists/**` is its mirror.
- `deploy/terraform/.terraform/**` and downloaded providers are local cache
  artifacts. They are never a writer target, release input, or commit surface.
- `.env*`, `*.pem`, `*.key`, secret-, credential-, and backup-named files stay
  unopened and untouched unless separately authorized through a trusted,
  narrowly scoped security task.
- `.venv/`, `dist/`, build output, coverage output, browser reports, caches,
  local databases, and user runtime files are not source surfaces.
- `uv.lock` and `web/pnpm-lock.yaml` are generated lock artifacts with exactly
  one authorized writer each; manual editing is forbidden.

## Sequencing Boundary

Source contracts and behavior stabilize first. Manifests and workflows consume
those decisions. Generated docs and public assets run after all source inputs.
Contract snapshots update only after intentional diff review. Final assurance
starts only when every writer is idle and the 310/327 baseline has a complete
path-by-path disposition.
