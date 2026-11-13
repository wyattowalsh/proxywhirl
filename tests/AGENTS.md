# Tests Agent Guidelines

> Extends: [../AGENTS.md](../AGENTS.md)

## Structure

| Dir | Purpose | Command | Status |
|-----|---------|---------|--------|
| `unit/` | Unit tests | `just test-unit` | ✅ |
| `integration/` | Integration tests | `just test-integration` | ⚠️ partial |
| `property/` | Hypothesis tests | `uv run pytest tests/property/ -v` | ✅ |
| `benchmarks/` | Performance | `uv run pytest tests/benchmarks/ -v --benchmark-only` | ✅ |
| `api/` | OpenAPI + HTTP surface | `uv run pytest tests/api/ -v` | ✅ |
| `contract/` | API contract tests | `uv run pytest tests/contract/ -m "not network" -v` | ✅ |

## Markers

`@pytest.mark.slow` (>5s), `@pytest.mark.integration`, `@pytest.mark.network`, `@pytest.mark.benchmark`, `@pytest.mark.snapshot`, `@pytest.mark.flaky` (pytest-rerunfailures `reruns=N`)

CI fast gate (`just test-fast`): `tests/ --ignore=tests/benchmarks` with `-m "not slow and not stress and not network"`.

## Key Fixtures (conftest.py)

| Fixture | Purpose |
|---------|---------|
| `faker` | Faker instance |
| `sample_proxy` / `sample_healthy_proxy` | `Proxy` instances |
| `sample_proxy_pool` / `sample_healthy_pool` | `ProxyPool` instances |
| `respx_mock` / `respx_mock_async` | HTTP mocking (lenient) |
| `respx_mock_strict` | HTTP mocking (`assert_all_called=True`) |
| `async_api_client` / `api_test_rotator` | FastAPI ASGI integration |
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
