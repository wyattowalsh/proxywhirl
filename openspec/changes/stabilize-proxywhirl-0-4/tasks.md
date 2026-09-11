# Hyperfine Task DAG

Every checkbox is a bounded leaf with an observable completion condition.
Leaves may run in parallel only when their dependencies are satisfied and their
write sets do not overlap. A failed leaf retains its lock. No task below grants
authority to commit, push, dispatch workflows, tag, publish, release, archive,
or deploy.

## 1. B0-B6 Control Plane

- [x] 1.1 **B0.1 — Freeze local identity.** Record branch, HEAD `040fa6a001097bf21828687439a3ba206066a08c`, index state, and timestamp before any program writer starts; verify the record is immutable evidence rather than a cleanup target.
- [x] 1.2 **B0.2 — Reproduce the collapsed baseline.** Record all 310 `git status --short` entries and totals (201 modified, 16 deleted, 93 untracked); stop if the count changed without an attributable writer.
- [x] 1.3 **B0.3 — Reproduce the expanded baseline.** Record all 327 `--untracked-files=all` paths and totals (201 modified, 16 deleted, 110 untracked files); hash the names-only inventory without opening secret-adjacent paths.
- [x] 1.4 **B1.1 — Load applicable instructions.** Map root and nested `AGENTS.md` files to every dirty path and record the strictest applicable constraints for each shard.
- [x] 1.5 **B1.2 — Classify protected paths.** Mark `.env*`, key, credential, secret, backup, local database, cache, report, `.terraform/`, `.venv/`, build, and generated paths as protected, local-only, or generator-owned before assignment.
- [x] 1.6 **B1.3 — Build the path disposition ledger.** Assign every one of the 327 expanded paths exactly one disposition: preserve as user work, integrate in a named leaf, regenerate through an owner, intentionally delete with evidence, or exclude as local-only.
- [x] 1.7 **B2.1 — Reconcile revision authorities.** Record local HEAD, any local remote-tracking ref, verified live `main` `9451abc3fb9f48d99b3eabf6b1d7e177644094d1`, and their path deltas; forbid different-SHA evidence from satisfying candidate gates.
- [x] 1.8 **B2.2 — Reconcile historical ledger.** Map each W0-W7 result and deferral from `goals/codebase-sota-improvement/` to a current B/F/C/shared/modernization/J leaf, marking every old test result historical until rerun.
- [x] 1.9 **B2.3 — Capture remote blocker evidence.** Preserve run `31285534474`, SHA `3a2222c47b589f36ce245fecd6f4dad9bc5f9147`, Safety job `93173499813`, exact step, and the 11-finding/five-package breakdown in the program evidence ledger.
- [x] 1.10 **B3.1 — Validate umbrella artifacts.** Run `openspec validate stabilize-proxywhirl-0-4 --json`; require `valid: true` and zero issues before implementation leaves use this change.
- [x] 1.11 **B3.2 — Trace specs to surfaces.** Map every requirement in the five capability specs to at least one owner leaf and one validation-matrix row; reject orphan requirements and orphan implementation leaves.
- [x] 1.12 **B3.3 — Freeze scope boundaries.** Record `0.4.0rc1 → 0.4.0`, `0.3.3` compatibility, single-replica deployment assurance, and explicit non-goals; route scope-expanding choices to a separate approved change.
- [x] 1.13 **B4.1 — Inventory the 0.3.3 Python contract.** Capture documented top-level exports, surviving module imports, call signatures, enum values, model serialization, and error families from source, docs, and an isolated `0.3.3` artifact where available.
- [x] 1.14 **B4.2 — Inventory interface contracts.** Capture `0.3.3` CLI help/options, REST paths/OpenAPI, MCP tools/resources, configuration keys/defaults, examples, and supported export/import formats.
- [x] 1.15 **B4.3 — Inventory persisted contracts.** Build sanitized representative `0.3.3` SQLite/file fixtures and record schema, fields, migrations, encryption expectations, and round-trip behavior without copying live user data.
- [x] 1.16 **B5.1 — Publish exclusive writer locks.** Assign one owner and queue order for facades/exports, `pyproject.toml`+`uv.lock`, Alembic, configuration, storage, API, MCP, workflows, release metadata, manifests, generators, snapshots, and proxy assets.
- [x] 1.17 **B5.2 — Publish dependency barriers.** Materialize the B→F→C→shared→modernization→J DAG, including the package-before-facade, behavior-before-generator, and candidate-before-remote-proof edges.
- [x] 1.18 **B5.3 — Publish leaf reporting contract.** Require each writer to report exact files, before/after status counts, commands and exit codes, result counts, warnings, residual risks, and whether its lock is released.
- [x] 1.19 **B6.1 — Run read-only baseline probes.** Execute import/CLI-help/OpenSpec/status and narrowly scoped static probes that do not mutate generated, lock, database, or secret surfaces; record current failures without repairing them.
- [x] 1.20 **B6.2 — Run focused baseline gates.** Run the smallest applicable lint/type/test probes for each future shard with no auto-fix; attribute each failure to one F/C owner.
- [x] 1.21 **B6.3 — Open implementation barrier.** Start F leaves only when all paths are classified, protected paths are excluded, writer locks are assigned, and no untracked concurrent writer remains.

## 2. F1-F8 Foundational Convergence

- [x] 2.1 **F1.1 — Inventory dual package layouts.** Compare legacy monoliths and new `models/`, `strategies/`, `fetchers/`, and `cli/` packages; identify canonical implementations, facade-only paths, missing package files, and duplicated state.
- [x] 2.2 **F1.2 — Converge models and strategies packages.** Finish canonical package layouts with one registry/state implementation while preserving `0.3.3` imports and serialization; verify focused model/strategy and compatibility tests.
- [x] 2.3 **F1.3 — Converge fetchers and CLI packages.** Finish canonical internal packages and thin entry facades without changing the documented command/parser/fetcher surface; verify import and CLI focused tests.
- [x] 2.4 **F1.4 — Integrate public exports.** After package internals are stable, update the single public-facade writer and verify lazy/eager import parity, `__all__`, entry points, deprecation warnings, and isolated-wheel imports.
- [x] 2.5 **F2.1 — Build the configuration graph.** Compare `config_core.py`, `config.py`, `settings.py`, API, CLI, MCP, Docker, Compose, Helm, environment docs, and defaults; record every duplicate or contradiction.
- [x] 2.6 **F2.2 — Select configuration SSOT.** Define canonical names, types, defaults, precedence, secret channels, production requirements, and adapter-only fields while retaining accepted `0.3.3` keys.
- [x] 2.7 **F2.3 — Implement adapter convergence.** Route API/CLI/MCP/runtime adapters through the SSOT without circular imports or silent aliasing; emit explicit deprecations for retained old keys.
- [x] 2.8 **F2.4 — Prove configuration parity.** Run `test_config_ssot`, CLI config, API config, MCP config, environment precedence, and manifest/docs comparison tests.
- [x] 2.9 **F3.1 — Audit schema and migration topology.** Compare SQLModel metadata, runtime initialization, Alembic configuration/versions, package data, and empty versus representative `0.3.3` databases; require one planned head.
- [x] 2.10 **F3.2 — Author the migration with one writer.** Implement the minimum data-preserving upgrade to the normalized `0.4` schema without runtime DDL competing with Alembic.
- [x] 2.11 **F3.3 — Test forward migration.** Upgrade disposable empty and sanitized `0.3.3` SQLite fixtures to head and verify record counts, proxy identity, health state, nullable fields, indexes, and non-secret configuration.
- [x] 2.12 **F3.4 — Prove packaged migration discovery.** Build/install the candidate artifact in isolation, run `alembic heads` and `upgrade head`, and require exactly one discoverable head.
- [x] 2.13 **F4.1 — Define backend parity corpus.** Specify equivalent file/SQLite create, load, update, remove, clear, invalid-row, partial-credential, filtering, and ordering cases.
- [x] 2.14 **F4.2 — Stabilize SQLite semantics.** Fix construction, transaction, locking, error translation, nullable comparisons, and migration integration; verify SQLite and concurrency tests.
- [x] 2.15 **F4.3 — Stabilize file semantics.** Fix atomic save/load/replace, malformed input, permissions/error translation, and credential handling; verify file-storage tests.
- [x] 2.16 **F4.4 — Run backend differential tests.** Execute the parity corpus against both backends and stop on any unexplained normalized result or public-error divergence.
- [x] 2.17 **F5.1 — Reconcile canonical commands.** Verify every `justfile`, CI, AGENTS, and validation-matrix command maps to a live path and uses `uv run` or the approved wrapper.
- [x] 2.18 **F5.2 — Repair harness path drift.** Remove stale references to deleted/moved tests and modules; do not add legacy code shims solely to satisfy a hook.
- [x] 2.19 **F5.3 — Reconcile lint/type/coverage policy.** Restore zero-error Ruff/ty gates, eliminate unjustified ignores, narrow coverage omissions, and ensure contract/API/CLI suites participate in the intended tier.
- [x] 2.20 **F5.4 — Prove the foundation harness.** Run `just lint`, `just format-check`, `just type-check`, and focused harness tests; record exact warnings and release the gate-config lock.
- [x] 2.21 **F6.1 — Reproduce dependency findings.** Export and scan the exact locked environment, confirming which of the 11 known Safety findings and any pip-audit/web findings remain reachable on the current tree.
- [x] 2.22 **F6.2 — Research compatible remediations.** For cryptography, joserfc, pydantic-settings, pyjwt, and soupsieve, identify fixed versions, transitive constraints, Python-floor impact, upstream changelogs, and runtime/test risks; do not guess from stale output.
- [x] 2.23 **F6.3 — Apply one manifest/lock resolution.** With explicit dependency-change authority and the shared lock, update declarations and regenerate `uv.lock` through `uv`; inspect every transitive change and never hand-edit the lock.
- [ ] 2.24 **F6.4 — Prove security and behavior after resolution.** Run locked sync, affected unit/integration tests, pip-audit, Bandit, Safety-equivalent evidence, web audit, build, and isolated-install smoke; require the five-package blocker to clear or stop for an approved exception.
- [x] 2.25 **F7.1 — Inventory resource ownership.** Map every sync/async httpx client, browser, stream, task, thread, lock, queue, and database connection to its creator, reuser, and closer.
- [x] 2.26 **F7.2 — Converge client factories.** Implement long-lived bounded client reuse with explicit timeout/limit/transport configuration while preserving dependency injection and mocks.
- [x] 2.27 **F7.3 — Harden shutdown and cancellation.** Make normal, exceptional, cancelled, and repeated close paths idempotent and settle active counters/tasks/threads.
- [x] 2.28 **F7.4 — Prove no resource leaks.** Run validator-pool, async teardown, cancellation, race, and repeated-lifespan tests with bounded timeouts.
- [x] 2.29 **F8.1 — Inventory generator inputs and outputs.** Map Python/API/CLI/strategy/source inputs to OpenAPI, generated MDX/JSON, navigation, `llms.txt`, and proxy public mirrors.
- [x] 2.30 **F8.2 — Stabilize web toolchain inputs.** Reconcile `web/package.json`, workspace/lock policy, generation scripts, path escaping, and retry-and-failover naming without running generators prematurely.
- [x] 2.31 **F8.3 — Add determinism assertions.** Make generation fail on duplicate paths, stale removed pages, invalid navigation, credential-bearing output, or a non-clean immediate second run.
- [x] 2.32 **F8.4 — Open behavior barrier.** Begin C leaves only after F public/config/storage/security/resource prerequisites relevant to each leaf are green; record explicitly deferred F work.

## 3. C1-C12 Behavioral Hardening

- [x] 3.1 **C1.1 — Define logical request outcomes.** Specify selection, attempt, retry, failover, cancellation, success, and terminal-failure events plus their sole state owners.
- [x] 3.2 **C1.2 — Remove duplicate terminal effects.** Ensure health, proxy counters, circuit state, metrics, active requests, and persistence consume one terminal result exactly once.
- [x] 3.3 **C1.3 — Prove lifecycle invariants.** Add deterministic success, retry-exhaustion, failover, cancellation, and exception regressions with exact counter/state assertions.
- [x] 3.4 **C2.1 — Stabilize sync rotator semantics.** Verify empty/bootstrap behavior, health filtering, selection context, session handling, request queues, and result recording against `0.3.3` contracts.
- [x] 3.5 **C2.2 — Stabilize sync resource lifecycle.** Reuse/close sync clients and clear queues/counters safely on context exit and repeated close.
- [x] 3.6 **C2.3 — Run sync rotator matrix.** Execute focused sync, bootstrap, queue, failure, session, and contract tests with no real network.
- [x] 3.7 **C3.1 — Establish async parity.** Make async selection, bootstrap, retry, failover, session, and terminal results behaviorally equivalent to sync.
- [x] 3.8 **C3.2 — Harden async cancellation/concurrency.** Bound pool/client creation, settle tasks and active counters, and make close idempotent under cancellation and concurrent empty pools.
- [x] 3.9 **C3.3 — Run async parity matrix.** Execute async client/rotator/teardown/concurrency/integration tests and compare deterministic outcomes with C2.
- [x] 3.10 **C4.1 — Stabilize circuit-breaker transitions.** Prove closed/open/half-open eligibility, one probe reservation, reset/cleanup, async parity, and monotonic-time behavior.
- [x] 3.11 **C4.2 — Stabilize retry and rate limiting.** Prove retry budgets, jitter bounds, exception taxonomy, cancellation, token refill, and queue/full behavior without duplicate request accounting.
- [x] 3.12 **C4.3 — Run resilience properties.** Execute circuit/retry/rate unit, async, property, cleanup, and race tests under bounded clocks.
- [x] 3.13 **C5.1 — Stabilize models and proxy-pool invariants.** Prove validation, credentials, identity indexes, thread safety, expiration, deduplication, serialization, and current mutability/frozen contracts.
- [x] 3.14 **C5.2 — Stabilize all nine strategies.** Verify registry completeness, aliases/deprecations, empty-pool errors, selection context, state locks, sessions, geo/cost/composite behavior, and deterministic seeded tests.
- [x] 3.15 **C5.3 — Run model/strategy contracts.** Execute unit, property, integration, import-compatibility, and contract snapshot suites.
- [x] 3.16 **C6.1 — Define tier contracts.** Record L1/L2/L3 sync/async APIs, TTL, eviction, encryption, miss/error semantics, and manager lock ordering.
- [x] 3.17 **C6.2 — Harden stampede and coherence.** Prove single-flight fill, invalidation propagation, eviction, corrupted-entry handling, encryption rotation, and bounded background work.
- [x] 3.18 **C6.3 — Run cache stress properties.** Execute tier, manager, stampede, coherence, eviction, crypto, property, and race tests without external Redis/network dependency.
- [x] 3.19 **C7.1 — Converge source and parser contracts.** Preserve registry shape, formats, disabled-source rationale, bounded streaming parsers, deduplication, and sanitized errors.
- [x] 3.20 **C7.2 — Enforce SSRF and validation boundaries.** Apply target policy before DNS/use and after redirects to source fetching, validators, browsers, health checks, and proxied requests; bound content/time/concurrency.
- [x] 3.21 **C7.3 — Run source/fetch safety matrix.** Execute source, parser, validator pool, browser-mocked, safe-regex, SSRF, size-limit, redirect, and error-redaction tests.
- [x] 3.22 **C8.1 — Freeze REST contract and auth matrix.** Compare routes/OpenAPI/models/status codes with `0.3.3`, classify every route, and preserve public behavior through compatible schemas/deprecations.
- [x] 3.23 **C8.2 — Harden REST boundaries.** Enforce non-loopback auth, mutation-before-side-effect denial, body/stream limits, SSRF, error sanitization, credential redaction, health/readiness, and lifespan cleanup.
- [x] 3.24 **C8.3 — Run REST matrix and runtime smoke.** Execute unit/API/integration/contract tests plus loopback uvicorn health/readiness and authenticated/unauthenticated probes against temporary storage.
- [x] 3.25 **C9.1 — Freeze CLI contract.** Snapshot `0.3.3` commands/options/help/exit codes/config precedence and map current package handlers to one Typer app.
- [x] 3.26 **C9.2 — Harden CLI secrets and state.** Ensure keys/credentials are non-echoing/redacted, locks and temporary config paths are bounded, and import/validate/source operations cannot persist plaintext secrets silently.
- [x] 3.27 **C9.3 — Run CLI regression and smoke matrix.** Exercise help, pool add/list/remove, config set/get, import, proxy validation, strict sources, errors, and credential redaction with temporary paths.
- [x] 3.28 **C10.1 — Freeze MCP contract.** Inventory `0.3.3` tools/actions/resources/transports/results, classify reads/writes/unknown actions, and preserve tool schemas and sanitized result shapes.
- [x] 3.29 **C10.2 — Harden MCP auth and lifecycle.** Keep stdio local semantics explicit, require auth for networked/mutating operations, read keys outside tool schemas, redact every result/error, and close lifespan resources.
- [x] 3.30 **C10.3 — Run MCP matrix.** Execute all write-without-key, unknown-action, key-channel, redaction, transport, cold-start, typed-result, and lifecycle tests; defer OAuth implementation unless separately accepted.
- [x] 3.31 **C11.1 — Stabilize import/export round trips.** Preserve supported formats, field normalization, source metadata, ordering where documented, duplicate behavior, and credential policy across CLI/API/storage.
- [x] 3.32 **C11.2 — Stabilize persistence under lifecycle events.** Prove restart, failure, partial write, migration, concurrent update, cancellation, and recovery behavior for supported backends.
- [x] 3.33 **C11.3 — Run persistence differential matrix.** Compare file/SQLite/import/export behavior and migrations using sanitized `0.3.3` and current fixtures.
- [x] 3.34 **C12.1 — Build cross-interface contract map.** Map Python, CLI, REST, MCP, configuration, persisted, and generated-doc representations for shared concepts and identify every intentional difference.
- [x] 3.35 **C12.2 — Update only intentional snapshots.** Review contract/OpenAPI/CLI/generated diffs against the compatibility spec before a single snapshot writer accepts them; reject incidental churn.
- [x] 3.36 **C12.3 — Close behavioral barrier.** Run public import, package compatibility, API, CLI, MCP, storage, and contract suites together; shared writers may start only when results are green or explicitly deferred with impact.

## 4. Shared Single-Writer Surfaces

- [x] 4.1 **S1.1 — Finalize Python manifest.** After F/C requirements stabilize, one writer reconciles package inclusion, entry points, extras, Python floor, coverage settings, and version metadata in `pyproject.toml`.
- [x] 4.2 **S1.2 — Regenerate and inspect `uv.lock`.** One writer resolves through `uv`, records package/version deltas, and verifies no hand edits or unrelated dependency churn.
- [x] 4.3 **S1.3 — Build and install artifacts.** Produce wheel/sdist in a disposable directory and verify package files, migrations, imports, CLI entry point, metadata, and runtime smokes outside the checkout.
- [x] 4.4 **S2.1 — Inventory workflow authority.** Map CI, security, source, docs, proxy generation, release, and deployment workflows to canonical commands, events, permissions, concurrency, timeouts, and artifacts.
- [x] 4.5 **S2.2 — Reconcile workflows with one writer.** Remove contradictory/duplicate behavior, retain blocking gates, preserve artifact evidence, and do not hide the known security blocker through `continue-on-error` or skipped logic.
- [x] 4.6 **S2.3 — Validate workflow definitions.** Run YAML/action/policy lint, inspect exact command parity, and verify warning/error markers and optional-token behavior without dispatching a workflow.
- [x] 4.7 **S3.1 — Reconcile release metadata.** One writer aligns version source, changelog/release notes, compatibility/deprecation/migration notes, build artifacts, prerelease semantics, and `0.4.0rc1 → 0.4.0` ordering.
- [x] 4.8 **S3.2 — Dry-run release locally.** Build, inspect, and install candidate artifacts and exercise release workflow logic without tag, upload, GitHub release, or deployment mutation.
- [ ] 4.9 **S3.3 — Freeze candidate inputs.** Record candidate SHA/tree, manifest and lock hashes, migration head, generated-output state, and release notes before J gates.
- [x] 4.10 **S4.1 — Reconcile Docker entry point.** Make `Dockerfile`, root Compose, and deploy Compose use the same runtime/config/auth/health/storage contract and non-root filesystem assumptions.
- [x] 4.11 **S4.2 — Render single-replica Compose configs.** Validate environment precedence, required secrets by reference, writable temporary storage, probes, ports, and absence of live secret values.
- [x] 4.12 **S4.3 — Build and smoke container locally.** In a disposable context, start one replica on loopback, probe health/readiness with temporary storage, inspect logs for actionable markers, and stop cleanly.
- [x] 4.13 **S5.1 — Reconcile Helm/Kubernetes templates.** One manifest writer aligns deployment, service, account/RBAC, probes, config, storage, and secret references; remove or label incomplete duplicate examples.
- [x] 4.14 **S5.2 — Render one-replica resources.** Render default and documented override charts/manifests and run schema/policy checks; forbid multi-replica readiness claims.
- [x] 4.15 **S5.3 — Verify manifest parity.** Compare rendered settings with Python/Docker/Compose SSOT and confirm no real secret, local provider cache, or unsupported subchart is required.
- [x] 4.16 **S6.1 — Regenerate OpenAPI and references once.** After C12, run only declared web generation scripts through the canonical command under the single generator writer.
- [x] 4.17 **S6.2 — Review generated diff.** Check path renames, navigation, Python/CLI/strategy/OpenAPI content, examples, redaction, `llms.txt`, and removed-page cleanup against intentional source changes.
- [x] 4.18 **S6.3 — Prove second-run determinism.** Run docs generation again and require no tracked diff before web lint/test/build and any snapshot acceptance.
- [x] 4.19 **S7.1 — Isolate remote proxy-list churn.** Reconcile canonical `docs/proxy-lists/**` and mirrored `web/public/proxy-lists/**` separately from code/docs integration and record the exact generated source.
- [ ] 4.20 **S7.2 — Regenerate only when authorized.** Use the canonical fetch/export workflow, never hand-edit freshness/health/count claims, and preserve external-failure evidence.
- [x] 4.21 **S7.3 — Prove source/mirror parity.** Compare canonical and public assets, metadata/counts/timestamps, source gate results, and generated README wording before release assurance.

## 5. Bounded Modernization

- [x] 5.1 **M1.1 — Re-measure architecture hotspots.** Record current LOC, dependencies, cycles, change frequency, test seams, and compatibility boundaries for CLI, cache, models, storage, MCP, sources, retry/circuit/rate, and configuration.
- [x] 5.2 **M1.2 — Select only release-safe splits.** Approve bounded internal extractions with stable facades and focused green tests; defer any rewrite that changes public behavior or crosses shared locks.
- [ ] 5.3 **M2.1 — Modularize CLI behind one app.** Extract one command family per serial leaf, preserve help/options/exit codes, and rerun CLI tests after every extraction.
- [x] 5.4 **M2.2 — Measure CLI coverage honestly.** Add tests for extracted handlers and narrow coverage omissions only when the measured candidate stays above the configured gate.
- [ ] 5.5 **M3.1 — Modularize cache/storage where seams are proven.** Extract tier/backend internals only after parity/coherence/migration gates and retain package-level public imports.
- [ ] 5.6 **M3.2 — Slim MCP composition without schema drift.** Extract auth/tool/runtime helpers serially while preserving tool/resource schemas, auth policy, redaction, and lifecycle tests.
- [x] 5.7 **M4.1 — Audit FastMCP major compatibility.** Compare installed/locked APIs with current FastMCP 4 auth, lifespan, transport, and structured-tool requirements using official evidence; produce a cost/risk matrix.
- [x] 5.8 **M4.2 — Apply or defer the FastMCP change.** Upgrade only if it is bounded, security-relevant, and `0.3.3` compatible; otherwise record a post-`0.4.0` change with no partial adapter layer.
- [x] 5.9 **M5.1 — Benchmark proven hot paths.** Measure request/client reuse, selection, pool snapshots, parser streaming, cache hit/miss/stampede, and storage operations with repeatable baselines before optimization.
- [x] 5.10 **M5.2 — Keep only verified optimizations.** Accept changes that preserve contracts and show meaningful repeatable gains without resource leaks; revert or defer noise-level changes through normal version control review.

## 6. J1-J9 Assurance and Release Train

- [x] 6.1 **J1.1 — Freeze writers and recount scope.** Confirm every writer is idle, every original expanded path has a disposition, current status deltas are attributable, and protected/local-only artifacts remain excluded.
- [x] 6.2 **J1.2 — Revalidate OpenSpec traceability.** Run `openspec validate stabilize-proxywhirl-0-4 --json` and verify every spec requirement maps to completed tasks and validation evidence.
- [x] 6.3 **J1.3 — Audit compatibility exceptions.** Require approval/evidence/migration notes for any `0.3.3` break; otherwise return the surface to its owner.
- [x] 6.4 **J2.1 — Run formatting and lint.** Execute `just format-check` and `just lint`; require zero errors and review all warnings without auto-fixing shared/generated files.
- [x] 6.5 **J2.2 — Run full type gates.** Execute `just type-check` and `uv run ty check proxywhirl/ tests/`; require zero errors and document every surviving warning.
- [ ] 6.6 **J2.3 — Run static hygiene checks.** Scan for stale paths, unexpected broad ignores, unresolved TODO/incomplete product paths, duplicate package implementations, forbidden generated edits, and credential-shaped output.
- [x] 6.7 **J3.1 — Run compatibility/interface suites.** Execute public-import, Wave 3 package compatibility, CLI, REST, MCP, storage migration/parity, and contract tests from the validation matrix.
- [x] 6.8 **J3.2 — Run runtime/security suites.** Execute rotator, lifecycle, resilience, concurrency, cache, source/fetcher, SSRF, streaming, redaction, auth, and secret-handling focused suites.
- [x] 6.9 **J3.3 — Triage focused failures by owner.** Reopen only the failing leaf and dependents, retain its lock, then rerun the focused gate before advancing.
- [x] 6.10 **J4.1 — Run CI-parity quality gates.** Execute `just quality-gates`; record exact pass/skip/deselect and coverage totals plus exit code.
- [x] 6.11 **J4.2 — Run expanded non-slow suite.** Execute the documented `tests/` non-slow/non-benchmark command and reconcile any coverage/xdist-only divergence.
- [x] 6.12 **J4.3 — Repeat changed focused gates after full-suite fixes.** No full-suite repair is accepted until its owner reruns the original focused suite and the full gate.
- [x] 6.13 **J5.1 — Run deterministic docs generation.** Execute the canonical generator twice and require a clean second run and reviewed generated diff.
- [x] 6.14 **J5.2 — Run web lint/tests/build.** Execute `pnpm --dir web run lint`, `test:run`, and `build`; inspect logs for actionable markers and generated route/link errors.
- [x] 6.15 **J5.3 — Run affected web E2E.** When browser dependencies are installed, run CI E2E for navigation, rendered docs behavior, reduced motion, and affected accessibility surfaces; otherwise record the exact external prerequisite.
- [x] 6.16 **J6.1 — Build wheel and sdist.** Use `uv build` in a disposable output directory, inspect contents/metadata/entry points/migrations, and require no local or secret-adjacent artifact.
- [x] 6.17 **J6.2 — Test isolated installation.** Install the wheel in a disposable uv environment and run imports, CLI help/commands, Alembic discovery/upgrade, API health/readiness, and representative contract smokes.
- [x] 6.18 **J6.3 — Compare source and installed behavior.** Require the installed artifact to match source-tree public exports, version, routes, CLI, MCP registration, data loading, and deprecation behavior.
- [ ] 6.19 **J7.1 — Run dependency/code security gates.** Run locked pip-audit, Bandit, current Safety-equivalent scan, web audit, redaction/secret tests, and inspect all artifacts; known 11 findings must clear or have approved expiring exceptions.
- [x] 6.20 **J7.2 — Validate workflows and release dry-run.** Parse/lint workflows, compare canonical commands, permissions, concurrency, artifacts, and warning policy, then dry-run release logic locally without external mutation.
- [x] 6.21 **J7.3 — Validate deployment artifacts.** Build/smoke one-replica container/Compose and render/check Helm/Kubernetes; require config/auth/probe/storage parity and no live secret or multi-replica claim.
- [ ] 6.22 **J8.1 — Obtain explicit remote-mutation authority.** Before any push or workflow dispatch, confirm exact target/ref/SHA and authorization; otherwise report local-ready state and stop.
- [ ] 6.23 **J8.2 — Run exact-SHA remote assurance.** On the authorized `0.4.0rc1` candidate SHA, require `CI`, `Security Scan`, and manually dispatched `Validate Proxy Sources`; capture run/job IDs, conclusions, commands, artifacts, and log-marker review.
- [ ] 6.24 **J8.3 — Reject stale or partial status.** Do not accept Vercel-only, different-SHA, skipped, cancelled, advisory-hidden, or missing required-job evidence; repair and rerun the owning gate on the candidate SHA.
- [ ] 6.25 **J9.1 — Assemble `0.4.0rc1` ledger.** Record exact SHA/tree, compatibility diff, migration head, dependency set, local and remote gate evidence, residual deferrals, known limitations, and rollback instructions.
- [ ] 6.26 **J9.2 — Hold candidate acceptance.** Obtain explicit release authority and complete the chosen acceptance interval/user validation; any candidate change invalidates affected and drift-prone evidence.
- [ ] 6.27 **J9.3 — Re-prove and promote `0.4.0`.** On the final exact tree, repeat security, sources, build/install, generated drift, and remote CI gates; publish/tag/release only with separate explicit authority and never deploy as an implied follow-on.
