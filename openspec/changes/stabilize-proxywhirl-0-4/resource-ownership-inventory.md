# Runtime Resource Ownership Inventory

This is the F7.1 ownership map for the live `0.4.0rc1` candidate. It records
resource creation, reuse, closure, cancellation, exception, and idempotence
boundaries; it does not authorize release operations or claim that the residual
risks below are fixed.

## Snapshot and method

- Snapshot: branch `main`, HEAD baseline
  `040fa6a001097bf21828687439a3ba206066a08c`, plus the concurrent uncommitted
  stabilization fixes present in the live working tree at the final 2026-08-13
  scan.
- Scope: runtime Python under `proxywhirl/`, including REST, MCP, CLI, cache,
  storage, migrations, fetchers, browser rendering, rotators, strategies, and
  offline database readers.
- Exclusions: tests, generated/vendor/build output, tooling-only one-line legacy
  shims, and protected-name files. No network call or live browser was used.
- Narrow static scans found exactly 21 `httpx.Client` / `httpx.AsyncClient`
  construction sites, seven explicit `asyncio.create_task` sites, five explicit
  thread/timer sites, three bounded queue sites, 45 lock construction or
  file-lock acquisition sites, four engine factory sites, 19 `AsyncSession`
  contexts, and nine raw `sqlite3.connect` construction sites. The tables below
  reconcile those sites by owner rather than treating repeated per-operation
  context managers as separate architectural owners.
- An optional injected `httpx.AsyncClient` in `sources.validate_source` is
  borrowed: the caller remains its owner and `validate_source` does not close it.

## HTTP clients

| Construction sites | Creator and reuse scope | Closer and failure semantics | Evidence and residual risk |
| --- | --- | --- | --- |
| `proxywhirl/rotator/sync.py`: `ProxyWhirl.__enter__`, `ProxyWhirl._get_or_create_client` (2) | `ProxyWhirl` owns one context-lifetime primary client and an `LRUClientPool` of at most 100 per-proxy clients. Requests reuse the per-proxy pool; concurrent same-key creators converge through `put_if_absent`. | `ProxyWhirl.close` clears the primary reference, closes it, cancels aggregation, and calls `LRUClientPool.clear`; removal and eviction close individual clients. Repeated close is safe and client-close errors are logged while cleanup continues. | `tests/unit/test_rotator.py`, `tests/unit/test_resource_limits.py`, and `tests/unit/test_runtime_lifecycle_wave3.py` cover context cleanup, eviction/removal, reuse, and the same-key race. The primary context client is created and closed but per-proxy traffic uses the pool. |
| `proxywhirl/rotator/async_.py`: `AsyncProxyWhirl.__aenter__`, `check_proxies_health`, `_get_or_create_client` (3) | `AsyncProxyWhirl` owns one context-lifetime primary client and a 100-entry `LRUAsyncClientPool`; a health-check client is operation-scoped per proxy. Pool publication is serialized by its `asyncio.Lock`. | `aclose` clears references, awaits the primary client and every pooled client, records the first cleanup error, cancels/joins aggregation, and is repeatable. Health-check clients use `async with`. Cancellation during pool clearing is retained until all snapshotted clients receive a close attempt. | `tests/unit/test_async_teardown.py`, `tests/unit/test_async_context_manager.py`, and `tests/unit/test_runtime_lifecycle_wave3.py` cover normal, cancelled, repeated, and racing shutdown paths. |
| `proxywhirl/fetchers/fetcher.py`: `ProxyFetcher._get_client` (1) | `ProxyFetcher` lazily owns one shared direct-fetch `AsyncClient`; repeated static-source fetches reuse it. Its validator is either injected or created by the fetcher, but current `close` treats either form as lifecycle-owned. | `ProxyFetcher.close` snapshots and clears the client, stops the refresh task, closes the client and validator concurrently, shields cleanup from caller cancellation, then re-raises cancellation or a cleanup error after cleanup settles. | `tests/unit/test_fetchers.py`, `tests/unit/test_sources.py`, and `tests/unit/test_runtime_lifecycle_wave3.py` cover client/validator closure and cancellation. Residual contract ambiguity: an injected validator is closed by the fetcher even though injection normally implies borrowed ownership. |
| `proxywhirl/fetchers/validator.py`: `_get_client`, `_get_socks_client`, `_validate_http_request`, `check_anonymity`, two protocol branches in `validate`, and `validate_https_capability_batch` (7) | `ProxyValidator` lazily owns one shared direct client and an LRU of hash-keyed clients per exact SOCKS URL, capped at `min(concurrency, 100)`. The other five sites are operation-scoped proxy clients. Batch work is concurrency-bounded with semaphores. | `_socks_client_lock` serializes lookup/publication; eviction awaits the least-recent client's close. `close` snapshots and clears all shared/SOCKS clients, deduplicates the compatibility `_socks_client`, closes every client with `gather`, and shields cleanup from external cancellation. All operation clients use `async with`. Raw async TCP writers are closed and `wait_closed` is awaited after successful connect. | `tests/unit/test_validator_client_pool.py`, `tests/unit/test_outbound_boundaries.py`, `tests/unit/test_fetchers.py`, and `tests/unit/test_tcp_validation.py` cover lazy reuse, URL isolation, bounded LRU eviction/closure, context cleanup, repeated close, and TCP closure. |
| `proxywhirl/sources.py`: `validate_source`, `validate_sources` (2) | A standalone validation attempt owns its client when no client is injected. Batch validation owns one shared client reused across every source under a bounded semaphore. | Both owned forms use `async with`; response streams also use `async with`. Timeout, HTTP error, retry, gather failure, and cancellation leave the client context before propagating. | `tests/unit/test_sources.py` covers standalone/shared behavior and source-fetcher cleanup. `validate_sources` waits for the whole gathered batch; there is no detached work. |
| `proxywhirl/api/routes/proxies.py`: `_check_proxy_health` (1) | One operation-scoped `AsyncClient` is created per selected proxy; `health_check_proxies` bounds concurrent owners with `APISettings.health_check_concurrency`. | Nested client and response-stream context managers close on success, exception, and cancellation. All gathered checks are awaited by the request. | `tests/unit/test_api_security_wave1.py` proves the streaming path and sanitized failure result. |
| `proxywhirl/mcp/server.py`: `_validate_proxy_impl` (1) | The MCP validation action creates one operation-scoped client for each proxy and processes proxies serially. | `async with` closes each client before the next proxy or return. Exceptions become sanitized per-proxy results. | `tests/unit/test_mcp_server.py` and `tests/unit/test_mcp_coverage_wave4.py` cover validation, auth, sanitization, lifespan, storage closure, and awaited context logging. |
| `proxywhirl/cli/_impl.py`: request retry loop, pool `test`, health loop (3) | Each retry, one-shot pool test, or per-proxy health check owns a synchronous client for exactly one request. | Every site uses `with httpx.Client`, so normal return and exceptions close the client before output/next iteration. | `tests/unit/test_cli.py` covers retries, pool testing, health, and redacted failures. Continuous health intentionally repeats construction rather than retaining a cross-iteration client. |
| `proxywhirl/geo.py`: `batch_geolocate` (1) | One operation-scoped `AsyncClient` is reused for all chunks in a geolocation batch. | `async with` closes it after all chunks or on the first propagated exception/cancellation. | `tests/unit/test_geo.py` covers batching/cache behavior. There is no package-global HTTP client. |

The 2 + 3 + 1 + 7 + 2 + 1 + 1 + 3 + 1 grouping above accounts for all 21
constructor sites.

## Browser and stream ownership

| Resource | Creator / reuser | Closer / cancellation behavior | Tests and residual risk |
| --- | --- | --- | --- |
| Playwright driver, browser, pooled contexts, pages | `proxywhirl/browser.py:BrowserRenderer.start` owns the driver, one browser, and `max_contexts` reusable contexts in a bounded `asyncio.Queue`. `render` borrows one context and owns one page. `ProxyFetcher.fetch_from_source` scopes a renderer with `async with`. | One stable `_pool_lock` serializes full startup publication, start-versus-close, resource detachment, lease registration, and release. Partial startup snapshots and drains its graph. `render` uses a finite acquisition deadline, closes its page in `finally`, and returns the context; page-close cancellation is preserved after release. `close` detaches under the lock, drains all contexts/browser/driver through a shielded cleanup task, and is repeatable. Leased identity makes duplicate/foreign release fail fast. | `tests/unit/test_browser_renderer.py`, `tests/integration/test_browser_fetching.py`, and `tests/test_browser_failures.py` cover concurrent starts, start-versus-close, partial startup, cancellation, normal/repeated close, rendering failure, context release, duplicate-release rejection, and pool exhaustion. **Compatibility residual:** direct manual `acquire_context()` still permits `timeout=None`; normal `render` never uses that unbounded form. |
| Bounded upstream sync response | `proxywhirl/rotator/sync.py:_request_with_bounded_response` owns the streamed `httpx.Response` returned by `client.send(stream=True)` while copying at most the configured byte cap. | A `finally` always calls `streamed_response.close`, including iterator failure or truncation. It returns a new buffered response that the caller owns. | `tests/unit/test_api_security_wave1.py` proves early truncation and stream closure. |
| Static source and source-validation streams | `ProxyFetcher._fetch_static_content` and `sources._fetch_validation_content` own response contexts from a borrowed/shared client. `fetchers.parsers._read_bounded_response_text` and `sources._read_validation_content` borrow the already-open response while consuming bounded chunks. | The enclosing `async with client.stream` closes at each response/redirect hop. Consumer helpers do not close a borrowed response themselves. | Source/fetcher and streaming-parser suites cover byte caps, redirect/error paths, and parsing. |
| REST proxy-health response stream | `_check_proxy_health` owns both the operation client and `client.stream` response. | Nested async context exit closes both before the `HealthCheckResult` is returned. | `tests/unit/test_api_security_wave1.py::test_proxy_health_check_streams_without_buffering`. |
| ASGI request-body stream | `proxywhirl/api/middleware/body_limit.py:RequestBodyLimitMiddleware` borrows server-owned `receive`/`send` callables and wraps them for one request. | No independent handle is created. It stops consuming immediately after the byte limit and lets the ASGI server own disconnect/cancellation cleanup. | `tests/unit/test_api_security_wave1.py` covers early stop and the full middleware stack. |
| REST NDJSON/CSV/text/metrics generators | `proxywhirl/api/routes/proxies.py`, `proxywhirl/api/routes/health.py`, and `proxywhirl/api/streaming.py` create request-scoped async generators over in-memory snapshots. Starlette's `StreamingResponse` owns iteration. | Generator completion or request cancellation ends the request-owned iterator; these generators hold no HTTP client, file, browser, or database connection. Serialization failures skip one row where documented. | `tests/unit/test_api_streaming_coverage.py` and API streaming tests cover output and row-local failures. Residual performance note: proxy lists are snapshotted before streaming, so the wire is streamed but source data is already buffered. |

## Tasks, threads, timers, events, semaphores, and queues

### Explicit tasks and gathered children

| Owner / site | Lifetime and settlement | Evidence / residual risk |
| --- | --- | --- |
| `RequestOrchestration._select_initial_proxy_async` and `_rotate_proxy_async` (2 explicit tasks) | Each wraps one `asyncio.to_thread` selection. The caller awaits it through `shield`; cancellation waits for selection to finish, settles any selected proxy exactly once, and re-raises cancellation. | Request-lifecycle and `tests/unit/test_runtime_lifecycle_wave3.py` cover cancellation during offloaded selection. |
| `BrowserRenderer.close` (1 explicit cleanup task) | Created only to shield aggregate browser cleanup. It is always awaited; external cancellation waits for cleanup and is then re-raised. | Browser renderer close/cancellation tests. |
| `ProxyFetcher.close` (1 cleanup task) and `start_periodic_refresh` (1 retained task) | Cleanup task is always awaited under shield. The refresh task is retained in `_refresh_task`; `stop_periodic_refresh` sets its event, cancels, awaits, and clears it. `close` detects self-close to avoid awaiting the current refresh task. | Fetcher and runtime lifecycle tests cover cancellation and repeated close. `start_periodic_refresh` creates and directly awaits the retained loop, so its caller owns the foreground wait while `stop_periodic_refresh` owns cancellation. |
| `ProxyValidator.close` (1 explicit cleanup task) | It is always awaited through `shield`, waits for all snapshotted clients, and only then propagates cancellation/errors. | Validator pool tests cover multiple close calls and recreation. |
| `HealthMonitor.start` (1 retained task) | The monitor retains `_task`; idempotent `start` prevents duplicates. `stop` cancels and awaits the task, translates background failure, and clears state in `finally`. Each cycle scopes its validator with `async with`. | `tests/unit/test_health_monitor.py` covers cancellation, idempotent start/stop, and pool updates. |
| Request-scoped gathered work | Fetcher source work, both validator batches, source validation, API health checks, async rotator health checks, health-monitor checks, enrichment, and proxy-view snapshots are all awaited in their caller. Validator/source/API/monitor batches use semaphores where network or validator ownership needs a cap. | Cancellation propagates through `gather`; there are no retained tasks after return. **Residual:** except for the fixed two-child proxy-view snapshot, batch helpers construct one gather child per input. Semaphores bound active I/O where present but not scheduled child count, so extremely large caller-supplied batches can create high task pressure. |
| MCP context logging | `_proxywhirl_tool` directly awaits `_async_log`; it no longer creates a fire-and-forget task. | `tests/unit/test_mcp_coverage_wave4.py::test_unified_tool_awaits_context_logging_before_dispatch`. |

The two orchestration tasks plus browser cleanup, fetcher cleanup/refresh,
validator cleanup, and health-monitor work account for all seven explicit
`asyncio.create_task` sites.

### Threads and timers

| Site | Owner and shutdown | Residual risk |
| --- | --- | --- |
| `proxywhirl/cache/manager.py:TTLManager.cleanup_thread` | `TTLManager` owns one daemon thread and a stop event. `stop` is repeatable, avoids joining itself, joins for five seconds, clears a stopped thread reference, and warns if still alive. `CacheManager.close` stops it and closes both closeable cache tiers; context exit and destructor delegate to `close`. | If tier cleanup blocks longer than five seconds, shutdown returns with a live daemon thread after an explicit warning. Tests cover deterministic close/context and idempotent start/stop. |
| `ProxyWhirl._aggregation_timer` | Sync rotator starts one daemon `threading.Timer` only on context entry. `_aggregation_lock` serializes publication/clearing; the stop event prevents rescheduling after close. `close` cancels, clears, avoids self-join, and joins an alive timer for at most five seconds. | `tests/unit/test_rotator_coverage.py` covers joining a running timer and the self-close path. The explicit five-second bound prevents shutdown from waiting forever; an over-bound callback remains daemonized. |
| `AsyncProxyWhirl._aggregation_timer` / compatibility `_aggregation_thread` | Async rotator starts one daemon timer on async context entry. `_aggregation_lock` serializes publication/clearing; `aclose` sets the stop event, cancels the timer, avoids self-join, and joins a still-alive timer thread for up to five seconds. | `tests/unit/test_async_teardown.py` covers normal/running joins, self-close, and destructor cancellation. The explicit five-second bound prevents shutdown from waiting forever; an over-bound callback remains daemonized. |
| `rotator._bootstrap._run_async_from_sync` | When invoked inside a running event loop, the call owns one daemon worker thread, starts it, and performs an unbounded `join`; the thread owns its temporary event loop and the call propagates its captured result/error. | **Residual:** a hung bootstrap coroutine hangs the synchronous caller because the join has no timeout or cancellation channel. |
| `security._resolve_hostname_addresses_with_timeout` | A module-global eight-slot `BoundedSemaphore` caps outstanding calls. Each admitted call owns one named daemon worker and a one-result bounded queue. The caller waits only until its deadline; a completed worker is joined briefly, while a timed-out worker deliberately remains daemonized until `getaddrinfo` returns and then releases its slot. | `tests/unit/test_security_hardening.py::test_dns_timeout_returns_promptly_without_non_daemon_worker` proves fail-closed wall-clock return and daemon ownership. The bounded failure mode is capacity exhaustion: at most eight stuck OS calls retain slots, and later callers fail closed on their own admission deadline without blocking process shutdown. |
| `asyncio.to_thread` call sites | The running event loop owns its default executor. Every package call awaits the returned coroutine directly or, for orchestration selection, through the retained tasks described above. | No package-owned executor requires shutdown. Cancellation cannot stop already-running synchronous work; lifecycle-sensitive selection explicitly waits and settles before re-raising. |

### Locks, events, semaphores, and queues

Locks do not require close; their owning object or module defines their state
lifetime. All file locks below use context managers or an explicit CLI context.

| Ownership family | Protected state and release behavior |
| --- | --- |
| Models | `Proxy._window_lock` protects sliding request metrics; `ProxyPool._lock` protects list/index state and async helpers offload lock-taking work. Both are per-instance. |
| Circuit breakers | `CircuitBreaker._lock` and `AsyncCircuitBreaker._lock` serialize state transitions and HALF_OPEN probe reservation per breaker. Sync `with` / async `async with` releases on every exception/cancellation. |
| Strategies | `StrategyState._lock`, `RoundRobinStrategy._lock`, `WeightedStrategy._cache_lock`, `LeastUsedStrategy._lock`, and `SessionManager._lock` are per instance. `StrategyRegistry._lock` protects singleton creation and `_registry_lock` protects its registry. All acquisitions are scoped context managers. |
| Rate limiting | Each `_TokenBucketLimiter` has an `RLock`; `RateLimiter` and `SyncRateLimiter` protect proxy-limiter maps with per-instance `RLock`s. `AsyncRateLimiter` lazily creates an event-loop-specific `asyncio.Lock`, replacing it when reused on another loop. |
| Validator | `ProxyValidator._socks_client_lock` serializes lookup, LRU eviction, publication, and close of the bounded per-URL SOCKS-client pool. Awaited evictions occur inside this lock, so another pool mutation cannot reuse an evicted owner. |
| Rotators and pools | `ProxyWhirl._strategy_lock`, `_bootstrap_lock`, and `_aggregation_lock`; `AsyncProxyWhirl._bootstrap_lock` and `_aggregation_lock`; and the sync/async LRU client-pool locks protect strategy/bootstrap/timer/client publication. All are per rotator or pool. Discarded client publication is atomic, and client close occurs under the pool-specific cleanup contract. |
| Retry metrics | `RetryMetrics._lock` is per metrics object and guards attempt/event retention, aggregate mutation, pruning, and summary snapshots. Every acquisition is a synchronous context manager. |
| Cache | `CacheManager._lock` protects cross-tier operations; `_singleflight_guard` protects the per-key `_LoadFlight` map, and each flight owns a `threading.Event` that is set in `finally`. `JsonlCacheTier._state_lock` protects index/LRU state; bounded `portalocker.Lock` contexts protect shard read/modify/write cycles. `DiskCacheTier._op_lock` and `_conn_lock` serialize use/creation/close of its persistent connection. `SQLiteCacheTier._op_lock` serializes operation-scoped connections. |
| MCP | Module-global `_rotator_lock` serializes lazy global rotator creation, replacement, and cleanup; lifespan and explicit setters use the same lock. |
| Migrations | Module-global `_ALEMBIC_COMMAND_LOCK` protects Alembic's process-global context. A database-URL-hashed `FileLock` also serializes the same database across processes; both are released by nested contexts on success/error. |
| CLI | `utils.CLILock` owns a `FileLock` and PID sidecar for a command context; `__exit__` releases the lock and removes the sidecar. |
| Browser | One stable per-renderer `_pool_lock` serializes startup, close/detach, lease registration, and release. It is never replaced, so lifecycle racers cannot mutate the same browser graph under different locks. |
| Semaphores/events | Operation-scoped semaphores bound API health checks, source validation, both validator batches, and health-monitor checks. A module-lifetime eight-slot `BoundedSemaphore` caps outstanding DNS resolver workers; every worker releases its slot in `finally`, including resolver exceptions. Events belong to fetcher refresh, validator early-stop, both rotator timers, TTL cleanup, and each cache singleflight. Waiters are tied to retained/awaited operations except the deliberately daemonized timed-out DNS work described above. |
| Queues | `ProxyWhirl._request_queue` is a bounded synchronous `queue.Queue` owned for rotator lifetime; all accesses are non-blocking, and `clear_queue` drains it. `BrowserRenderer._context_pool` is a bounded async queue owned from `start` to `close`; normal rendering borrows/returns one context in `finally`. Each DNS resolution owns a one-result `queue.Queue`; the worker publishes either the address set or captured exception with `put_nowait`, and the caller consumes it or leaves it for a timed-out daemon worker to finish. The browser manual API has the blocking residual described above. |

The 45 lock sites reconcile as models (3), circuit breakers (2), retry metrics
(1), strategies (8), rate limiting (4), validator (1), rotators/client pools
(7), cache/file locking (14), MCP (1), migrations (2), CLI (1), and browser
(1). Default-factory sites count once at their declaration; each runtime owner
receives its own lock.

## Database and local-reader ownership

| Resource | Creator / reuse | Closer / exception behavior | Tests and residual risk |
| --- | --- | --- | --- |
| `SQLiteStorage.engine` | `proxywhirl/storage.py:SQLiteStorage.__init__` creates one `AsyncEngine` per storage object and reuses its bounded SQLAlchemy pool. Nineteen `AsyncSession(self.engine)` contexts cover `update_identity`, add/batch, delete/clear/query, validation writes, load variants, cleanup/stats, batch reads, and audit logging. | Every session is an `async with` context and commits/rolls back at its method boundary. Direct engine connections in `initialize` and `_vacuum_database` are also context managed. `SQLiteStorage.close` awaits `engine.dispose`; repeated dispose is safe. API lifespan, MCP cold load, CLI storage helpers, exports, and tests close the owner in `finally`/shutdown paths. | Storage, SQLite, migration, API lifespan, MCP, CLI coverage, and export tests exercise close and concurrency. `SQLiteStorage` has no async context-manager facade, so custom callers must retain and explicitly close it. |
| MCP cold-load storage | `mcp.server.get_rotator` creates a temporary `SQLiteStorage` only when the configured database exists. | A local `finally` now closes it whether initialize/load/add succeeds or fails; close errors are logged by type without exposing details. | `tests/unit/test_mcp_coverage_wave4.py` covers successful and failed load closure. |
| API storage and rotator | `api.core.lifespan` creates optional `SQLiteStorage` and a sync `ProxyWhirl` inside one encompassing `try`. | The `finally` covers failures before and after `yield`, attempts save, then nests rotator close, storage close, and global-state clearing so later cleanup still runs if an earlier step fails. | `tests/unit/test_api_core_additional.py::test_lifespan_closes_storage_when_rotator_startup_fails` plus API lifespan tests. |
| L2 persistent SQLite connection | `cache.tiers.DiskCacheTier._get_connection` lazily creates one `check_same_thread=False` connection per tier and reuses it under `_op_lock`; `_conn_lock` serializes publication/close. | `DiskCacheTier.close` closes and clears it under both locks and is idempotent; destructor delegates to close. `CacheManager.close` invokes the tier closer, marks the manager closed, and every public cache operation calls `_ensure_open`, preventing post-close use from reopening this handle. | Cache tier/manager and concurrency suites cover persistence, parallel writes, deterministic close, context exit, and post-close rejection in `tests/unit/test_cache_manager.py::test_closed_manager_rejects_operations_without_reopening_tiers`. |
| L3 operation-scoped SQLite connections | `SQLiteCacheTier` has eight `closing(sqlite3.connect(...))` sites: schema init, get, put, delete, clear, size, keys, and expiry cleanup. | `contextlib.closing` closes on every return/exception; `_op_lock` serializes operations. There is no persistent connection to close at tier shutdown. | `tests/unit/test_cache_tiers.py` covers all operations, schema repair, health fields, and concurrent access. |
| Migration engines/connections | `migrations.get_current_revision` creates a temporary async engine; packaged Alembic env creates async or sync engines for online migration. | `finally: await engine.dispose()` handles the revision helper. Alembic env connects with a context and disposes the engine after it exits. Locked upgrade/downgrade/stamp work uses Alembic-owned sync connections behind process/file locks. | `tests/unit/test_migrations.py` covers idempotence, serialization, packaged discovery, and thread safety. |
| Operation-scoped GeoIP readers | `proxywhirl/geo.py:_lookup_single_ip_cached` creates one reader per uncached single lookup; `geolocate_with_database` creates one reader for all uncached addresses in a batch. | Both use `with geoip2.database.Reader(...)`, so the MMDB handle closes on return or lookup/open failure. | `tests/unit/test_geo.py` covers local-database selection and missing-database fallback, but has no focused reader-close assertion; the language-level context boundary is explicit. |
| Offline GeoIP readers | `enrichment.AsyncOfflineEnricher` and `OfflineEnricher` each own an optional `geoip2.database.Reader` opened at construction and reused for lookups. | Explicit `close` closes and clears the reader; `is_geoip_available` closes its probe owner. | `tests/unit/test_enrichment.py` covers reader/no-reader closure. **Residual:** neither enricher implements a context manager or destructor, so custom callers that construct one and omit `close` can retain the MMDB file handle. |

## Residual-risk register

These remaining findings do not make the inventory incomplete; they identify
live owners whose contract still merits an explicit follow-up. DNS resolution,
bounded SOCKS reuse, sync/async timer settlement, browser lease identity and
render acquisition, MCP/API cleanup, and cache post-close behavior are reflected
above as implemented controls rather than stale residuals.

| ID | Priority | Exact live risk | Recommended owning follow-up |
| --- | --- | --- | --- |
| RES-F7-02 | Low | The public manual `BrowserRenderer.acquire_context(timeout=None)` compatibility form can wait indefinitely when every context is leased. Normal `render` supplies a finite deadline, and lifecycle/double-release paths are serialized and bounded. | Prefer a finite manual default in the next compatible API revision, or document that expert callers must pass `timeout`. |
| RES-F7-04 | Medium | `_run_async_from_sync` uses an unbounded worker-thread join. | Add an explicit bootstrap deadline/cancellation contract or document deliberate unbounded blocking. |
| RES-F7-05 | Low | Injected `ProxyFetcher.validator` is closed by `ProxyFetcher.close`, while injection otherwise suggests borrowed ownership. | Declare transfer-of-ownership explicitly or track whether the fetcher constructed the validator. |
| RES-F7-06 | Low | Offline enrichers require manual `close`; custom callers have no context-manager safety net. | Add sync/async context facades without changing existing call semantics. |
| RES-F7-07 | Low | Fetcher, validator, source, API/monitor health, enrichment, and async-rotator batches schedule one gather child per input; semaphores bound active I/O in several families but not child allocation. REST “streaming” routes also snapshot the full proxy list first. | Add chunked scheduling and snapshot pagination only with benchmark and contract evidence. |

## F7.1 disposition

Task 2.25 / F7.1 is eligible to check after maintainer/integrator review of this
artifact. Every live material client, browser graph, stream family, explicit or
gather-owned task family, package-owned thread/timer, lock family, semaphore,
event, queue, SQL engine/session/connection family, and local GeoIP reader found
by the scoped scans has an owner and closer disposition above. The residuals are
explicit follow-ups; they must not be read as closure proof or silently waived by
checking the inventory task.
