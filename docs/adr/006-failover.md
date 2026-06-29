# ADR-006: Cross-Proxy Failover Orchestration

## Status

Accepted

## Context

Inner `RetryExecutor` retries against a single selected proxy. Users also need optional
**outer** rotation to a different proxy when inner retries are exhausted, without breaking
existing single-proxy behavior.

## Decision

- Introduce `proxywhirl/orchestration.py` with `FailoverPolicy` and `RequestOrchestration`.
- **`FailoverPolicy.enabled=False` by default** preserves legacy inner-retry-only semantics.
- When enabled, an outer loop selects the next proxy via `RetryExecutor.select_retry_proxy`
  (or strategy fallback), excluding failed proxy IDs through `SelectionContext`.
- Sync and async rotators delegate `_make_request` to `RequestOrchestration`; the FastAPI
  `/api/request` endpoint calls `rotator._make_request` via `asyncio.to_thread`.
- Proxies without circuit breaker entries remain selectable (`_should_use_circuit_breaker`).
- **Rate limits are non-failover signals**: `RateLimitExceededError` propagates without outer
  rotation; only connection-level exhaustion triggers proxy failover.
- **Queued sync requests pin the enqueued proxy** via `pinned_proxy` so dequeue does not
  re-select a different proxy when failover is enabled.
- **Default outer round cap** uses the count of eligible proxies at request start (non-expired,
  circuit-available), not raw pool size, unless `max_proxy_attempts` is set explicitly.
- **Async parity**: `AsyncProxyWhirl` accepts `proxy_rotation_callback` like sync `ProxyWhirl`.

## Consequences

- **Positive**: Explicit opt-in failover; API and library share one code path.
- **Negative**: Additional orchestration layer; tests must cover enabled/disabled modes.

## References

- `proxywhirl/orchestration.py`
- `proxywhirl/rotator/sync.py`, `proxywhirl/rotator/async_.py`
- `proxywhirl/api/routes/proxies.py`
- `tests/integration/test_true_failover.py`, `tests/integration/test_failover_legacy.py`