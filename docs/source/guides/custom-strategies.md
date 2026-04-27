# Creating Custom Rotation Strategies

ProxyWhirl ships with several built-in strategies (`round-robin`, `least-connections`, `weighted-response-time`, `random`, `health-aware`). When these do not fit your traffic pattern, you can implement a custom strategy using the `RotationStrategy` protocol.

## The `RotationStrategy` Protocol

A valid strategy must implement three methods:

```python
from typing import Protocol
from proxywhirl.models import ProxyPool, SelectionContext

class RotationStrategy(Protocol):
    def select(self, pool: ProxyPool, context: SelectionContext) -> str:
        ...

    def register(self, proxy_id: str) -> None:
        ...

    def deregister(self, proxy_id: str) -> None:
        ...
```

- `select(pool, context)` — Chooses a proxy ID from the pool. Called on every request.
- `register(proxy_id)` — Notifies the strategy that a new proxy is available.
- `deregister(proxy_id)` — Notifies the strategy that a proxy was removed.

## Example: Sticky-Session Strategy

The following strategy routes the same user to the same proxy for a configurable duration, then rebalances.

```python
import time
from proxywhirl import RotationStrategy, ProxyPool, SelectionContext

class StickySessionStrategy:
    def __init__(self, sticky_ttl_seconds: float = 300.0):
        self.ttl = sticky_ttl_seconds
        self._sessions: dict[str, tuple[str, float]] = {}

    def select(self, pool: ProxyPool, context: SelectionContext) -> str:
        # context.request_id is a stable identifier (e.g., user_id)
        req_id = context.request_id or "default"
        now = time.time()

        cached = self._sessions.get(req_id)
        if cached:
            proxy_id, expires = cached
            if now < expires and proxy_id in pool.available_ids:
                return proxy_id

        # Fallback to round-robin for new or expired sessions
        chosen = pool.next_round_robin()
        self._sessions[req_id] = (chosen, now + self.ttl)
        return chosen

    def register(self, proxy_id: str) -> None:
        pass

    def deregister(self, proxy_id: str) -> None:
        # Clean up any sticky mappings pointing to the removed proxy
        expired = [
            req_id for req_id, (pid, _) in self._sessions.items()
            if pid == proxy_id
        ]
        for req_id in expired:
            del self._sessions[req_id]
```

## Registering Your Strategy

After implementing the protocol, register the strategy under a short name so it can be referenced by string in `ProxyWhirl` or `AsyncProxyWhirl` constructors.

```python
from proxywhirl import StrategyRegistry

StrategyRegistry.register("sticky", StickySessionStrategy)

# Now use it anywhere
rotator = ProxyWhirl(strategy="sticky")
```

## Thread Safety

`select()` is called on the hot path. Keep it fast and lock-free if possible. `register()` and `deregister()` are called less frequently (on proxy pool updates) and can safely use locks.

## Testing Custom Strategies

ProxyWhirl’s test helpers include a mock `ProxyPool` for unit-testing strategies without a real proxy list.

```python
from proxywhirl.testing import MockProxyPool

pool = MockProxyPool(["p1", "p2", "p3"])
ctx = SelectionContext(request_id="user-42")

strategy = StickySessionStrategy()
assert strategy.select(pool, ctx) == "p1"
assert strategy.select(pool, ctx) == "p1"  # Sticky!
```

## Summary

| Step | Action |
|------|--------|
| 1 | Implement `RotationStrategy` protocol |
| 2 | Handle `register` / `deregister` lifecycle events |
| 3 | Register with `StrategyRegistry.register(name, cls)` |
| 4 | Instantiate rotator with `strategy="name"` |
