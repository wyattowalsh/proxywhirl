# Validation Matrix

## Evidence Contract

Every recorded result includes the exact SHA, dirty-state snapshot, command,
exit code, test/coverage/finding counts, output artifact path or remote run/job
ID, and actionable warning/error marker review. Commands below are planned
proof; their presence here is not a claim that they have run on the current
tree.

| Gate | Command or evidence | Pass condition | Wave |
| --- | --- | --- | --- |
| OpenSpec | `openspec validate stabilize-proxywhirl-0-4 --json` | `valid: true`; zero errors | B3, J1 |
| Baseline collapsed | `git status --short` plus status-code count | Initial record is exactly 310: 201 M, 16 D, 93 `??`; later changes attributed | B0 |
| Baseline expanded | `git status --porcelain=v1 --untracked-files=all` plus count | Initial record is exactly 327: 201 M, 16 D, 110 `??`; later changes attributed | B0 |
| Revision split | `git rev-parse HEAD`; trusted remote SHA evidence | Local root and live remote are recorded separately; no stale SHA is treated as release proof | B0, J8 |
| Scope/secret inventory | Path/name-only status review | Local caches and secret-adjacent paths excluded without opening them | B1, J1 |
| Public imports | `uv run pytest tests/unit/test_public_api.py tests/unit/test_wave3_package_compat.py -q --no-cov -n0` | Stable and package-split imports pass | F1, C12 |
| Contract snapshots | `uv run pytest tests/contract/ -q --no-cov -n0 -m "not network"` | Snapshots change only with reviewed intentional contract delta | C12, J3 |
| CLI focused | `uv run pytest tests/unit/test_cli.py tests/unit/test_cli_config_templates.py -q --no-cov -n0` | `0.3.3` command/option/config compatibility passes | C9, J3 |
| CLI smoke | `uv run proxywhirl --no-lock --help` plus temporary-config pool/config/import/validate/source probes | Help and representative commands succeed; credentials remain redacted | C9, J6 |
| REST focused | `uv run pytest tests/api/ tests/unit/test_api.py tests/unit/test_api_auth.py tests/unit/test_api_security_wave1.py tests/integration/test_api_health.py tests/integration/test_api_requests.py -q --no-cov -n0` | Auth, SSRF, streaming, redaction, health/readiness, and schema contracts pass | C8, J3 |
| MCP focused | `uv run pytest tests/unit/test_mcp_server.py tests/integration/test_mcp_integration.py -q --no-cov -n0` | Tool/resource compatibility, write auth, redaction, and lifecycle pass | C10, J3 |
| Request lifecycle | Focused rotator/orchestration/retry/circuit/rate-limit unit, property, and integration tests | Exactly-once terminal effects, sync/async parity, and cancellation cleanup pass | C1-C5, J3 |
| Cache/concurrency | Focused cache stampede/coherence/eviction and race/property tests | No deadlock, stampede, stale tier, negative counter, or leaked task | C6, J3 |
| Sources/fetchers | Focused source, parser, validator, browser, safe-regex, and SSRF tests | Bounded parsing/network behavior and error/redaction contracts pass | C7, J3 |
| Storage parity | `uv run pytest tests/unit/test_storage.py tests/unit/test_sqlite_storage.py tests/unit/test_migrations.py -q --no-cov -n0` plus parity corpus | File/SQLite results agree and migration tests pass | F3-F4, C11 |
| Alembic topology | `uv run alembic heads` and disposable empty/`0.3.3` database `upgrade head` probes | Exactly one head; both upgrades preserve expected records | F3, J6 |
| Lint | `just lint` | Ruff exits 0 | F5, each barrier, J2 |
| Format | `just format-check` | Ruff format check exits 0 | F5, each barrier, J2 |
| Types | `just type-check` and `uv run ty check proxywhirl/ tests/` | Zero type errors; warnings reviewed | F5, each barrier, J2 |
| Fast test tier | `just test-fast` | CI-parity non-slow/non-stress/non-network suites pass | F5, C barriers, J3 |
| Full Python gate | `just quality-gates` | Lint, types, non-slow tests, and configured coverage threshold pass | J4 |
| Expanded non-slow | `uv run pytest tests/ -q -m "not slow" --ignore=tests/benchmarks --timeout=120` | API, contract, property, unit, and integration surfaces pass | J4 |
| Build | `uv build` twice in validated disposable source copies | Wheel is byte-reproducible; normalized wheel/sdist contents, metadata, entry points, and package membership are equivalent; archive-only differences are recorded | J6 |
| Isolated install | Install the candidate wheel into a disposable uv environment, then run import, CLI, migration-discovery, and API health smokes | Artifact behavior matches source-tree contract | J6 |
| API runtime smoke | `uv run uvicorn proxywhirl.api:app --host 127.0.0.1 --port <free-port>` with a temporary `PROXYWHIRL_STORAGE_PATH`; probe `/api/health` and `/api/ready` | Readiness is 200/ready, empty-pool health is the documented 503/unhealthy, and shutdown is clean | C8, J6 |
| Python dependency audit | `uv export --frozen --all-extras --all-groups --no-hashes --no-emit-project --output-file audit-requirements.txt`, then `uvx --from pip-audit==2.10.1 pip-audit --requirement audit-requirements.txt --no-deps --disable-pip --strict --format markdown` | Exact locked closure has no blocking vulnerability and no skipped collection | F6, J7, J9 |
| Bandit | `uvx --from bandit==1.9.4 bandit -r proxywhirl/ -ll --format json` | No unwaived medium-or-higher finding | F6, J7 |
| Safety blocker | Export the same frozen closure, then run pinned `safety==3.8.1 check --file audit-requirements.txt --output json`; retain normalized JSON | Known 11 findings across five packages are absent or explicitly time-bounded and approved | F6, J7-J9 |
| Web dependency audit | `pnpm --dir web audit --audit-level=moderate` | No blocking moderate-or-higher finding | F6, J7 |
| Docs generation | `pnpm --dir web run docs:generate` twice | Both succeed; second run has no generated diff | Shared docs, J5 |
| Web lint | `pnpm --dir web run lint` | Exit 0 without actionable warnings | J5 |
| Web tests | `pnpm --dir web run test:run` | Exit 0 | J5 |
| Web build | `pnpm --dir web run build` | Static/build output succeeds without actionable warnings | J5 |
| Web E2E | `pnpm --dir web run test:e2e:ci` when browser dependencies are available | Rendered docs behavior, navigation, and affected accessibility paths pass | J5 |
| Source gate | `uv run proxywhirl sources --validate --fail-on-unhealthy --timeout 5 --concurrency 5` | Every enabled source is healthy; external failures are diagnosed, not bypassed | J8-J9 |
| Workflow syntax/policy | Parse retained workflows plus repository workflow lint/security policy tools | Valid YAML/actions, pinned intended actions, canonical commands, permissions, timeouts, concurrency, artifacts | Shared workflows, J7 |
| Container build/config | Build container in a disposable context; render both Compose files | Same entry point/settings; non-root, health checks, auth, storage, and secret references valid | Shared manifests, J7 |
| Helm/Kubernetes | Render chart/manifests for one replica and run schema/policy checks | Valid one-replica resources; probes/RBAC/secrets/storage agree; no live secret or multi-replica claim | Shared manifests, J7 |
| Generated artifact exclusion | Enumerate Git diff, distribution contents, and container context | No `.terraform/`, provider binary, environment, credential, database, cache, report, or build artifact | Every barrier, J7 |
| Remote CI | GitHub `CI` run on exact candidate SHA | Required jobs green; logs free of unwaived actionable markers | J8-J9 |
| Remote security | GitHub `Security Scan` run on exact candidate SHA | Required jobs green; known Safety findings cleared; logs reviewed | J8-J9 |
| Remote sources | Manually dispatched `Validate Proxy Sources` on exact candidate SHA | Green and strict source command confirmed | J8-J9 |
| RC acceptance | Evidence ledger for `0.4.0rc1` | All J1-J8 gates complete on candidate SHA; explicit authority required before release mutation | J9 |
| Stable promotion | Repeat drift-prone build, security, source, generated, and remote gates on final SHA | No unresolved regression or evidence/SHA mismatch; explicit authority required before publication/deploy | J9 |

## Remote Blocker Record

The known failure is Security Scan `31285534474` at
`3a2222c47b589f36ce245fecd6f4dad9bc5f9147`, Safety job `93173499813`, step
`Run Safety check`: cryptography 47.0.0 (1), joserfc 1.6.4 (2),
pydantic-settings 2.14.0 (1), pyjwt 2.12.1 (5), and soupsieve 2.8.3 (2).
This matrix is not satisfied by making the job advisory, skipping it, or citing
another SHA. Fresh exact-lock scans determine the actual compatible remediation.

## Stop Rules

1. Stop a wave when its dependency barrier, ownership lock, compatibility
   contract, or security prerequisite is not satisfied.
2. Stop release assurance on any nonzero required command, unexpected contract
   diff, extra Alembic head, generated second-run drift, unresolved
   program-blocking advisory, or actionable warning/error marker.
3. Do not broaden a failing leaf into unrelated cleanup; return it to its owner
   with exact evidence.
4. Do not execute push, dispatch, tag, publish, release, or deploy operations
   without separate explicit authority.
