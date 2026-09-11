# Requirement Trace and Cross-Interface Map

This map binds every capability requirement to its owning task leaves and to
named rows in `validation-matrix.md`. A mapping identifies responsibility and
proof; it does not mark a task complete or substitute historical evidence for
the final candidate-tree run.

## Capability-to-task trace

| Capability requirement | Owning leaves | Validation rows |
| --- | --- | --- |
| Public contract: `0.3.3` is the compatibility baseline | 1.13-1.15, 3.22, 3.25, 3.28, 6.3 | Public imports; Contract snapshots; CLI focused/smoke; REST focused; MCP focused; Storage parity |
| Public contract: compatibility facades have one implementation | 2.1-2.4, 3.35-3.36 | Public imports; Contract snapshots; Isolated install |
| Public contract: deprecations are explicit and testable | 2.4, 3.22, 3.25, 3.28, 6.3 | Public imports; Contract snapshots; CLI/REST/MCP focused |
| Public contract: installed distributions match source behavior | 2.12, 4.1-4.3, 6.16-6.18 | Build; Isolated install; Alembic topology; Generated artifact exclusion |
| Public contract: persisted `0.3.3` data remains readable | 1.15, 2.9-2.16, 3.31-3.33 | Storage parity; Alembic topology; Isolated install |
| Public contract: breaking exceptions require a recorded gate | 1.12-1.15, 3.22, 3.25, 3.28, 6.3 | Contract snapshots; RC acceptance; Stable promotion |
| Runtime: request lifecycle effects occur exactly once | 3.1-3.3 | Request lifecycle; Fast test tier; Full Python gate |
| Runtime: sync and async rotators have semantic parity | 3.4-3.9 | Request lifecycle; Fast test tier; Full Python gate |
| Runtime: resources have bounded ownership | 2.25-2.28, 3.5, 3.8 | Request lifecycle; Sources/fetchers; Cache/concurrency |
| Runtime: storage backends provide contract parity | 2.13-2.16, 3.31-3.33 | Storage parity; Alembic topology |
| Runtime: schema migration has one authoritative head | 2.9-2.12, 4.3, 6.16-6.18 | Alembic topology; Build; Isolated install |
| Runtime: concurrent state remains coherent | 3.1-3.18, 3.31-3.33 | Request lifecycle; Cache/concurrency; Storage parity |
| Runtime: untrusted operations fail within bounds | 3.11, 3.17-3.21, 3.23, 3.26, 3.29 | Sources/fetchers; REST focused; MCP focused; Runtime/security suites |
| Interface security: non-loopback services require authentication | 3.22-3.24, 3.28-3.30 | REST focused; MCP focused; API runtime smoke |
| Interface security: authentication covers the complete matrix | 3.22-3.24, 3.28-3.30 | REST focused; MCP focused; Contract snapshots |
| Interface security: network targets pass SSRF policy at every hop | 3.19-3.24 | Sources/fetchers; REST focused; Runtime/security suites |
| Interface security: streaming/parsing are bounded before accumulation | 3.19-3.24 | Sources/fetchers; REST focused; Runtime/security suites |
| Interface security: credentials never cross output boundaries | 3.19-3.30, 3.31 | CLI smoke; REST focused; MCP focused; Generated artifact exclusion |
| Interface security: CLI/MCP secrets are non-echoing and non-persistent | 3.25-3.30 | CLI focused/smoke; MCP focused |
| Interface security: no unresolved blocking dependency advisory | 2.21-2.24, 6.19, 6.23 | Python dependency audit; Bandit; Safety blocker; Web dependency audit; Remote security |
| Delivery: configuration has one source of truth | 2.5-2.8, 4.10-4.15 | Contract snapshots; Container build/config; Helm/Kubernetes |
| Delivery: package metadata and lock state are reproducible | 2.17-2.24, 4.1-4.3 | Build; Isolated install; Python dependency audit |
| Delivery: deployments are complete and single-replica safe | 4.10-4.15, 6.21 | Container build/config; Helm/Kubernetes; Generated artifact exclusion |
| Delivery: workflows invoke canonical project gates | 2.17-2.20, 4.4-4.6, 6.20 | Workflow syntax/policy; Full Python gate; Docs/Web gates |
| Delivery: generated documentation is script-owned/deterministic | 2.29-2.31, 4.16-4.18, 6.13-6.15 | Docs generation; Web lint/tests/build/E2E |
| Delivery: public proxy assets preserve source/mirror parity | 4.19-4.21 | Source gate; Generated artifact exclusion |
| Delivery: local and secret-adjacent artifacts are excluded | 1.5-1.6, 4.3, 6.1, 6.16 | Scope/secret inventory; Generated artifact exclusion; Build |
| Release: evidence is bound to an exact baseline | 1.1-1.10, 6.1-6.2 | Baseline collapsed/expanded; Revision split; OpenSpec |
| Release: candidate passes the complete local matrix | 6.4-6.21 | Lint through Helm/Kubernetes rows |
| Release: known remote security blocker is cleared | 2.21-2.24, 6.19, 6.23 | Safety blocker; Python dependency audit; Remote security |
| Release: remote assurance uses the exact candidate SHA | 1.7, 6.22-6.24 | Revision split; Remote CI/security/sources |
| Release: stable promotion repeats drift-prone gates | 6.25-6.27 | RC acceptance; Stable promotion |
| Release: logs preserve actionable markers | 1.18, 6.10, 6.13-6.21, 6.23 | Full Python/Web/security/workflow/deploy/remote rows |
| Release: change control does not grant release authority | 6.22, 6.25-6.27 | RC acceptance; Stable promotion |

No capability requirement is orphaned, and every implementation leaf belongs
to a control, foundation, behavior, shared-surface, modernization, or assurance
barrier represented above or in `affected-surfaces.md`.

## Cross-interface concept map

| Shared concept | Python/runtime | CLI | REST | MCP | Persisted/config | Generated docs | Intentional difference |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Proxy identity | `Proxy.id`, normalized URL and protocol | Pool/import/export rows | Proxy schemas and `/api/proxies` | Proxy tools/results | UUID plus normalized URL in file/SQLite | Python, CLI, OpenAPI references | CLI CSV exposes a stable four-field status projection, not the full model dump. |
| Credentials | `ProxyCredentials` / secret-aware URL parsing | Non-echoing inputs and redacted output | Auth headers plus redacted request/result models | Metadata/environment key channels; no key in tool schema | Encrypted credential fields and canonical key settings | Examples use placeholders/redacted values | Public proxy-list and export surfaces omit credentials entirely. |
| Health/state | `HealthStatus`, counters, `HealthMonitor` | `health`, pool status/statistics | Health/readiness and proxy health routes | Static health resource and health tools | Rich proxy health fields round-trip | CLI/OpenAPI/Python reference tables | Readiness can be ready while empty-pool health is intentionally unhealthy. |
| Request outcome | Orchestration owns exactly-once settlement | Human-readable failures/exit codes | Sanitized status/error envelope | Sanitized structured tool result | Counters/timestamps persist where supported | Retry/failover and API references | Interface presentation differs; terminal state ownership stays runtime-only. |
| Configuration | `ProxyConfiguration` and settings models | Config get/set/templates | API settings/auth environment | MCP settings/auth environment | TOML plus documented environment precedence | Config reference and deployment prose | Secret values use environment/encrypted stores and are never rendered by config reads. |
| Storage/migration | File models, released SQLite row contract, and additive SQLite model hydration | Import/export/pool workflows | Lifespan `load_models`/persist | MCP lifespan `load_models`/persist | Packaged `_alembic`, sole head `d4e5f6a7b8c9` | Migration and operations guides | `FileStorage.load()` returns models; released `SQLiteStorage.load()` returns 18-key rows; additive `load_models()` provides full-fidelity runtime models. |
| Sources/validation | Source registry, fetchers, parsers, SSRF policy | `sources --validate` | Fetch/validation routes | Source/fetch tools | Source/config metadata | Source, CLI, and API references | Real-network source health is a release gate, while ordinary tests use bounded mocks. |
| Strategies | One registry with canonical classes and aliases | Strategy options/help | Strategy config schemas | Strategy selection fields/tools | Strategy name/config fields | Eight unique classes and registered aliases | Aliases remain compatibility names and do not create duplicate implementations. |

Intentional representation differences are accepted only where named above;
snapshot, package, API, CLI, MCP, storage, and generator tests remain the
executable contract authority.
