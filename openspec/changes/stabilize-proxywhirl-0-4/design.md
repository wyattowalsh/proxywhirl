## Context

This umbrella change governs the **ProxyWhirl 0.4 Stabilization and SOTA
Hardening Program**. It reconciles three different evidence layers:

1. The current program authority targets `0.4.0rc1` and then `0.4.0`, preserves
   the `0.3.3` public contract through compatibility facades and explicit
   deprecations, and uses B0-B6, F1-F8, C1-C12, shared single-writer,
   modernization, and J1-J9 assurance waves.
2. `goals/codebase-sota-improvement/` records the earlier W0-W7 audit and
   remediation. Its July closeout (`4242 passed`, 90.23% coverage, zero ty
   errors) is valuable evidence, but its own ledger defers package/god-module,
   FastMCP, CLI coverage, and production-auth concerns.
3. The live local checkout is a later, distinct worktree rooted at
   `040fa6a001097bf21828687439a3ba206066a08c`: 310 collapsed status records
   (201 modified, 16 deleted, 93 untracked) and 327 expanded paths (110
   untracked files). The verified live `main` revision is
   `cba6e74875fba8181d70c33c843c4a55232a732a`, which has only Vercel status and
   no GitHub Actions runs. Neither state inherits release proof from July.

The dirty work spans package facades and splits, request lifecycle, storage and
migrations, REST/CLI/MCP security, dependencies, workflows, deployment assets,
web UI, OpenAPI, and generated docs. It also includes local-only artifacts that
must never be integrated, notably Terraform provider/cache content. All work
must preserve user changes and avoid secret-adjacent files.

The current remote security stop is scheduled Security Scan run `31285534474`
at SHA `3a2222c47b589f36ce245fecd6f4dad9bc5f9147`, Safety job `93173499813`, step
`Run Safety check`: 11 vulnerabilities across five packages (cryptography
47.0.0: 1; joserfc 1.6.4: 2; pydantic-settings 2.14.0: 1; pyjwt 2.12.1: 5;
soupsieve 2.8.3: 2). The program treats these findings as release-blocking even
if a workflow implementation labels a scanner advisory.

## Goals / Non-Goals

**Goals:**

- Convert the current dirty tree into a coherent, reviewable `0.4.0rc1`
  candidate without resetting or losing user work.
- Preserve `0.3.3` public and persisted contracts throughout `0.4.x`, with
  contract tests, facades, deprecation warnings, and migration guidance.
- Prove packaging, migration, lifecycle, storage, security, deployment,
  workflow, documentation, and release invariants on exact candidate SHAs.
- Clear the current dependency-security blocker and prevent stale or
  different-SHA evidence from satisfying release gates.
- Maximize safe parallelism through bounded leaves, explicit dependencies, and
  exclusive ownership of every shared or generated surface.
- Promote `0.4.0rc1` to `0.4.0` only after candidate acceptance and a repeated
  final assurance pass.

**Non-Goals:**

- New products, premium-provider features, or unrelated capability expansion.
- A `0.5` breaking redesign or removal of `0.3.3` compatibility paths.
- Multi-replica storage claims, distributed consensus, or production rollout.
- Implementing OAuth 2.1 merely because ADR 007 proposes it; remote MCP OAuth
  remains a separately accepted epic unless required to close a demonstrated
  `0.4` security blocker without breaking compatibility.
- Force pushes, history rewrites, destructive worktree cleanup, hand edits to
  lockfiles/generated outputs, secret access, or external mutation without
  separate authority.

## Decisions

### D1. Treat the current worktree as data, not disposable state

The B waves first capture exact path, status, ownership, and intent. No agent
may reset, stash, bulk-delete, or replace the worktree to obtain a clean base.
The 310/327 counts are a reconciliation baseline, not a target count; every
change in count must be attributable to an owned leaf.

**Alternative considered:** rebase or recreate the changes from live `main`.
Rejected because it risks losing user-owned work and makes attribution of 327
paths less reliable.

### D2. Preserve contracts through canonical facades, not dual implementations

Package splits (`models`, `strategies`, `fetchers`, CLI, and later modularized
surfaces) retain stable imports and entry points through thin facades. Facades
may adapt signatures or emit deprecations, but all runtime state and registries
belong to one implementation. Installed-wheel tests are authoritative because
source-tree imports can hide missing package data.

**Alternative considered:** remove old paths in `0.4` and rely on release
notes. Rejected by the explicit `0.3.3` compatibility requirement.

### D3. Re-key the historical W0-W7 ledger into the current program graph

Historical results are inputs, not completed tasks. The mapping is:

| Current program | Historical evidence reused for planning | Re-proof rule |
| --- | --- | --- |
| B0-B6 control plane | W0 inventory/stabilization and goal facts | Re-run against 310/327 baseline |
| F1-F8 foundations | W1 types/gates plus W4 deferred architecture | Reconcile current files and installed artifact |
| C1-C12 behavior | W2 security, W3 correctness, W5 concurrency | Re-run focused and cross-interface contracts |
| Shared writers | W6 public/docs plus CI/deploy surfaces | One writer after source contracts stabilize |
| Modernization | Deferred god modules/FastMCP/perf work | Only compatibility-preserving, evidence-driven work |
| J1-J9 assurance | W7 closeout | Entirely rerun on exact candidate SHA |

### D4. Use barriers and a strict single-writer registry

Leaves with disjoint paths may run in parallel. The following remain serial:

| Lock | Required sequence |
| --- | --- |
| Public facades and exports | package internals → compatibility tests → facade writer |
| `pyproject.toml` and `uv.lock` | dependency evidence → manifest writer → lock refresh → security audit |
| Alembic versions/head | model/storage contract → migration writer → installed-wheel migration tests |
| Configuration defaults | runtime/API/CLI/MCP decisions → configuration SSOT writer → manifest/docs consumers |
| `.github/workflows/**` | canonical commands stable → workflow writer → workflow/static validation |
| Release metadata | all version/compat decisions stable → release writer |
| Docker/Compose/Helm/Kubernetes | runtime/config/auth stable → manifest writer(s), serialized on shared semantics |
| OpenAPI/generated docs/public assets | source interfaces stable → generator writer → drift check |

A failed leaf retains its ownership lock until it passes or records a scoped
defer. Dependent panels do not start on partial success.

### D5. Make dependency remediation evidence-driven and single-writer

F6 owns the five-package security investigation. It must refresh advisory
evidence, determine fixed compatible versions and transitive constraints, and
prefer non-breaking upgrades. The manifest/lock writer applies the smallest
coherent resolution; all scanners and affected tests rerun. No version is
guessed from the old report, and no advisory is hidden by changing workflow
failure semantics.

**Alternative considered:** make Safety non-blocking and rely only on another
scanner. Rejected because the current program explicitly treats the known 11
findings as a release stop.

### D6. Separate behavior convergence from architecture modernization

F and C waves establish correct, compatible behavior before optional internal
splits. Modernization may reduce god modules or evaluate FastMCP 4 only when
focused contracts are green, the write set is isolated, and the change does
not jeopardize the release train. Deferral with evidence is preferable to an
unbounded rewrite.

### D7. Use one request-lifecycle state machine across adapters

Rotators and orchestration own logical request outcomes; retry, circuit
breaker, health, metrics, and storage consume those outcomes without applying
the same terminal effect twice. Sync and async adapters share behavior and
differ only in resource/lifecycle mechanics. Cancellation is a first-class
terminal path and resource closure is idempotent.

### D8. Put security checks at module boundaries

Authentication is checked before mutation, SSRF policy is reapplied at DNS and
redirect boundaries, stream limits apply before accumulation, and redaction is
the final boundary before any public/log/model-visible output. CLI and MCP
secrets use non-schema, non-echoing channels and are never silently persisted.

### D9. Limit deployment assurance to one replica

Docker, Compose, Helm, and Kubernetes must agree on entry point, auth, probes,
storage, and secret references for a single replica. The program removes or
labels incomplete examples rather than claiming unsupported PostgreSQL/Redis
subcharts or multi-replica database semantics.

### D10. Treat generators as compilers

Source Python/API/CLI/strategy contracts and source MDX are edited first.
Generated OpenAPI, reference MDX/JSON, `llms.txt`, and public mirrors have one
writer and are produced only through declared scripts. A second identical
generation must be diff-clean.

### D11. Use a two-stage, exact-SHA release train

`0.4.0rc1` is the first complete integration point. It requires local J gates
and remote CI, Security Scan, and Validate Proxy Sources on the same SHA.
Promotion to `0.4.0` requires an acceptance interval plus repeat of every
drift-prone gate. Any code, dependency, manifest, workflow, release, or
generated change after rc1 invalidates the relevant evidence.

## Risks / Trade-offs

- **[Dirty-tree attribution error]** A generated or concurrent writer can alter
  counts while integration is underway. **Mitigation:** snapshot before every
  panel and record added/removed paths by owner at each barrier.
- **[Compatibility facade becomes permanent debt]** Preserving `0.3.3` paths
  costs maintenance. **Mitigation:** one canonical implementation, targeted
  warnings, removal scheduled only for a future major.
- **[Lockfile remediation causes broad drift]** Security fixes can update many
  transitive packages. **Mitigation:** research first, one writer, inspect the
  lock diff, and rerun package/runtime/security matrices.
- **[Migration damages persisted data]** A normalized schema change can pass on
  empty databases but fail on real shapes. **Mitigation:** sanitized `0.3.3`
  fixtures, backup/rollback rehearsal, one Alembic head, and no production
  migration in this program.
- **[Parallel writer collision]** Package facades, storage, config, workflows,
  and generators are broad choke points. **Mitigation:** explicit locks and
  serial queues; the orchestrator integrates status, not overlapping edits.
- **[Remote evidence mismatch]** A green workflow on another SHA can be
  mistaken for candidate proof. **Mitigation:** J evidence records SHA, run,
  job, command, conclusion, and marker review.
- **[External source volatility]** Strict source validation can fail unrelated
  to code. **Mitigation:** diagnose each source and record external status;
  never weaken the strict gate or mislabel an external block as code success.
- **[Modernization overruns release]** God-module or FastMCP work can expand.
  **Mitigation:** bounded modernization leaves with stop rules and explicit
  deferral; compatibility and release assurance outrank refactor completion.

## Migration Plan

1. **Control plane:** capture the exact 310/327 baseline, current revision
   split, applicable instructions, path ownership, compatibility inventory,
   security evidence, and writer locks.
2. **Foundations:** converge packages/facades, configuration, migrations,
   storage primitives, quality harness, dependency security, resource
   factories, and generation prerequisites.
3. **Behavior:** execute C1-C12 behind focused tests, preserving compatibility
   and recording every intentional semantic change.
4. **Shared surfaces:** serialize manifest/lock, workflow, release,
   Docker/Compose, Helm/Kubernetes, OpenAPI/docs, and public-asset writers after
   their inputs stabilize.
5. **Modernization:** perform only bounded, contract-preserving improvements
   whose dependencies and stop rules are satisfied.
6. **Candidate assurance:** run J1-J9 locally and, only with separate authority,
   on the exact `0.4.0rc1` remote SHA. Retain artifacts and marker review.
7. **Stable promotion:** after candidate acceptance, rerun drift-prone gates on
   the exact `0.4.0` tree. Publication/deployment remains separately
   authorized.

Rollback is version-control and artifact based. Before any separately
authorized live migration, preserve a recoverable database backup and prove
downgrade/restore on a disposable copy. No rollback action is executed by this
planning change.

## Resolved Implementation Decisions

- The compatible lock resolution raises the affected dependency floors and
  resolves the candidate to fixed versions; exact frozen pip-audit, Safety,
  Bandit, and behavioral gates report no blocking finding.
- FastMCP remains at compatible `3.4.7` for `0.4.0rc1`. A FastMCP 4 major
  migration is explicitly deferred to a separate post-`0.4.0` OpenSpec change;
  this candidate contains no partial dual-version adapter.
- The `0.3.3` Python, CLI, REST, MCP, configuration, and persistence inventories
  are recorded in `requirements-trace.md` and executable contract tests. The
  top-level 117-export set/order, CLI command/option set, REST operation paths,
  MCP actions/resources, existing config defaults, four SQLModel tables, and
  40 persisted `Proxy` fields remain stable.
- Compatibility defects found during final differential review were returned
  to implementation: `ProxyValidator` retains its released positional order,
  safe-regex returns native matches with one-second defaults,
  `SQLiteStorage.load()` retains its dictionary-row contract, cleanup retains
  its released default, and metrics hour windows retain their accepted result
  shapes. Additive model hydration uses `SQLiteStorage.load_models()`.
- Two security-intentional behavior changes are documented for candidate
  acceptance: unauthenticated non-loopback API startup fails closed, and new
  credential-bearing storage writes require encryption. Existing plaintext
  rows remain readable for migration; users may configure the canonical Fernet
  key or omit credentials. On 2026-08-13 the maintainer explicitly approved
  both exceptions for `0.4.0rc1` release validation, accepting their documented
  startup/write failures and migration paths. This approval does not authorize
  staging, commit, push, tag, publication, deployment, or stable promotion.
- The release workflow creates or verifies and pushes the immutable source tag
  before invoking the irreversible PyPI trusted-publishing step, then creates
  the GitHub Release. Every mutation still requires separate release authority.
- Repeated wheels are byte-identical. Repeated source distributions have the
  same 166 normalized payloads, modes, owners, and entry types, but setuptools
  stamps 24 generated tar members with build-time mtimes even when
  `SOURCE_DATE_EPOCH` is fixed. This normalized-content equivalence satisfies
  the candidate package comparison; byte-identical sdist output is an explicit
  residual, not a claim.

## Open Questions

- What acceptance interval and user validation are required between
  `0.4.0rc1` and `0.4.0`?
- Which remote workflow dispatch/push/tag/publication steps will receive
  explicit authority after local assurance is complete?
