# Execution Evidence

This ledger distinguishes the integrated local `0.4.0rc1` source snapshot from
an accepted or published release. The checkout remains rooted at committed HEAD
`040fa6a001097bf21828687439a3ba206066a08c`; all candidate work is unstaged and
unpublished, so that HEAD is an ancestry anchor rather than exact-SHA proof for
the dirty candidate.

## Baseline and orchestration

- Initial collapsed status: 310 records (`201 M`, `16 D`, `93 ??`), nothing staged.
- Initial expanded status: 327 paths (`201 M`, `16 D`, 110 untracked files).
- Final resumed-wave expanded status: 453 paths (`283 M`, `24 D`, 146
  untracked files); final collapsed status: 411 (`283 M`, `24 D`, `104 ??`),
  with an empty index. NUL-delimited status digests are
  `32fb08ce8d3b17c56dc0eebcbace8368979256fe7fbe0401e141fc9f0dbd80bc`
  (expanded) and
  `747072f2fcdffb0195da33c7956913b6dfb4a956112da8a099dab2c468c73695`
  (collapsed). Exact baseline attribution and plain-text path digests are
  recorded in `path-disposition.md`.
- Verified live remote `main`: `6873cf71f8fd66ce209f897ed04a1e08858409a6`,
  a straight 314-generated-commit descendant of local HEAD. A read-only
  sample found no Actions runs or check runs on that exact live SHA and only
  Vercel success; its successful producer run belongs to the parent SHA.
- Known remote Security failure retained as historical blocker evidence: run
  `31285534474`, job `93173499813`, 11 findings in five packages.
- Writers were serialized across package/public API, migrations/storage,
  runtime, API/MCP/CLI, dependency/workflow/deploy, and generated-doc surfaces.
  Protected `.env*`, key/credential/backup paths, `.venv`, build output, and the
  existing `deploy/terraform/.terraform/` cache were excluded.

## Implemented convergence

- Canonical split packages preserve the focused `0.3.3` Python/CLI/interface
  inventory while candidate metadata is `0.4.0rc1`. The executable comparison
  records 117/117 top-level exports, 17 CLI handlers with unchanged options,
  27 REST method/path decorators, 11 MCP actions, two MCP resources, unchanged
  existing config defaults, four SQLModel tables, and 40 persisted Proxy
  fields. Two security-intentional exceptions are implemented, tested, and
  documented: declared non-loopback API startup now requires auth mode plus a
  usable API key unless the explicit local-development override is set, and new
  credential-bearing File/SQLite writes require their documented Fernet-key
  configuration while legacy plaintext remains readable for migration. On
  2026-08-13 the maintainer explicitly approved both exceptions for release
  validation only; no staging, commit, push, tag, publication, deployment, or
  stable-promotion authority was granted.
- Alembic resources are packaged under `proxywhirl/_alembic`; migrations use
  process/file serialization and installed-wheel discovery reaches sole head
  `d4e5f6a7b8c9`.
- File storage returns rich `Proxy` models; SQLite retains its released 18-key
  dictionary `load()` result and adds `load_models()` for equivalent rich
  runtime hydration. Both sanitize malformed rows/errors and keep new
  credential-bearing writes encrypted at rest. JSON-mode tag serialization is
  sorted deterministically, and the default SQLite cleanup path awaits async
  autocommit configuration before `VACUUM`.
- Request settlement, sync/async rotator lifecycle, client-pool races,
  cancellation, HealthMonitor checks, retry/circuit/cache concurrency, and
  state counters were hardened with focused regressions.
- REST request/response byte bounds, force-auth routes, SSRF/redirect policy,
  health streaming, log/error redaction, CLI secret handling, MCP auth/lifecycle,
  and FastMCP 3 static resources were hardened.
- Dependency floors and the lock clear the prior five-package Safety failure;
  workflows use immutable action SHAs and exact tool versions.
- The release transaction verifies and pushes the immutable source tag before
  the irreversible PyPI publication, then creates the GitHub Release.
- Docker/Compose/Helm/Kubernetes/Terraform agree on single-replica SQLite
  operation, canonical encryption settings, probes, and secret references.
- Generated Python/CLI/strategy/OpenAPI references and `llms.txt` are
  deterministic; proxy-list source/mirror assets stayed protected and equal.
- `architecture-modernization-inventory.md` measures 142 modules, 246 internal
  import edges, three structural cycles, hotspots, compatibility seams, and a
  serialized post-release extraction order. Release-risky CLI/cache/storage/MCP
  module moves are explicitly deferred rather than mixed into the RC.
- `resource-ownership-inventory.md` maps 21 httpx construction sites, seven
  retained tasks, five thread/timer sites, three bounded queues, 45 lock/file-lock
  sites, four engines, 19 async-session contexts, and nine raw SQLite constructors.
  The resumed wave closed browser start/close races, bounded SOCKS reuse and DNS
  workers, joined metric timers, made cache shutdown deterministic, and settled
  MCP/API startup and logging resources.
- `dependency-and-fastmcp-research.md` records official advisory/changelog,
  Python-floor, transitive, and runtime-risk evidence. The five remediated locks
  remain compatible with Python 3.10+, while FastMCP 4.0.0b1 is deliberately
  deferred to an atomic post-0.4 change rather than a partial auth adapter.

## Final local assurance

Unless a row says otherwise, every command below exited 0 on 2026-08-13
against HEAD `040fa6a001097bf21828687439a3ba206066a08c` plus the final 411-record dirty
snapshot identified above. Required output was reviewed for warning, error,
traceback, deprecation, skipped-collection, and credential-shaped markers.

| Surface | Exact command/evidence and result |
| --- | --- |
| Focused repairs | Consolidated cache/API/MCP/browser/validator/security/rotator lifecycle suite under fatal `RuntimeWarning`: 741 passed, 7 skipped, 8 deselected. The affected validator/rotator pack then passed 292 tests after raw exception values were removed from new cleanup/validation logs. Browser concurrent-start, both start/close publication windows, partial-start failure, and cancellation cleanup passed 5/5. |
| Static | `uv run ruff check proxywhirl/ tests/`, `uv run ruff format --check proxywhirl/ tests/`, `uv run ty check proxywhirl/ tests/`, `just --fmt --check`, and `git diff --check` passed with zero diagnostics; CI-exact Ruff checked 384 files and the package/test format probe checked 378. |
| CI-parity Python | Final post-fix `just quality-gates`: both pytest phases completed with 4,644 passed, 40 skipped, 259 deselected, and 20 snapshots; coverage 7,476/8,194 statements, 718 missing, 91.2374908469612%. `coverage.json` SHA-256 is `22ea7bc37705ffca8a4a79a9f7814436affc596027ffc92be30de212d08281b2`. Captured output contained no warning, error, traceback, or deprecation markers. |
| Expanded Python | `uv run pytest tests/ -q -m "not slow" --ignore=tests/benchmarks --timeout=120`: 4,649 passed, 41 skipped, 252 deselected; 20 snapshots passed. |
| Benchmarks | `tests/benchmarks/test_modernization_baselines.py` collects exactly six local-only nodes and passed 6/6 under fatal `RuntimeWarning`, exactly 25 measured rounds each. Final host medians: sync HTTP pair 109.042 µs; async HTTP pair 243.292 µs; 10/100/1,000/10,000 pool snapshots 31.7041 ms; 1/16 MiB bounded parser streams 5.2173 ms; L1/L2/miss/eight-worker singleflight 8.5165 ms; SQLite insert/load/indexed query 27.0405 ms. The JSON evidence was validated then removed; client, task, thread, stream, and connection counts balanced. A separate broad threshold pack passed 49 and had three load-sensitive timing misses; isolated reruns passed, so no noise-level optimization was accepted. |
| Sources | `uv run proxywhirl sources --validate --fail-on-unhealthy --timeout 5 --concurrency 5`: 70/70 healthy and 0 unhealthy in 5.40 seconds, with no status delta. |
| API runtime | A disposable loopback subprocess using `uv run` returned `/api/ready` 200 with `data.ready=true` and the documented empty-pool `/api/health` 503 with `data.status=unhealthy`; SIGINT shutdown exited 0 and temporary SQLite cleanup completed. Focused auth/bind tests prove non-loopback startup rejects missing, empty, and placeholder API keys unless the explicit local-development override is set. There were no error, traceback, or `RuntimeWarning` markers. |
| Generation | Exact pnpm 10.13.1 `docs:generate` ran twice, followed by the build's prebuild generation. The complete 59-file generated path/size/SHA manifest remained `8617c8717644ed2ed53b89655cf26847710435623fa11e8302a00f2e017d6656` before/after all passes; second-run and post-build changes: 0. Protected `docs/proxy-lists` and `web/public/proxy-lists` digests remained `813634c765305d22c23b979cbf5f469d700064ec3cb1ae4a9461068f192123f7` and `6a16d07a6811ff1341d6380bc9460554bacf9b3e3e749caeb777d4a87584770d`; all 10 substantive mirror files are byte-equal. |
| Web | Exact pnpm 10.13.1 TypeScript no-emit and ESLint passed; Vitest: 84 passed, 2 skipped; Next 16.3.0 build: 89/89 static pages. Fresh Playwright E2E: 38 passed, 4 intentional matrix skips in 1.5 minutes. The only emitted warnings were the known test-harness `NO_COLOR`/`FORCE_COLOR` notices; no test failed. |
| Security | `uv lock --check`: 250 packages. Frozen all-extras/groups export: 249 exact pins, SHA `d74e86db2ac3cfa9952388ad46f16ef259d68f8009022d55a8e609835ad68347`. pip-audit 2.10.1: 0 vulnerabilities. Safety 3.8.1: 238 packages, 0 vulnerabilities and 0 ignored. Bandit 1.9.4: 32,276 LOC, 0 medium/high findings. Pinned pnpm 10.13.1 audit: 0 advisories at every severity. Reviewed scanner-only Authlib and Safety command-deprecation notices did not originate from the product. |
| Workflows | actionlint 1.7.12 and strict YAML/duplicate-key parsing passed. All 78/78 remote action uses are immutable 40-hex SHAs. Release order assertion passed: metadata/exact-SHA gates → tests/build/Twine → create-or-verify tag → push tag → PyPI → GitHub Release. Final `release.yml` SHA-256: `c356ddeda3d71a2002215f14fe46c19411daf294faa2b5e9ae8dbcadb24d23de`. |
| Deploy | Compose 5.3.1 validated all three configurations. Terraform 1.15.5 `fmt`, disposable read-only-lock `init -backend=false`, and `validate` passed. Checksum-verified temporary Helm 4.2.3 and kubeconform 0.7.0 passed strict lint and schema checks. Exact post-fix `docker build --check` was warning-free; image `sha256:c66c4730c5917d8259d64694454cd807ab81cc264ed284614c323c2e6a0fcb4d` installed `0.4.0rc1`, ran as UID/GID 999, wrote `/data`, returned authenticated readiness 200 and documented empty-pool health 503, and stopped with exit 0. Root Compose API+Redis reached healthy with equivalent probes and clean shutdown. Disposable containers, networks, and volumes were removed; pre-existing Docker Desktop remained running and validation images were retained. |
| Package | After the migration→MCP shadowing fix, an exact authorized 822-file snapshot (manifest `04d8d3d753509496bee359980bb6486119db491416eedfc46d69b39bd865bb05`) produced sdist SHA `6bd1be04f582997210697ea82dc1a31ae207969b12c1dffb776ae59af9b90234` (337,239 bytes/183 members) and wheel SHA `ba4f1c7c110afe4938f929fc4a9b049730e581a530de7f888d38545869c39461` (376,752 bytes/149 members). Twine 7.0.0, all 149 RECORD rows, and 143 source/sdist/wheel/installed runtime-file parity passed. Python 3.11.15 `[all]` installed 129 packages and `uv pip check` passed. In one fatal-`RuntimeWarning` process, migration preserved external `mcp` and `mcp.client` resolution, FastMCP connected and read both JSON resources, and core exports, CLI/MCP help, HTTP/2 sync closure, File/SQLite encrypted/fail-closed behavior, and authenticated API probes passed. Alembic benignly prepended the containing site-packages directory once but never the installed `proxywhirl/` directory, so no SDK shadowing remained. The exact temporary artifact tree was removed after proof. |
| Protected paths | Authorized read-only review found no real secret/private-key/cloud-token/JWT values; gitleaks, private-key detection, Python static checks, exact-pnpm TypeScript, YAML/Compose structure, whitespace, and 46 credential/migration tests passed. Release-blocking semantic findings remain: `deploy/kubernetes/secret.yaml` is not ignored after its tracked placeholder is removed; `export_credentials(encrypt=True)` leaves username and arbitrary `extra_fields` plaintext; colon-delimited credential encoding does not round-trip usernames containing `:`; raw-string `Credential` construction is accepted then fails at `SecretStr` access. The untracked `db_backup.py` is a docstring-only unreferenced shim and is automatically packaged. |

## Documentation maintenance summary

- **Public/API and structure changes:** updated generated Python, CLI, strategy,
  REST/OpenAPI, navigation, and MCP naming surfaces through their generators.
- **Operations changes:** aligned deployment/auth/storage prose and generated
  references with the single-replica manifests and canonical environment names.
- **Generator policy:** no generated page was hand-authored; the source scripts
  own generated MDX/JSON and `llms.txt`. A volatile generation timestamp was
  removed and determinism is regression-tested.
- **Accessibility/rendering:** lint, TypeScript, component tests, static build,
  and affected Playwright accessibility/navigation checks passed; internal
  links, icon names, decorative hiding, and reduced-motion behavior were reviewed.
- **Protected artifacts:** `docs/proxy-lists/**` and
  `web/public/proxy-lists/**` were content-hash checked and not regenerated by
  the docs-steward wave.

## Release stop conditions

The local candidate is not accepted, tagged, published, or deployed. Exact
post-fix artifact and container gates are green under the maintainer's
validation-only protected-path authorization. Release remains blocked by the
credential-manager encryption/serialization/type-contract findings and the
unignored Kubernetes secret target; validation-only authority did not permit
implementation fixes. Completion still requires those repairs and reruns, an
exact committed candidate SHA, plus explicit authority for
commit/push/workflow dispatch, successful `CI`, `Security Scan`, and strict
`Validate Proxy Sources` runs on that exact SHA, log/artifact review, explicit
an RC acceptance interval, and a separately authorized `0.4.0` promotion. The
two documented security-intentional compatibility exceptions were explicitly
approved for `0.4.0rc1` validation on 2026-08-13.

Compose, Helm, Kubernetes, Terraform, and exact post-fix container checks are
green. Local dirty-tree evidence does not substitute for exact-candidate remote
checks. Repeated earlier sdists had identical normalized
payloads but 24 setuptools-generated mtime differences; the wheel is
byte-reproducible, and the sdist mtime residual must remain disclosed. Existing
ignored `build/`, `dist/`, and `proxywhirl.egg-info/` directories predated final
assurance and were not removed or treated as release input.

The task ledger closes 133 of 147 bounded leaves. The 14 open leaves are not
silent omissions: they cover exact committed-candidate freezing, the
authorization-gated proxy-list regeneration, three explicitly deferred
post-release module extractions, reopened credential/static-security repairs,
exact-SHA remote assurance, RC acceptance, and stable promotion.
