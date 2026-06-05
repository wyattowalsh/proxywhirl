---
title: Testing Guide
---

# Testing Guide

## Overview

This guide covers testing strategies, fixtures, and best practices for ProxyWhirl applications.

## Unit Testing

### Basic Test Structure

```python
import pytest
from proxywhirl import ProxyWhirl, Proxy, ProxyPoolEmptyError

class TestProxySelection:

    @pytest.fixture
    def whirl(self):
        """Create test instance."""
        config = ProxyWhirl.ProxyConfiguration()
        return ProxyWhirl(config)

    def test_get_returns_proxy(self, whirl):
        """Test proxy retrieval."""
        proxy = whirl.get()
        assert proxy is not None
        assert proxy.host is not None
        assert 1 <= proxy.port <= 65535

    def test_empty_pool_raises_error(self, whirl):
        """Test error on empty pool."""
        whirl.pool.proxies.clear()
        with pytest.raises(ProxyPoolEmptyError):
            whirl.get()
```

### Mock Fixtures

```python
import pytest
from unittest.mock import Mock, patch, MagicMock
from proxywhirl import Proxy

@pytest.fixture
def mock_proxy():
    """Create mock proxy."""
    return Proxy(
        url="http://127.0.0.1:8080",
        host="127.0.0.1",
        port=8080,
        protocol="http",
        is_active=True
    )

@pytest.fixture
def mock_proxies():
    """Create multiple mock proxies."""
    return [
        Proxy(
            url=f"http://proxy{i}.test:8080",
            host=f"proxy{i}.test",
            port=8080,
            protocol="http",
            is_active=True
        )
        for i in range(5)
    ]
```

## Async Testing

### AsyncProxyWhirl Tests

```python
import pytest
import asyncio
from proxywhirl import AsyncProxyWhirl

@pytest.mark.asyncio
async def test_async_get():
    """Test async proxy retrieval."""
    whirl = AsyncProxyWhirl()
    proxy = whirl.get()
    assert proxy is not None

@pytest.mark.asyncio
async def test_concurrent_access():
    """Test concurrent proxy access."""
    whirl = AsyncProxyWhirl()

    async def get_proxies(n):
        return [whirl.get() for _ in range(n)]

    results = await asyncio.gather(
        get_proxies(10),
        get_proxies(10),
        get_proxies(10)
    )

    all_proxies = [p for proxies in results for p in proxies]
    assert len(all_proxies) == 30
```

## HTTP Mocking

### Using respx (Recommended)

```python
import pytest
import httpx
from proxywhirl import ProxyWhirl
import respx

@pytest.fixture
def respx_mock():
    """Create respx mock."""
    with respx.mock:
        yield respx

def test_proxy_request_with_mocking(respx_mock):
    """Test with mocked HTTP responses."""
    whirl = ProxyWhirl()
    proxy = whirl.get()

    # Mock proxy validation endpoint
    respx_mock.get("http://httpbin.org/ip").mock(
        return_value=httpx.Response(200, json={"origin": "1.2.3.4"})
    )

    with httpx.Client() as client:
        response = client.get(
            "http://httpbin.org/ip",
            proxies=proxy.to_url()
        )
        assert response.status_code == 200
```

### Custom Mock Responses

```python
@pytest.fixture
def mock_sources(respx_mock):
    """Mock proxy source endpoints."""
    respx_mock.get(
        "https://raw.githubusercontent.com/example/proxies/main/list.json"
    ).mock(return_value=httpx.Response(200, json=[
        {"ip": "1.2.3.4", "port": 8080, "protocol": "http"},
        {"ip": "5.6.7.8", "port": 8080, "protocol": "https"},
    ]))
    return respx_mock

def test_bootstrap_with_mocking(mock_sources):
    """Test bootstrapping with mocked sources."""
    whirl = ProxyWhirl()
    proxies = whirl.bootstrap()
    assert len(proxies) == 2
```

## Property-Based Testing

### Using Hypothesis

```python
import pytest
from hypothesis import given, strategies as st
from proxywhirl import Proxy, ProxyPool

class TestProxyValidation:

    @given(
        host=st.text(min_size=1),
        port=st.integers(min_value=1, max_value=65535)
    )
    def test_proxy_creation(self, host, port):
        """Test proxy creation with random inputs."""
        try:
            proxy = Proxy(
                url=f"http://{host}:{port}",
                host=host,
                port=port,
                protocol="http",
                is_active=True
            )
            assert proxy.host == host
            assert proxy.port == port
        except (ValueError, AssertionError):
            # Expected for invalid inputs
            pass
```

## Integration Tests

### With Database

```python
import pytest
from proxywhirl import ProxyWhirl
from proxywhirl.storage import SQLiteStorage

@pytest.fixture
def whirl_with_db(tmp_path):
    """Create instance with temporary database."""
    db_path = tmp_path / "test.db"
    storage = SQLiteStorage(str(db_path))
    config = ProxyWhirl.ProxyConfiguration(storage=storage)
    return ProxyWhirl(config)

def test_persistence(whirl_with_db):
    """Test proxy persistence."""
    proxy = whirl_with_db.get()

    # Verify it's in storage
    stored = whirl_with_db.storage.get_by_url(proxy.url)
    assert stored.host == proxy.host
```

## Performance Testing

### Benchmark Tests

```python
import pytest
import timeit
from proxywhirl import ProxyWhirl

class TestPerformance:

    def test_selection_speed(self, benchmark):
        """Benchmark proxy selection."""
        whirl = ProxyWhirl()

        def select():
            return whirl.get()

        result = benchmark(select)
        assert result is not None

    def test_throughput(self):
        """Test throughput of selections."""
        whirl = ProxyWhirl()

        start = timeit.default_timer()
        for _ in range(10000):
            whirl.get()
        duration = timeit.default_timer() - start

        throughput = 10000 / duration
        assert throughput > 5000  # 5k ops/sec minimum
```

### Memory Profiling

```python
import pytest
from memory_profiler import profile
from proxywhirl import ProxyWhirl

@profile
def test_memory_usage():
    """Check memory usage during operation."""
    whirl = ProxyWhirl()
    proxies = []

    for _ in range(1000):
        proxies.append(whirl.get())

    # Memory snapshot here
    return proxies
```

## Snapshot Testing

### Using syrupy

```python
import pytest
from proxywhirl import ProxyWhirl

def test_proxy_snapshot(snapshot):
    """Test proxy structure matches snapshot."""
    whirl = ProxyWhirl()
    proxy = whirl.get()

    assert snapshot == {
        "host": proxy.host,
        "port": proxy.port,
        "protocol": proxy.protocol,
        "is_active": proxy.is_active,
    }
```

## Test Organization

### `conftest.py`

```python
# tests/conftest.py

import pytest
from proxywhirl import ProxyWhirl, Proxy

@pytest.fixture(scope="session")
def test_config():
    """Shared test configuration."""
    return {
        "pool_size": 10,
        "timeout": 5,
        "retry_attempts": 2
    }

@pytest.fixture
def whirl(test_config):
    """ProxyWhirl instance for all tests."""
    config = ProxyWhirl.ProxyConfiguration(**test_config)
    return ProxyWhirl(config)

@pytest.fixture
def sample_proxies():
    """Sample proxy data."""
    return [
        Proxy(
            url=f"http://proxy{i}.test:8080",
            host=f"proxy{i}.test",
            port=8080,
            protocol="http",
            is_active=True
        )
        for i in range(5)
    ]
```

## Test Markers

```python
import pytest

# Mark slow tests
@pytest.mark.slow
def test_large_pool():
    """Test with large proxy pool."""
    pass

# Mark integration tests
@pytest.mark.integration
def test_real_api():
    """Test with real API."""
    pass

# Mark flaky tests
@pytest.mark.flaky(reruns=3)
def test_network_dependent():
    """Test that may fail intermittently."""
    pass
```

## CI/CD Testing

### GitHub Actions

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12", "3.13"]

    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: uv sync --extra dev

      - name: Run tests
        run: uv run pytest tests/ -v

      - name: Upload coverage
        run: uv run pytest tests/ --cov=proxywhirl
```

## Best Practices

### Do's ✓

- Use fixtures for reusable setup
- Mock external dependencies (HTTP, databases)
- Test both happy path and error cases
- Use parametrize for multiple scenarios
- Test async code with @pytest.mark.asyncio
- Isolate unit tests from integration tests

### Don'ts ✗

- Don't test external APIs (mock them)
- Don't share mutable fixtures across tests
- Don't use sleep() for timing (use mocks)
- Don't hard-code test data
- Don't log in tests (use capsys)

## Running Tests

```bash
# All tests
uv run pytest tests/ -v

# Unit tests only
uv run pytest tests/unit/ -v

# Integration tests
uv run pytest tests/integration/ -v

# With coverage
uv run pytest tests/ --cov=proxywhirl --cov-report=html

# Specific test
uv run pytest tests/test_rotator.py::test_get_returns_proxy -v

# Markers
uv run pytest tests/ -m "not slow" -v
```

See also: [Troubleshooting Guide](./troubleshooting.md)
