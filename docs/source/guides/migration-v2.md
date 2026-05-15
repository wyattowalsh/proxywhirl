# Migration Guide: ProxyWhirl v1.x to v2.0

This guide helps you migrate from ProxyWhirl v1.x to v2.0, which removes several deprecated fields and features.

## Breaking Changes

### 1. Proxy Model: `total_requests` Field

**Deprecated in:** v1.8+  
**Removed in:** v2.0

The `total_requests` field on the `Proxy` model is legacy and has been superseded by more granular request tracking.

#### Migration Path

**Before (v1.x):**
```python
from proxywhirl import ProxyWhirl

rotator = ProxyWhirl()
proxy = rotator.get_proxy()
print(f"Total requests: {proxy.total_requests}")
```

**After (v2.0):**
```python
from proxywhirl import ProxyWhirl

rotator = ProxyWhirl()
proxy = rotator.get_proxy()

# Use granular request tracking instead:
print(f"Completed requests: {proxy.requests_completed}")
print(f"Started requests: {proxy.requests_started}")
print(f"Active requests: {proxy.requests_active}")
print(f"Success rate: {proxy.total_successes / max(proxy.requests_completed, 1)}")
```

**Why the change?**  
The granular request tracking provides better visibility into proxy state (started, in-flight, completed) enabling smarter selection strategies.

---

### 2. Proxy Model: `ema_alpha` Field

**Deprecated in:** v1.8+  
**Removed in:** v2.0

The per-proxy `ema_alpha` field is no longer used. EMA alpha configuration is now handled at the strategy level via `StrategyConfig.ema_alpha`.

#### Migration Path

**Before (v1.x):**
```python
from proxywhirl import Proxy

proxy = Proxy(host="proxy.example.com", port=8080)
proxy.ema_alpha = 0.3  # Set per-proxy EMA smoothing factor
```

**After (v2.0):**
```python
from proxywhirl import ProxyWhirl, StrategyConfig, RotationStrategy
from proxywhirl.strategies import PerformanceBasedStrategy

config = StrategyConfig(ema_alpha=0.3)
strategy = PerformanceBasedStrategy(config=config)
rotator = ProxyWhirl(strategy=strategy)
```

**Why the change?**  
EMA configuration is strategy-specific, not proxy-specific. Strategies manage their own `StrategyState` with independent alpha values per proxy.

---

## Compatibility Layer (v1.x)

In ProxyWhirl v1.x, these fields remain present but are marked for deprecation:

```python
# Still works in v1.x, but shows deprecation warning
proxy.total_requests  # DeprecationWarning
proxy.ema_alpha       # DeprecationWarning
```

To prepare your code now:

1. **Audit your codebase:**
   ```bash
   grep -r "\.total_requests" .
   grep -r "\.ema_alpha" .
   ```

2. **Replace usages:**
   - `total_requests` → `requests_completed`
   - `ema_alpha` assignments → `StrategyConfig.ema_alpha` in strategy initialization

3. **Test thoroughly** with both old and new approaches during the transition

---

## Removed Features

### `quality-dead-code-deprecated-endpoints`

All `/api/v0/*` API endpoints have been removed. Use `/api/*` exclusively:

**Removed:**
- `GET /api/v0/proxies`
- `POST /api/v0/proxies/validate`
- All other v0 endpoints

**Migration:**  
Update all API client code to use `/api/` routes instead.

---

## Timeline

| Version | Status | Details |
|---------|--------|---------|
| v1.8.x | **Current** | Deprecation warnings added for `total_requests`, `ema_alpha`, v0 API endpoints removed |
| v1.9.x | **Planned** | Fields remain but inaccessible via type hints (runtime compatible) |
| v2.0 | **Next Major** | Fields removed entirely; API v0 gone; requires code updates |

---

## Getting Help

- **Questions?** Open an issue: https://github.com/wyattowalsh/proxywhirl/issues
- **Still on v1.7?** See the older migration guide in the repo history
- **Need gradual migration?** Stay on v1.8.x while updating your code, then upgrade to v2.0

---

## Summary Checklist

- [ ] Audit code for `proxy.total_requests` usage
- [ ] Audit code for `proxy.ema_alpha` usage
- [ ] Replace `total_requests` with `requests_completed`
- [ ] Move EMA config to `StrategyConfig`
- [ ] Update all `/api/v0/` calls to `/api/`
- [ ] Run test suite to verify compatibility
- [ ] Deploy to staging and verify behavior
