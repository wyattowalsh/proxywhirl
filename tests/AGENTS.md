# Tests Agent Guidelines

> Extends: [../AGENTS.md](../AGENTS.md)

## Structure

| Dir | Purpose | Command |
|-----|---------|---------|
| `unit/` | Unit tests | `make test-unit` |
| `integration/` | Integration tests | `make test-integration` |
| `property/` | Hypothesis tests | `make test-property` |
| `benchmarks/` | Performance | `make test-benchmark` |
| `contract/` | API contract tests | `uv run pytest tests/contract/ -v` |

## Markers

| Marker | Purpose | Usage |
|--------|---------|-------|
| `@pytest.mark.slow` | Tests >5s | `-m "not slow"` |
| `@pytest.mark.integration` | External deps | `-m integration` |
| `@pytest.mark.network` | Network required | `-m "not network"` |
| `@pytest.mark.benchmark` | Performance | `--benchmark-only` |
| `@pytest.mark.snapshot` | Snapshot tests | `--snapshot-update` |
| `@pytest.mark.flaky` | Known flaky | Auto-rerun in CI |

## Fixtures (conftest.py)

| Fixture | Purpose |
|---------|---------|
| `faker` | Faker instance for test data |
| `sample_proxy` | Single `Proxy` instance |
| `sample_healthy_proxy` | Healthy proxy with good stats |
| `sample_proxy_pool` | `ProxyPool` with test proxies |
| `sample_healthy_pool` | Pool with all healthy proxies |
| `respx_mock` | HTTP mocking (sync) |
| `respx_mock_async` | HTTP mocking (async) |
| `httpx_client` | Sync HTTP client |
| `async_httpx_client` | Async HTTP client |
| `sample_retry_policy` | `RetryPolicy` instance |
| `sample_circuit_breaker` | `CircuitBreaker` instance |

## Factories (Polyfactory)

```python
from tests.conftest import ProxyFactory, ProxyPoolFactory

proxy = ProxyFactory.build()  # Random proxy
healthy = ProxyFactory.healthy()  # Healthy proxy
pool = ProxyPoolFactory.build()  # Random pool
```

## Patterns

- **Async:** No decorator needed (`asyncio_mode=auto`)
- **Mock HTTP:** Use `respx_mock` fixture or `@respx.mock` decorator
- **Property tests:** `@given(st.integers())` from hypothesis
- **Benchmarks:** `benchmark` fixture param
- **Snapshots:** `snapshot` fixture with `snapshot_json` for JSON

## Boundaries

**Always:**
- Write tests BEFORE implementation
- Use fixtures for common setup
- Mark tests with appropriate markers
- Clean up resources with `yield`
- Test edge cases and error paths
- Mock all external HTTP calls with `respx`

**Ask First:**
- New test markers
- Fixture scope changes
- Modifications to `conftest.py`
- Adding new test dependencies

**Never:**
- Skip tests without documenting reason
- Remove tests without replacement
- Hardcode external URLs
- Make real network calls in unit tests
- Commit failing tests
