# Tests Agent Guidelines

> Extends: [../AGENTS.md](../AGENTS.md)

## Structure

| Dir | Purpose | Command | Status |
|-----|---------|---------|--------|
| `unit/` | Unit tests | `make test-unit` | ✅ |
| `integration/` | Integration tests | `make test-integration` | ⚠️ partial |
| `property/` | Hypothesis tests | `make test-property` | ✅ |
| `benchmarks/` | Performance | `make test-benchmark` | ✅ |
| `contract/` | API contract tests | `uv run pytest tests/contract/ -v` | ⚠️ partial |

## Markers

`@pytest.mark.slow` (>5s), `@pytest.mark.integration`, `@pytest.mark.network`, `@pytest.mark.benchmark`, `@pytest.mark.snapshot`, `@pytest.mark.flaky`

## Key Fixtures (conftest.py)

| Fixture | Purpose |
|---------|---------|
| `faker` | Faker instance |
| `sample_proxy` / `sample_healthy_proxy` | `Proxy` instances |
| `sample_proxy_pool` / `sample_healthy_pool` | `ProxyPool` instances |
| `respx_mock` / `respx_mock_async` | HTTP mocking |
| `httpx_client` / `async_httpx_client` | HTTP clients |

## Factories (Polyfactory)

```python
from tests.conftest import ProxyFactory, ProxyPoolFactory
proxy = ProxyFactory.build()      # Random
healthy = ProxyFactory.healthy()  # Healthy
```

## Patterns

- **Async:** No decorator needed (`asyncio_mode=auto`)
- **Mock HTTP:** `respx_mock` fixture or `@respx.mock`
- **Property:** `@given(st.integers())` from hypothesis
- **Snapshots:** `snapshot` fixture, `snapshot_json` for JSON

## Boundaries

**Always:** Test-first, use fixtures, mark appropriately, mock HTTP with respx

**Never:** Skip without reason, hardcode URLs, real network in unit tests, commit failing
