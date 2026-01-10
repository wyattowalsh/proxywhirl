# Test Suite Agent Guidelines

> Extends: [../AGENTS.md](../AGENTS.md)

Agent guidelines for the proxywhirl test suite.

## Overview

Comprehensive test coverage using pytest with async support, property-based testing, benchmarks, and snapshot testing.

## Directory Structure

| Directory | Purpose | Run Command |
|-----------|---------|-------------|
| `unit/` | Unit tests (~60 files) | `make test-unit` |
| `integration/` | Integration tests | `make test-integration` |
| `property/` | Property-based tests (hypothesis) | `make test-property` |
| `benchmarks/` | Performance benchmarks | `make test-benchmark` |
| `contract/` | Contract/API tests | `uv run pytest tests/contract/ -v` |

## Quick Reference

```bash
# Run all tests
make test

# Run specific test types
make test-unit          # Unit tests only
make test-integration   # Integration tests
make test-property      # Property-based tests
make test-benchmark     # Benchmarks
make test-parallel      # Parallel execution (fast)
make test-watch         # Watch mode

# Run with coverage
make coverage

# Run specific test file
uv run pytest tests/unit/test_rotator.py -v

# Run tests matching pattern
uv run pytest tests/ -k "cache" -v

# Skip slow tests
uv run pytest tests/ -m "not slow"
```

## Test Patterns

### Standard Unit Test

```python
import pytest
from proxywhirl import ProxyRotator, Proxy

def test_rotator_initialization():
    """Test basic rotator initialization."""
    rotator = ProxyRotator()
    assert rotator is not None

@pytest.fixture
def sample_proxy():
    """Fixture providing a sample proxy."""
    return Proxy(
        host="127.0.0.1",
        port=8080,
        protocol="http",
    )

def test_proxy_validation(sample_proxy):
    """Test using fixture."""
    assert sample_proxy.host == "127.0.0.1"
```

### Async Test

```python
# No decorator needed - asyncio_mode = "auto"
async def test_async_get_proxy():
    """Async tests work automatically."""
    rotator = ProxyRotator()
    proxy = await rotator.get_proxy()
    assert proxy is not None
```

### Property-Based Test (Hypothesis)

```python
from hypothesis import given, strategies as st
from proxywhirl import Proxy

@given(
    host=st.from_regex(r"[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}"),
    port=st.integers(min_value=1, max_value=65535),
)
def test_proxy_creation(host, port):
    """Property: Any valid host/port creates a valid proxy."""
    proxy = Proxy(host=host, port=port, protocol="http")
    assert proxy.port == port
```

### Benchmark Test

```python
import pytest

@pytest.mark.benchmark
def test_proxy_selection_performance(benchmark):
    """Benchmark proxy selection."""
    rotator = ProxyRotator()

    result = benchmark(rotator.select_proxy)

    assert result is not None
```

### Snapshot Test (Syrupy)

```python
@pytest.mark.snapshot
def test_api_response_format(snapshot):
    """Snapshot test for API response structure."""
    response = get_api_response()
    assert response == snapshot
```

## Fixtures (conftest.py)

Key fixtures available in all tests:

| Fixture | Scope | Description |
|---------|-------|-------------|
| `rotator` | function | Fresh ProxyRotator instance |
| `async_rotator` | function | AsyncProxyRotator instance |
| `sample_proxy` | function | Sample Proxy object |
| `proxy_pool` | function | ProxyPool with test data |
| `mock_httpx` | function | Mocked httpx client |

## Test Markers

| Marker | Purpose | Usage |
|--------|---------|-------|
| `@pytest.mark.slow` | Slow tests (>5s) | Skip: `-m "not slow"` |
| `@pytest.mark.integration` | External dependencies | Skip: `-m "not integration"` |
| `@pytest.mark.network` | Network access required | Skip: `-m "not network"` |
| `@pytest.mark.benchmark` | Performance tests | Only: `--benchmark-only` |
| `@pytest.mark.snapshot` | Snapshot tests | Update: `--snapshot-update` |
| `@pytest.mark.property` | Hypothesis tests | Run: `-m property` |
| `@pytest.mark.flaky` | Known flaky tests | Auto-rerun in CI |

## Mocking Patterns

### Mock HTTP Requests (respx)

```python
import respx
from httpx import Response

@respx.mock
async def test_fetch_proxies():
    """Mock external HTTP calls."""
    respx.get("https://api.example.com/proxies").mock(
        return_value=Response(200, json={"proxies": []})
    )

    result = await fetch_proxies()
    assert result == []
```

### Mock with pytest-mock

```python
def test_with_mock(mocker):
    """Use pytest-mock for patching."""
    mock_validate = mocker.patch(
        "proxywhirl.fetchers.ProxyValidator.validate"
    )
    mock_validate.return_value = True

    result = validate_proxy(proxy)
    assert result is True
```

## Boundaries

### Always Do

- Write tests BEFORE implementation
- Use fixtures for common setup
- Mark tests with appropriate markers
- Clean up resources in fixtures (use `yield`)
- Test edge cases and error conditions

### Ask First

- Adding new markers
- Changing fixture scopes
- Modifying conftest.py shared fixtures

### Never Touch

- Skipping tests without documenting reason
- Removing tests without replacement
- Hardcoding external URLs in tests

## Coverage

```bash
# Generate coverage report
make coverage

# View HTML report
open logs/htmlcov/index.html
```

Target coverage: 85%+ for core modules.
