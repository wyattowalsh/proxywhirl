## Why

ProxyWhirl's local `main` checkout is a 310-record dirty worktree (327 paths when
untracked directories are expanded) rooted at
`040fa6a001097bf21828687439a3ba206066a08c`, with overlapping package,
runtime, API, deployment, workflow, and generated-documentation changes that
cannot be released safely without one compatibility and assurance contract.
The immediate release target is `0.4.0rc1` followed by `0.4.0`, while the latest
known scheduled Security Scan is red and the verified live `main` revision has
no GitHub Actions proof.

## What Changes

- Stabilize and integrate the existing dirty-tree work without resetting,
  stashing, or silently discarding user changes.
- Preserve the `0.3.3` public Python, CLI, REST, MCP, configuration, and
  persisted-data contracts; use tested deprecation paths and migration notes
  for intentional evolution instead of unannounced breaks.
- Finish packaging and Alembic convergence, request-lifecycle correctness,
  storage-backend parity, and the in-progress package splits behind stable
  facades.
- Harden REST authentication, streaming bounds, SSRF defenses, and credential
  redaction, together with CLI and MCP secret-handling boundaries.
- Make Docker, Compose, Helm, workflows, release metadata, OpenAPI, generated
  docs, and public artifacts deterministic and mutually consistent; deployment
  assurance is limited to safe single-replica configurations in this program.
- Clear the remote security gate. The latest known failed scheduled Security
  Scan is run `31285534474` at
  `3a2222c47b589f36ce245fecd6f4dad9bc5f9147`; Safety job `93173499813`, step
  `Run Safety check`, reports 11 vulnerabilities across cryptography 47.0.0
  (1), joserfc 1.6.4 (2), pydantic-settings 2.14.0 (1), pyjwt 2.12.1 (5), and
  soupsieve 2.8.3 (2).
- Prove the release train in two stages: `0.4.0rc1` must pass the complete local
  and remote assurance matrix before `0.4.0` promotion, and final promotion
  must repeat all drift-prone checks on the exact release SHA.
- Maintain a hyperfine task DAG with exclusive writer ownership, dependency
  barriers, explicit stop rules, and single writers for manifests, workflows,
  release metadata, Kubernetes/Helm, and generated documentation.
- No commit, push, tag, publication, deployment, destructive cleanup, or secret
  access is authorized by this change artifact alone.

## Capabilities

### New Capabilities

- `public-contract-continuity`: Preserve the shipped `0.3.3` public and persisted contracts through `0.4.x` with explicit, tested deprecations and migrations.
- `runtime-state-correctness`: Define request lifecycle, proxy health, concurrency, persistence, migration, and backend-parity invariants.
- `interface-security-boundaries`: Define authentication, SSRF, streaming, redaction, and secret-handling requirements across REST, CLI, and MCP.
- `deterministic-delivery-surfaces`: Keep package metadata, deployment manifests, OpenAPI, generated docs, and public artifacts reproducible and consistent.
- `release-assurance`: Gate `0.4.0rc1` and `0.4.0` on exact-SHA local and remote evidence, including a clean dependency-security result.

### Modified Capabilities

None. `openspec/specs/` contains no existing canonical capability specs; this
umbrella change establishes the initial contracts.

## Impact

- **Core and public API:** `proxywhirl/**`, especially package facades, models,
  rotators, strategies, retry/circuit/rate limiting, storage/migrations,
  fetchers, sources, API, CLI, MCP, configuration, and exports.
- **Contracts and tests:** `tests/unit/**`, `tests/integration/**`,
  `tests/property/**`, `tests/api/**`, and `tests/contract/**`.
- **Dependencies and packaging:** `pyproject.toml`, `uv.lock`, package entry
  points, wheels/sdists, and Alembic heads.
- **Operations and delivery:** `.github/workflows/**`, `Dockerfile`, Compose,
  `deploy/**`, release automation, source validation, and security scanning.
- **Documentation and generated assets:** `README.md`, `AGENTS.md`,
  `web/content/docs/**`, `web/content/generated/**`, `web/public/**`, and the
  generation scripts that own them.
- **Baseline split:** local work is rooted at `040fa6a001097bf21828687439a3ba206066a08c`;
  verified live `main` is `cba6e74875fba8181d70c33c843c4a55232a732a`
  with only Vercel status and no GitHub Actions runs. The two states must be
  reconciled deliberately, and prior July gate results are historical evidence,
  not proof for the current tree.
