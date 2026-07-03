# R-006: Async Rotator Teardown Paths (`proxywhirl/rotator/async_.py`)

Preliminary read-only pass (finalized against fresh coverage data in F-013):

- `AsyncProxyWhirl` as an async context manager: `__aenter__`/`__aexit__` client-pool cleanup.
- Explicit `close()`/`_close_all_clients()` idempotency (calling teardown twice should not raise).
- Cancellation during an in-flight request: ensure the underlying httpx client is still closed on
  cancellation.
- Background aggregation thread shutdown (`_stop_event`, `_aggregation_thread.join`) on teardown.

See F-013 for concrete tests added against current coverage gaps.
