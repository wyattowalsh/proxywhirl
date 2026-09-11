# Architecture modernization and resource-ownership inventory

This is the read-only architecture evidence artifact for tasks **5.1 (M1.1)**
and **5.2 (M1.2)**. Its resource summary cross-checks **2.25 (F7.1)**; the
dedicated `resource-ownership-inventory.md` is authoritative for completing
that task. This file also defines bounded candidate work and stop rules for
**5.3 (M2.1)**, **5.5 (M3.1)**, **5.6 (M3.2)**, and **5.9 (M5.1)**. It does
not itself authorize or perform any product extraction.

## Disposition

| Task | Evidence disposition |
| --- | --- |
| 2.25 | Cross-check only: this file summarizes every live ownership category; `resource-ownership-inventory.md` is the authoritative task-completion artifact. |
| 5.1 | **Eligible to mark complete:** current size, dependency, cycle, history, test-seam, compatibility, and CLI coverage measurements are recorded. |
| 5.2 | **Eligible to mark complete:** only the serial leaves listed below are approved as future candidates; actual module moves are deferred for this dirty release candidate. |
| 5.3 / 5.5 / 5.6 | Not completed here. These are implementation tasks with shared-file writer locks. |
| 5.9 | **Completed by the subsequent benchmark leaf:** the six planned local-only distribution nodes now exist and have a validated 25-round baseline; results are appended below. |

The release-safe decision is deliberately narrow: **perform no actual 5.3,
5.5, or 5.6 module extraction on this dirty `0.4.0` release candidate.** The
listed leaves are approved scopes for a later frozen base, not authorization
to mutate the current RC. The current release already has a large, uncommitted
package split, public/private monkeypatch seams, and concurrent assurance
writers. Lifecycle correctness and candidate freezing take precedence over
another cross-cutting rewrite.

## Measurement snapshot and scope

- Branch: `main`.
- HEAD at measurement: `040fa6a001097bf21828687439a3ba206066a08c`.
- The worktree was intentionally dirty and concurrently active. The final
  status count and digest are recorded in [Reproduction and validation](#reproduction-and-validation).
- Local history contains 278 commits, spanning
  `2026-05-15T04:30:18-04:00` through `2026-07-04T21:13:57-04:00`.
- Physical LOC counts include comments and blank lines. Dependency counts are
  unique imports, not weighted runtime calls.
- The import graph contains all 142 Python modules under `proxywhirl/`,
  including currently untracked package-split files. The standard-library AST
  scanner counts local and `TYPE_CHECKING` imports so it is a conservative
  structural graph, not a claim that every edge executes during import.
- `radon`, `networkx`, `pydeps`, and `grimp` are not installed. No dependency
  or lock change was authorized, so cycles were computed with a local
  standard-library Tarjan scan.
- Architecture group boundaries are explicit: CLI is `proxywhirl/cli/**/*.py`
  plus `cli_config_templates.py`; storage is `storage.py`, `migrations.py`, and
  `_alembic/**/*.py`; sources/fetch is `sources.py`, `browser.py`, `geo.py`, and
  `fetchers/**/*.py`. Other groups are the named packages or files in the
  table.

## Resource-ownership cross-check (2.25 / F7.1)

### HTTP clients

“Closer” names the actual owner. A context-managed client is intentionally
one-shot; a borrowed client is not closed by the callee.

| Creator / exact symbol | Reuse and bound | Closer | Result |
| --- | --- | --- | --- |
| `proxywhirl/cli/_impl.py:591-818` `request()` creates `httpx.Client` at line 728 | One CLI invocation and retry loop | Synchronous `with` exit | Closed on success/error. |
| `proxywhirl/cli/_impl.py:821-1148` `pool()` creates `httpx.Client` at line 1071 | One pool-health invocation | Synchronous `with` exit | Closed. |
| `proxywhirl/cli/_impl.py:2163-2230` `check_health()` creates at line 2170 | One health probe | Synchronous `with` exit | Closed. |
| `proxywhirl/cli/_impl.py:2326-2426` `validate_proxy()` uses `httpx.get` at line 2370 | One convenience call; httpx owns its implicit client | Call return/exception | Closed by httpx; not reusable. |
| `proxywhirl/api/routes/proxies.py:510-557` `_check_proxy_health()` creates at line 533 | One proxy probe; concurrency bounded by the caller semaphore | Async context exit | Closed. |
| `proxywhirl/fetchers/fetcher.py:223-240` `ProxyFetcher._get_client()` creates `_client` at line 233 | Reused by one fetcher; limits 50 connections / 10 keepalive | `ProxyFetcher.close()` at `242-276`; async context at `641-649` | Explicit, cancellation-settled close. |
| `proxywhirl/fetchers/validator.py:205-221` `_get_client()` creates `_client` at line 213 | Reused by one validator; limits 1000 / 100 | `ProxyValidator.close()` at `288-325`; async context at `327-333` | Explicit close. Current product use is limited to direct/no-proxy helpers. |
| `proxywhirl/fetchers/validator.py:223-286` `_get_socks_client()` | LRU reuse per exact URL/credentials under an async lock; cap is `min(concurrency, 100)` | Eviction closes at `255-262`; `ProxyValidator.close()` snapshots, clears, and closes all at `288-325` | Bounded and explicit after the current lifecycle hardening. No non-test product callsite currently exists. |
| `proxywhirl/fetchers/validator.py:421-454`, `461-536`, `538-710`, and `823-996` | Per-operation clients | Each async context exit | Closed; batch concurrency remains bounded. |
| `proxywhirl/geo.py:231-297` `geolocate_with_api()` creates at line 263 | One client reused across the function's API attempts | Async context exit | Closed. |
| `proxywhirl/mcp/server.py:1032-1138` `_validate_proxy_impl()` creates at line 1090 | One MCP validation call | Async context exit | Closed. |
| `proxywhirl/rotator/sync.py:224-240` `ProxyWhirl.__enter__()` creates shared `_client` at line 227 | Context lifetime; configured limits | `ProxyWhirl.close()` at `246-262` | Closed idempotently. This compatibility client is not the per-proxy request pool. |
| `proxywhirl/rotator/sync.py:696-746` `_get_or_create_client()` creates at line 722 | Reused by proxy ID in bounded `LRUClientPool` (`client_pool.py:19-174`) | Duplicate/eviction/remove/clear close at `client_pool.py:87-153`; rotator close clears all | Bounded and explicit. |
| `proxywhirl/rotator/async_.py:330-347` `AsyncProxyWhirl.__aenter__()` creates shared `_client` at line 333 | Async-context lifetime; configured limits | `aclose()` at `353-383` | Closed idempotently and cancellation-safely. |
| `proxywhirl/rotator/async_.py:684-727` `_check()` creates at line 705 | One health probe | Async context exit | Closed. |
| `proxywhirl/rotator/async_.py:729-781` `_get_or_create_client()` creates at line 757 | Reused by proxy ID in `AsyncLRUClientPool` (`async_.py:39-213`), default max 100 | Duplicate/eviction/remove/clear at `async_.py:95-185`; rotator `aclose()` clears all | Bounded and explicit. |
| `proxywhirl/sources.py:1271-1346` `validate_source()` creates at line 1296 only when no client is borrowed | One source validation, or reuse of caller-owned batch client | Local async context closes only the locally created client | Borrowed-owner boundary is correct. |
| `proxywhirl/sources.py:1349-1395` `validate_sources()` creates at line 1382 | One shared client across the semaphore-bounded batch | Async context exit | Closed after all gathered validations. |

No other product `httpx.Client`, `httpx.AsyncClient`, or top-level
`httpx.get/post/put/delete/patch/request/stream` constructor/call exists in the
142-module scan. `retry.py` and `orchestration.py` operate on injected callables
or exceptions and do not own an HTTP client.

### Browser, response streams, and file streams

| Resource / exact symbol | Creator and reuse | Closer / cancellation owner | Result |
| --- | --- | --- | --- |
| Playwright controller, browser, and contexts: `proxywhirl/browser.py:242-294` `BrowserRenderer.start()` | One controller/browser per renderer; `max_contexts` contexts held in an `asyncio.Queue` | `BrowserRenderer.close()` locks and snapshots state first, then closes all contexts, browser, and Playwright controller at `307-372`; `__aexit__` at `655-657` | Complete and idempotent, including start failure and concurrent lease/release. |
| Browser pages: `BrowserRenderer.render()` at `proxywhirl/browser.py:462-648` | One page per render; pooled context is borrowed | Page closed in `finally` at `634-638`; context returned at `640-648` | Complete on success/error/cancellation. |
| Fetch stream: `proxywhirl/fetchers/fetcher.py:280-323` | Borrowed fetcher client; redirect-by-redirect `client.stream()` at line 296 | Async context closes each response; bounded reader is `fetchers/parsers.py:597-615` with 64 KiB chunks | Closed and memory-bounded. |
| Source validation stream: `proxywhirl/sources.py:1179-1232` | Borrowed source-validation client; stream at line 1192 | Async context closes; bounded reader at `1140-1173` with 64 KiB chunks | Closed and memory-bounded. |
| Sync rotator stream: `proxywhirl/rotator/sync.py:59-102` `_request_with_bounded_response()` | Borrowed pooled client; `send(..., stream=True)` at line 77 | Explicit response close at line 90 in `finally` | Closed and bounded. |
| API health-probe stream: `proxywhirl/api/routes/proxies.py:510-557` | Local client and response stream at lines 533-537 | Nested async contexts | Closed. |
| API output streams: `api/routes/proxies.py:357-411` and `423-439`; `api/routes/health.py:263-277`; `api/streaming.py:17-119` | Async generators produce bounded NDJSON/metrics chunks; `StreamingResponse` owns iteration | Starlette request/disconnect lifecycle owns generator finalization | No external client/DB handle is captured. |
| FileStorage streams: `proxywhirl/storage.py:556-726` | `aiofiles.open` at lines 623, 678, 684 | Every handle is an async context | Closed. |
| Remaining ordinary file streams | Context-managed `open()` sites in `config.py:478-564`, `utils.py:765-826`, `pool_snapshot.py:149-218`, `exports.py:411-764`, `cache/manager.py:901-1035`, and `cli/_impl.py:2477-2498` | Lexical `with` owner | Closed. |

`BrowserRenderer._pool_lock` is created at `browser.py:277` and now acquired by
close/acquire/release at `325-442`; `_leased_context_ids` prevents duplicate
returns. It is part of the current concurrent queue-safety proof, not dead
state.

### Tasks, threads, process, locks, and queues

| Resource / exact symbol | Creator / reuser | Stop, join, or lifecycle owner | Result |
| --- | --- | --- | --- |
| Browser cleanup task `browser.py:352-361` | Local task shields cleanup from caller cancellation | Same `close()` awaits it even after external cancellation | Settled. |
| Fetcher cleanup task `fetchers/fetcher.py:260-270` | Local task closes periodic task, client, and validator | Same `close()` shields and awaits | Settled. |
| Fetcher periodic task/event `fetchers/fetcher.py:652-709`, event at line 168 | `_refresh_task` retained on the fetcher; one live task enforced | `stop_periodic_refresh()` at `640-650`; `close()` invokes it | Retained, cancelled, awaited, cleared. |
| Validator cleanup task `fetchers/validator.py:306-320` | Local task closes snapshot of reusable clients | Same `close()` shields and awaits | Settled. |
| Health monitor task `models/core.py:1600-1740` | `HealthMonitor.start()` stores one task at line 1660 | `stop()` at `1662-1695` cancels, awaits, and clears | Settled. |
| Orchestration selection tasks `orchestration.py:499-545` | Two local tasks wrap default-executor work | Both cancellation handlers shield then await completion before re-raising | Settled. |
| Gather-only coroutine batches | `_proxy_views.py:97-108`, API `proxies.py:566-606`, `browser.py:343-345`, `enrichment.py:186-213`, fetcher `531-638`, validator `691-800` / `802-975`, sources `1349-1395`, async rotator `687-730`, health monitor `1712-1726` | The calling coroutine awaits each `gather`; semaphores bound network batches where relevant | Structured, no detached tasks. |
| Default executor work | `asyncio.to_thread` in `_proxy_views.py:244-259`, `api/core.py:91-197`, API routes/runtime, `enrichment.py:100-132`, migrations, models async helpers, orchestration, rotators, storage fsync, and browser policy checks | Event loop owns executor shutdown; every returned awaitable is awaited. Shielded orchestration tasks are also retained and awaited | Borrowed workers, not module-owned threads. |
| Cache TTL thread/event `cache/manager.py:65-215` | `TTLManager.start()` creates one daemon thread at line 118; event controls the loop | `TTLManager.stop()` at `126-157` sets event and joins up to 5 seconds; `CacheManager.close()`/context at `371-403` now calls it | Explicit owner plus destructor fallback. |
| Metrics timers/events | Sync rotator `sync.py:124-278`, timer lifecycle `1350-1401`; async rotator `async_.py:235-410`, timer lifecycle `969-1030` | Context entry starts one daemon timer; a dedicated lock serializes create/reschedule/cancel; close/aclose cancels and bounded-joins outside the timer thread | Bounded, race-aware daemon lifecycle; destructor cancellation intentionally avoids joining. |
| Bootstrap bridge thread `rotator/_bootstrap.py:256-286` | One daemon thread only when sync code is called under a running loop | Caller immediately `join()`s and propagates result/error | Synchronous ownership; join has no timeout because completion is the requested operation. |
| DNS resolver worker `security.py:124-182` | One daemon thread per lookup, admitted through a process-wide `BoundedSemaphore(8)`; result uses `Queue(maxsize=1)` | Completed workers are joined briefly; timed-out workers finish later, release their slot in `finally`, and cannot keep process shutdown alive | Bounded outstanding work and honest timeout after the current lifecycle hardening. |
| Safe-regex worker process/pipe `safe_regex.py:293-348` | One spawn-context process and duplex pipe per isolated operation | Parent closes pipe and `_stop_worker_process()` terminates/joins at `186-221` and `322-340` | Bounded process ownership. |
| Browser context queue | `browser.py:275`, max size `max_contexts` | Contexts borrowed/lease-tracked at `374-407`, returned at `409-442`, and locked against close | Bounded and race-aware. |
| Sync request queue | `rotator/sync.py:187-189`, max `config.queue_size` | Immediate producer/consumer at `948-1026`; `clear_queue()` at `1462-1484` drains | Bounded; it is not a background-worker queue. |

Lock ownership is object- or call-scoped; locks have no close method. The full
set is:

- cache: `_LoadFlight.event` and TTL stop event at
  `cache/manager.py:38-43,65-215`; `CacheManager` RLock/singleflight Lock at
  `257-303`; JSONL state RLock and lexical `portalocker.Lock` acquisitions at
  `cache/tiers.py:370-836`; disk connection Lock/operation RLock at
  `857-1427`; SQLite-tier RLock at `1436-1893`;
- models and strategies: proxy rolling-window Lock at
  `models/core.py:357-862`, pool RLock at `998-1525`, strategy state locks in
  `strategies/base.py:82-194`, `round_robin.py:31-68`,
  `least_used.py:42-98`, `weighted.py:40-249`, `session.py:35-184`, and
  registry class/instance RLocks at `registry.py:19-235`;
- retry/control: `RetryMetrics` Lock at `retry.py:145-251`, sync/async circuit
  locks at `circuit_breaker.py:172-224,238-290`, token/rate model locks at
  `rate_limiting.py:39-241`, and sync/async rotator pool, strategy, and
  bootstrap locks at `rotator/client_pool.py:19-174`,
  `rotator/sync.py:124-221`, and `rotator/async_.py:39-327`;
- global/process: MCP rotator `asyncio.Lock` at `mcp/server.py:56,241-354`,
  Alembic process Lock plus per-database `FileLock` at
  `migrations.py:73,140-156`, and CLI singleton `FileLock` at
  `utils.py:785-852` / `cli/_impl.py:368-498`;
- call-scoped async synchronization: API health semaphore at
  `api/routes/proxies.py:566-606`, source semaphore at
  `sources.py:1349-1395`, validator semaphores/event at
  `fetchers/validator.py:712-821,823-996`, and health-monitor semaphore at
  `models/core.py:1712-1726`.

The state buffers adjacent to these resources are also bounded:
`CircuitBreakerMetrics` uses `deque(maxlen=10000)` at
`circuit_breaker.py:40-54`; retry current-attempt and event histories are
bounded in `retry.py:145-251`; the HTTP client LRU pools cap entries; and both
explicit queues declare maximum sizes.

### Database engines, connections, and sessions

| Resource / exact symbol | Creator and reuse | Closer | Result |
| --- | --- | --- | --- |
| `SQLiteStorage.engine`, `storage.py:768-832` | One async SQLAlchemy engine per storage at line 807; pooled for storage lifetime | `SQLiteStorage.close()` at `1019-1025` disposes it | Explicit and idempotent. |
| Storage initialization connection | `SQLiteStorage.initialize()` at `984-1017` uses `engine.begin()` | Async context | Closed. |
| Storage operation sessions | `AsyncSession` at lines 1241, 1302, 1345, 1436, 1462, 1492, 1520, 1585, 1681, 1708, 1757, 1783, 1823, 1854, 1883, 2007, 2111, 2174, 2198 | Each method owns one `async with AsyncSession(self.engine)`; engine is borrowed | Async context closes every session on success/error. |
| Storage maintenance connection | `storage.py:1993-1997` vacuum path | `async with self.engine.connect()` | Closed. |
| SQLite connect hook cursor | `storage.py:814-820` | Per newly connected DBAPI connection | `try/finally` closes cursor. |
| Migration revision engine/connection | `migrations.py:235-271` creates engine at line 259 and connects at 262 | Connection context; engine `dispose()` in `finally` at `270-271` | Closed on all paths. |
| Alembic online engines/connections | `_alembic/env.py:115-163` | Async connection at 132 / sync connection at 160 | Contexts close connections; engines dispose at 135 / 163. |
| Disk L2 persistent sqlite connection | `cache/tiers.py:857-943`; lazy create at line 902 | Reused under connection + operation locks for tier lifetime | `DiskCacheTier.close()` at `913-943`; `CacheManager.close()` at `371-403`; destructor is only fallback. |
| SQLite L3 short connections | `cache/tiers.py:1436-1893`; creates at 1484, 1607, 1715, 1783, 1811, 1837, 1861, 1882 | One per operation under RLock | Every `sqlite3.connect` is wrapped by `contextlib.closing`; closed. |
| API storage owner | `api/core.py:91-197` lifespan | One optional `SQLiteStorage` per app lifespan | Encompassing `try/finally` closes storage and rotator, including startup failure. |
| MCP bootstrap storage | `mcp/server.py:230-291` `get_rotator()` | One short-lived `SQLiteStorage` only when DB exists | `finally` at `264-273` closes through initialize/load/add failures. |
| Other storage consumers | CLI fetch helpers `cli/_impl.py:1421-1774`, exports `exports.py:718-778` | Each creates a short-lived storage | Owning coroutine `finally`/close. |

## Architecture hotspot measurements (5.1 / M1.1)

### Size and dependency surface

| Area | Files / physical LOC | Unique internal dependencies outside group | Unique external top-level imports | Incoming internal modules |
| --- | ---: | ---: | ---: | ---: |
| CLI | 3 / 2,872 | 11 | 21 | 0 |
| cache | 5 / 3,660 | 3 | 18 | 2 |
| models package | 2 / 2,101 | 5 | 16 | 36 |
| storage + migrations | 12 / 3,868 | 3 | 28 | 5 |
| MCP | 3 / 1,704 | 9 | 15 | 0 |
| sources / fetch / browser / geo | 8 / 5,145 | 5 | 22 | 4 |
| retry / circuit / rate | 3 / 1,749 | 2 | 16 | 5 |
| configuration | 3 / 1,080 | 2 | 18 | 13 |

The largest single live implementation files at this snapshot are:

| File | LOC | High-value symbol ranges |
| --- | ---: | --- |
| `proxywhirl/cli/_impl.py` | 2,566 | app/context `110-498`; rendering `501-582`; request `591-818`; pool `821-1148`; config `1151-1348`; export/fetch `1356-2014`; sources `2018-2102`; health `2106-2322`; validate/import `2326-2562` |
| `proxywhirl/storage.py` | 2,227 | codecs/tables `38-395`; FileStorage `491-726`; SQLiteStorage `729-2206` |
| `proxywhirl/models/core.py` | 2,040 | Proxy `357-862`; ProxyPool `998-1525`; HealthMonitor `1600-1911` |
| `proxywhirl/cache/tiers.py` | 1,893 | memory `198-348`; JSONL `351-836`; disk L2 `839-1427`; SQLite L3 `1430-1893` |
| `proxywhirl/mcp/server.py` | 1,531 | auth/policy `69-182`; lifespan `196-217`; runtime `230-372`; composition `410-547`; implementations `555-1179`; unified tool `1202-1317`; resources/prompts `1330-1517` |
| `proxywhirl/sources.py` | 1,459 | catalog `36-1023`; validation/fetch `1026-1459` |
| `proxywhirl/retry.py` | 1,196 | policy/metrics/control all in `44-1196` |
| `proxywhirl/cache/manager.py` | 1,120 | TTL manager `47-215`; CacheManager `218-1120` |
| `proxywhirl/fetchers/validator.py` | 996 | client lifetime `147-333`; validation/batches `421-996` |
| `proxywhirl/fetchers/parsers.py` | 881 | parser implementations and bounded stream reader `86-881` |
| `proxywhirl/config.py` | 741 | config discovery/load/save `45-741` |
| `proxywhirl/fetchers/fetcher.py` | 709 | client/render/fetch/task lifecycle `99-709` |
| `proxywhirl/browser.py` | 657 | renderer lifecycle `93-657` |
| `proxywhirl/circuit_breaker.py` / `rate_limiting.py` | 312 / 241 | cohesive current modules; no split justified |

The exact outbound dependency set explains why line count alone is not the
priority signal:

- CLI imports root/public facade, config, exports, fetchers, formatters,
  models, rotator, sources, storage, types, and utils.
- Cache imports only models, settings, and types; its hotspot is backend and
  concurrency density rather than fan-out.
- Models has the highest fan-in and therefore the highest compatibility risk.
- MCP imports nine product modules and combines policy, lifetime, dispatch,
  schemas, resources, prompts, and CLI composition.
- Configuration has 13 incoming modules despite modest LOC, so moving config
  types is a cross-tree change, not a small extraction.

### Import cycles

The 142-module / 246-edge structural graph has three non-trivial strongly
connected components:

1. **Fetch/model/facade SCC (7 modules):** `proxywhirl.fetchers` →
   `fetchers.fetcher` → `fetchers.parsers` → `fetchers.validator` →
   `proxywhirl.models` → `models.core` → `proxywhirl.utils`. Concrete late or
   guarded reverse edges include `parsers.py:81`, `validator.py:30,135,558`,
   `models/core.py:469,1732`, and `utils.py:19`. Some are deliberately lazy, so
   this is structural debt rather than proof of an import-time failure.
2. **Strategy SCC (2 modules):** `strategies/registry.py:15` imports session;
   `strategies/session.py:297` late-imports registry resolution.
3. **CLI compatibility SCC (2 modules):** `cli/__init__.py:10-47` re-exports
   `_impl`; `_impl.py:32-41` deliberately imports the package at call time so
   existing monkeypatch targets `proxywhirl.cli.socket` and
   `proxywhirl.cli.load_config` keep working.

Do not “fix” these with new compatibility shims. The release-safe extraction
plan below removes an edge only when the tests demonstrate that the facade and
patch contract remain intact.

### Local change frequency and current churn

Commit counts are lineage-aware: deleted predecessor monoliths (`cli.py`,
`models.py`, `fetchers.py`) are included with their replacement package paths.
This matters because direct history for currently untracked split files is
zero. Counts cover the complete 278-commit local history.

| Area | Unique touching commits | Most recent local commit | Current status records | Tracked diff / untracked Python |
| --- | ---: | --- | ---: | --- |
| CLI | 5 | `2026-07-04T21:13:57-04:00` | 4 | `+4/-2487`; 2 files / 2,627 LOC |
| cache | 3 | `2026-07-03T14:43:29-04:00` | 3 | `+403/-260`; none |
| models | 4 | `2026-07-03T14:43:29-04:00` | 4 | `+4/-1785`; 2 files / 2,101 LOC |
| storage | 7 | `2026-07-04T21:13:57-04:00` | 12 | `+984/-404`; 10 files / 1,108 LOC |
| MCP | 5 | `2026-07-03T14:59:26-04:00` | 1 | `+158/-103`; none |
| sources/fetch | 6 | `2026-07-04T21:13:57-04:00` | 9 | `+345/-2209`; 5 files / 2,654 LOC |
| retry/circuit/rate | 6 | `2026-07-04T21:13:57-04:00` | 3 | `+153/-36`; none |
| configuration | 4 | `2026-07-03T14:43:29-04:00` | 3 | `+134/-40`; 1 file / 107 LOC |

These small historic counts must not be misread as stability: the current
uncommitted monolith-to-package replacement is much larger than the recorded
commit frequency.

### Test seams and compatibility boundaries

| Area | Stable boundary and fragile seam | Focused proof required after an extraction |
| --- | --- | --- |
| CLI | Console scripts in `pyproject.toml:127-129`; package facade `cli/__init__.py:1-61`; Typer app, help ordering, option spelling/defaults, exit codes; private patch seams such as `_fetch_from_sources`, `_save_results`, `_export_results`, and `_revalidate_existing_proxies` in `cli._impl` | `uv run pytest tests/unit/test_cli.py tests/unit/test_cli_coverage.py tests/unit/test_cli_config_templates.py tests/unit/test_wave3_package_compat.py -q --no-cov -n0` plus `uv run proxywhirl --no-lock --help` |
| cache | Public re-exports `cache/__init__.py:1-44`; serialized/encrypted entry format; coherence, stampede, TTL, lock ordering; tests patch `proxywhirl.cache.tiers.portalocker.Lock` and `proxywhirl.cache.tiers.sqlite3.connect` | cache unit/concurrency/coherence/stampede/property tests; retain forwarding patch names or deliberately update the tested seam in the same leaf |
| models | Root lazy export map `__init__.py:18-170,177-295`; model facade `models/__init__.py:1-61`; Pydantic validation/serialization and pool lock/index invariants | `test_models.py`, `test_proxy_pool_state.py`, `test_proxy_pool_concurrency.py`, model property/contract tests, `test_public_api.py`, and `test_wave3_package_compat.py` |
| storage | Public `proxywhirl.storage` imports; SQLite/Alembic durable schema; migration revision chain; legacy-row decode and the released load/load_models shapes | `test_storage.py`, `test_sqlite_storage.py`, migration/schema tests, and `integration/test_storage_hydration.py` |
| MCP | `mcp/__init__.py:1-25`; 11 action values, resources/prompts/tool JSON schemas, auth/redaction, lifespan; tests patch many `proxywhirl.mcp.server` globals and private implementation functions | `test_mcp_server.py`, `test_mcp_coverage_wave4.py`, `test_mcp_auth.py`, MCP integration/contract snapshots |
| sources/fetch | `fetchers/__init__.py:1-57`; `ALL_SOURCES` and recommended/category constants; parser and validator contracts; strict source-gate behavior; http mocks and browser policy | `test_sources.py`, `test_fetchers.py`, `test_validator_client_pool.py`, browser/outbound-policy, parser and source contract tests |
| retry/circuit/rate | Root exports and public class signatures; sync/async parity; tenacity behavior; snapshot/state enums; event-history bounds | retry policy/executor/metrics/timing/property/integration tests, circuit sync/async/state/property tests, rate model/integration tests |
| configuration | Env/file/default precedence; `CLIConfig`, `ProxyConfiguration`, `APISettings`, MCP settings; root exports and sanitized secret handling | `test_config.py`, `test_config_ssot.py`, settings/API config tests, and CLI config tests |

The root lazy facade currently advertises 117 public names. Any extraction that
touches a root export, package facade, public API, file structure, CLI surface,
or generated reference must take the single facade lock and run the repo's
docs-steward/docs generation sequence after the implementation tests.

The measured CLI candidate is already healthy without another structural move:
the focused run completed **186 tests passed** and reported **92% coverage**
across the CLI candidate (**924 statements, 74 missed**). That satisfies the
configured modernization measurement intent while reinforcing the defer
decision: coverage is not the reason to risk the current facade/patch seams.

## Selected release-safe splits and explicit deferrals (5.2)

### 5.3 / M2.1 — CLI behind one app

The following is an approved **post-`0.4.0` candidate order**, one serial leaf
at a time. It is not current-RC work:

1. Establish single-owner `_app.py` and `_context.py` internals while leaving
   `cli/__init__.py` and `_impl.py` forwarding names stable. Preserve command
   registration order exactly.
2. Extract the config family (`_impl.py:1151-1348`). Run the full CLI focused
   gate and compare `--help` before proceeding.
3. Extract the pool family (`821-1148` plus `1284-1323`).
4. Extract fetch/export helpers and command (`1356-2014`) as one leaf because
   their private monkeypatch seams cross those ranges.
5. Extract sources (`2018-2102`), then health (`2106-2322`), then
   validate/import (`2326-2562`), each as a separate leaf.
6. Extract request (`591-818`) last; it shares top-level URL-policy, formatter,
   retry, and context concerns with the preceding families.

Stop after any help/options/exit-code, monkeypatch-target, coverage, import, or
root-export drift. Do not parallelize these leaves: every one removes lines
from `_impl.py`, changes command registration, and may touch the same facade
and CLI tests.

**Deferred:** a command framework rewrite, nested-app redesign, new dependency,
public import rename, or full 2,566-LOC move. The current RC does not need any
of those to ship safely.

### 5.5 / M3.1 — cache and storage

Approved post-`0.4.0` candidate order:

1. Keep the just-added deterministic `CacheManager.close()`/context protocol
   stable and prove it under repeated close, active TTL, and disk-connection
   tests before moving its code.
2. Extract `DiskCacheTier` (`cache/tiers.py:839-1427`) into an internal module,
   re-export it from `cache.tiers` and `cache.__init__`, and preserve the tested
   `portalocker`/`sqlite3.connect` patch seam.
3. Extract `SQLiteCacheTier` (`1430-1893`) in a separate serial leaf with the
   same facade and coherence/migration gates.
4. Only then consider extracting `TTLManager` (`cache/manager.py:47-215`) and
   `FileStorage` (`storage.py:491-726`) as independent internal leaves.

**Deferred:** splitting `SQLiteStorage` (`storage.py:729-2206`), moving table
models/codecs (`38-395`), changing the SQLite schema or migration chain,
unifying cache and durable storage, or changing serialized formats. The 19
session-owning methods, Alembic chain, legacy rows, and test patch points make
those post-`0.4.0` work.

### 5.6 / M3.2 — MCP composition

Approved post-`0.4.0` candidate order:

1. Pure auth/policy/presentation helpers (`mcp/server.py:69-182`) behind
   forwarding names in `server.py`.
2. Runtime acquisition/cleanup (`230-372`) only after dependencies can be
   injected while preserving the existing `server._rotator`, `_mcp_db_path`,
   `AsyncProxyWhirl`, `SQLiteStorage`, and `_auto_fetch_proxies` test seams.
3. Read-only implementations (`555-957`), then mutating implementations
   (`958-1179`), while leaving the unified action schema and registration in
   the composition root.
4. Resources and prompts (`1330-1517`) last, with byte-for-byte schema and
   snapshot comparison after each leaf.

**Deferred:** changing FastMCP major APIs, the unified 11-action schema,
auth semantics, error shape, transport, resource URIs, prompt names, or doing a
single tool-directory rewrite. Those are public protocol changes, not internal
extractions.

### Writer-conflict order

One writer owns each row until its focused gate is green:

| Order | Exclusive writer surface | Barrier before next writer |
| ---: | --- | --- |
| 0 | Finish current lifecycle/resource fixes in cache, MCP, API, fetcher/validator, browser, and rotators | Focused teardown/cancellation/resource tests green; freeze exact base digest |
| 1 | CLI `_impl.py`, CLI command modules, CLI facade, CLI tests | Full CLI gate + help diff green after every family; no concurrent CLI writer |
| 2 | Cache `tiers.py`/new tier module/cache facade/cache tests | Tier/coherence/stampede/migration gates green after every backend |
| 3 | FileStorage-only leaf and storage tests | Storage hydration/compatibility gates green; no Alembic/schema touch |
| 4 | MCP `server.py`/new internals/MCP facade/MCP tests | Tool/resource/prompt/auth schema snapshots and lifecycle tests green after every leaf |
| 5 | Root `proxywhirl/__init__.py` and public API tests, if genuinely required | All package writers complete; public export inventory unchanged |
| 6 | Generated docs/reference surfaces | All code/facades frozen; deterministic second generation clean |

No CLI, cache, storage, or MCP leaf may share a writer with its adjacent leaf.
The root facade, `pyproject.toml`, `uv.lock`, Alembic files, generated docs, and
task/evidence ledgers remain separate exclusive locks.

## Benchmark baseline plan (5.9 / M5.1)

### What exists now

`tests/benchmarks/` contains 7 files, 2,213 physical LOC, and 67 collected test
functions/methods. The useful current pytest-benchmark seams are:

- client-pool get/put:
  `test_async_rotator_benchmark.py:129-180`;
- async and strategy selection:
  `test_async_rotator_benchmark.py:82-121` and
  `test_strategy_performance.py:28-192`;
- pool add/healthy-list operations:
  `test_strategy_performance.py:354-392`;
- cache threshold tests: `test_cache_performance.py:20-165`, L2 10K tests at
  `test_l2_cache_performance.py:49-233`, and cache optimization checks at
  `test_performance_optimizations.py:121-173`;
- storage/index checks: `test_performance_optimizations.py:19-118`.

The current client-pool tests do **not** measure an actual request with reused
versus newly created clients. The pool-operation test does not measure
`pool_snapshot.py` or `_proxy_views`. There is no bounded parser-stream
benchmark. Most cache/storage tests use one manual wall-clock sample rather
than `benchmark.pedantic`, and there is no cache stampede distribution or
storage insert/load/query suite. Therefore the existing tests are useful
threshold smoke, but they do not close task 5.9.

### Exact existing baseline commands

Run on an otherwise idle host, `-n0`, with no live network:

```bash
uv run pytest \
  tests/benchmarks/test_async_rotator_benchmark.py::TestLRUClientPoolBenchmarks \
  --benchmark-only --benchmark-disable-gc --benchmark-warmup=on \
  --benchmark-min-rounds=25 \
  --benchmark-columns=min,median,mean,stddev,ops \
  --benchmark-json=/tmp/proxywhirl-client-pool-baseline.json \
  -q --no-cov -n0

uv run pytest \
  tests/benchmarks/test_async_rotator_benchmark.py::TestAsyncProxySelectionBenchmarks \
  tests/benchmarks/test_strategy_performance.py::TestStrategySelectionBenchmarks \
  --benchmark-only --benchmark-disable-gc --benchmark-warmup=on \
  --benchmark-min-rounds=25 \
  --benchmark-columns=min,median,mean,stddev,ops \
  --benchmark-json=/tmp/proxywhirl-selection-baseline.json \
  -q --no-cov -n0

uv run pytest \
  tests/benchmarks/test_cache_performance.py \
  tests/benchmarks/test_l2_cache_performance.py::TestL2CachePerformance \
  tests/benchmarks/test_performance_optimizations.py::TestCachePerformance \
  -q -s --no-cov -n0

uv run pytest \
  tests/benchmarks/test_performance_optimizations.py::TestDatabaseIndexPerformance::test_healthy_proxies_query_performance \
  --benchmark-only --benchmark-disable-gc --benchmark-warmup=on \
  --benchmark-min-rounds=25 \
  --benchmark-columns=min,median,mean,stddev,ops \
  --benchmark-json=/tmp/proxywhirl-storage-query-baseline.json \
  -q --no-cov -n0
```

The cache command is intentionally not labeled a distribution baseline; its
tests mostly emit or assert single manual timings.

The current wave also ran this broader benchmark/threshold command after
repairing the async benchmark hygiene (`asize`/`ahas_proxy_url` and `aclose`):

```bash
uv run pytest tests/benchmarks/test_cache_performance.py \
  tests/benchmarks/test_performance_optimizations.py \
  tests/benchmarks/test_fetch_performance.py \
  tests/benchmarks/test_async_rotator_benchmark.py \
  tests/benchmarks/test_strategy_performance.py \
  -q --no-cov -n0 -W error::RuntimeWarning --durations=20
# 49 passed, 3 failed
```

All three failures were wall-clock thresholds under concurrent system load,
not correctness/resource failures:

- `TestConcurrentAsyncThroughputStress::test_concurrent_get_proxy_throughput_1000`:
  5.662 seconds versus a 2-second threshold;
- `TestConcurrentAsyncThroughputStress::test_concurrent_get_proxy_throughput_10k`:
  14.704 seconds versus a 10-second threshold;
- `TestConcurrentAsyncThroughputStress::test_batched_concurrent_throughput`:
  132.432 milliseconds versus a 100-millisecond threshold.

Three isolated reruns of the 1,000-operation node passed. The earlier run's
fatal `RuntimeWarning` in
`TestBatchValidationPerformance::test_parallel_batch_validation_setup` was
repaired and its focused rerun passed. This is useful benchmark-hygiene
evidence, but it is **not** a performance baseline and no optimization is
accepted from it. Re-run the exact command on an idle host before interpreting
the three thresholds.

### Implemented benchmark contract and exact command

The subsequent benchmark leaf added
`tests/benchmarks/test_modernization_baselines.py` with these exact nodes:

- `TestRequestClientReuse::test_sync_reused_vs_fresh_client`
- `TestRequestClientReuse::test_async_reused_vs_fresh_client`
- `TestPoolSnapshot::test_snapshot_10_100_1000_10000`
- `TestParserStreaming::test_bounded_stream_1mib_16mib`
- `TestCachePaths::test_l1_hit_l2_hit_miss_and_stampede`
- `TestStorageOperations::test_insert_load_and_indexed_query`

It uses `httpx.MockTransport`, fixed proxy sets and payload bytes,
`benchmark.pedantic` with 25 rounds, `tmp_path` for cache/SQLite, tracemalloc
peak-memory enforcement for parser streaming, and explicit client/task/thread/
stream/connection counts before and after. It never benchmarks a live source.

```bash
uv run pytest \
  tests/benchmarks/test_modernization_baselines.py::TestRequestClientReuse \
  tests/benchmarks/test_modernization_baselines.py::TestPoolSnapshot \
  tests/benchmarks/test_modernization_baselines.py::TestParserStreaming \
  tests/benchmarks/test_modernization_baselines.py::TestCachePaths \
  tests/benchmarks/test_modernization_baselines.py::TestStorageOperations \
  --benchmark-only --benchmark-disable-gc --benchmark-warmup=on \
  --benchmark-min-rounds=25 \
  --benchmark-columns=min,median,mean,stddev,ops \
  --benchmark-json=/tmp/proxywhirl-modernization-baseline.json \
  -q --no-cov -n0
```

The final fatal-`RuntimeWarning` JSON run passed all six nodes with exactly 25
measured rounds each. Host medians were 109.042 µs (sync HTTP pair), 243.292 µs
(async HTTP pair), 31.7041 ms (all pool sizes), 5.2173 ms (both parser sizes),
8.5165 ms (cache paths), and 27.0405 ms (storage operations). The JSON had six
unique full names and nonempty ownership metadata, then was removed with its
temporary directory. These are host distributions, not portable latency
thresholds. Accept an optimization only when its median improves repeatably
beyond run noise, p95/maximum and peak memory do not regress materially,
contracts remain green, and the resource inventory remains balanced. The
current wave accepted no timing-noise optimization.

## Reproduction and validation

### Exact evidence commands and observed results

```bash
git rev-parse --abbrev-ref HEAD
# main
git rev-parse HEAD
# 040fa6a001097bf21828687439a3ba206066a08c
git rev-list --count HEAD
# 278
git log --reverse --format=%cI -1
# 2026-05-15T04:30:18-04:00
git log -1 --format=%cI
# 2026-07-04T21:13:57-04:00
```

Resource constructor scan:

```bash
rg -n --glob '*.py' --glob '!tests/**' \
  'httpx\.(AsyncClient|Client)|\.stream\(|StreamingResponse\(|asyncio\.(create_task|gather|shield|to_thread|Queue|Lock|Semaphore|Event)|threading\.(Thread|Timer|Lock|RLock|Event)|ThreadPoolExecutor|Process\(|create_async_engine|AsyncSession\(|sqlite3\.connect' \
  proxywhirl
```

Tool-availability result:

```bash
uv run python - <<'PY'
import importlib.util
for name in ("radon", "networkx", "pydeps", "grimp"):
    print(f"{name}={bool(importlib.util.find_spec(name))}")
PY
# radon=False
# networkx=False
# pydeps=False
# grimp=False
```

The standard-library AST graph scan observed:

```text
modules=142
internal_import_edges=246
nontrivial_strongly_connected_components=3
```

The benchmark-node proof was read-only:

```bash
uv run pytest --collect-only -q -n0 \
  tests/benchmarks/test_async_rotator_benchmark.py::TestLRUClientPoolBenchmarks \
  tests/benchmarks/test_async_rotator_benchmark.py::TestAsyncProxySelectionBenchmarks \
  tests/benchmarks/test_strategy_performance.py::TestStrategySelectionBenchmarks \
  tests/benchmarks/test_strategy_performance.py::TestPoolOperationBenchmarks \
  tests/benchmarks/test_cache_performance.py \
  tests/benchmarks/test_l2_cache_performance.py::TestL2CachePerformance \
  tests/benchmarks/test_performance_optimizations.py::TestCachePerformance \
  tests/benchmarks/test_performance_optimizations.py::TestDatabaseIndexPerformance
# 29 tests collected in 0.53s
```

The measured CLI coverage command/result was:

```bash
uv run pytest tests/unit/test_cli.py tests/unit/test_cli_coverage.py \
  -q -n0 --cov=proxywhirl.cli --cov=proxywhirl.cli_config_templates \
  --cov-report=term-missing --cov-fail-under=0
# 186 passed
# TOTAL: 924 statements, 74 missed, 92% coverage
```

### Artifact validation

Run immediately before accepting this artifact:

```bash
git diff --no-index --check /dev/null \
  openspec/changes/stabilize-proxywhirl-0-4/architecture-modernization-inventory.md
uv run python - <<'PY'
from pathlib import Path

path = Path("openspec/changes/stabilize-proxywhirl-0-4/architecture-modernization-inventory.md")
text = path.read_text()
assert text.endswith("\n")
assert "\t" not in text
assert not any(line.endswith((" ", "\t")) for line in text.splitlines())
for heading in (
    "Resource-ownership cross-check (2.25 / F7.1)",
    "Architecture hotspot measurements (5.1 / M1.1)",
    "Selected release-safe splits and explicit deferrals (5.2)",
    "Benchmark baseline plan (5.9 / M5.1)",
):
    assert heading in text
print(f"validated_lines={len(text.splitlines())}")
PY
git status --short -- \
  openspec/changes/stabilize-proxywhirl-0-4/architecture-modernization-inventory.md
```

Final status snapshot (the digest is of the entire expanded porcelain stream,
not only this artifact):

```bash
git status --porcelain=v1 -uall | wc -l
# 451
git status --porcelain=v1 -uall | shasum -a 256
# f6527a5ee27176838ec070c279c4280ca35049d88ab9c1c4d9b9c9894c1cc870  -
```

These values are the final inventory read at `2026-08-13T03:05:54-04:00`.
Other authorized writers were active, so a changed overall status digest after
handoff does not invalidate the artifact; it means the consumer must re-run
the same command before using it as a release-candidate freeze.
