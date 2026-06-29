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

## Consequences

- **Positive**: Explicit opt-in failover; API and library share one code path.
- **Negative**: Additional orchestration layer; tests must cover enabled/disabled modes.

## References

- `proxywhirl/orchestration.py`
- `proxywhirl/rotator/sync.py`, `proxywhirl/rotator/async_.py`
- `proxywhirl/api/routes/proxies.py`
- `tests/integration/test_true_failover.py`, `tests/integration/test_failover_legacy.py`