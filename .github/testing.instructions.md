---
applyTo: "tests/**/*.py"
---

# ProxyWhirl Testing Instructions

Follow these instructions for comprehensive testing with AI assistance and MCP tool orchestration.

## Testing Framework Setup

### Core Testing Dependencies
Always use these testing tools in ProxyWhirl:
- **pytest-asyncio**: For async test execution with `@pytest.mark.asyncio`
- **pytest-cov**: Coverage analysis with branch coverage enabled
- **pytest-benchmark**: Performance regression detection
- **pytest-xdist**: Parallel test execution with `-n auto`
- **pytest-mock**: Mocking and patching for isolated tests
- **hypothesis**: Property-based testing for robust validation

### Test Configuration
Ensure your tests follow these patterns:

```python
# Required imports for ProxyWhirl tests
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, Mock, patch
from hypothesis import given, strategies as st

# Use asyncio event loop for all async tests
@pytest.mark.asyncio
async def test_async_proxy_validation():
    """Test async proxy validation with proper error handling."""
    # Implementation follows async patterns
```

## AI-Assisted Test Development

### GitHub Copilot Integration
When writing tests, GitHub Copilot will understand ProxyWhirl patterns:
- Use descriptive test names that explain the scenario
- Follow the pattern `test_<component>_<scenario>_<expected_outcome>`
- Include docstrings for complex test scenarios
- Use type hints for better AI assistance

### MCP Tool-Enhanced Test Planning
Before implementing complex test scenarios, use:

```bash
# Research testing patterns for similar libraries
mcp_docfork_get-library-docs("pytest-dev/pytest", "async testing patterns")
mcp_docfork_get-library-docs("pydantic/pydantic", "validation testing strategies")

# Performance benchmarking research
mcp_brave_search_brave_web_search("Python async performance testing 2025")
```

## Test Organization Patterns

### Required Test Structure
Follow this test organization:

```
tests/
├── conftest.py              # Shared fixtures and configuration
├── test_<component>.py      # Component-specific tests
├── integration/             # Integration tests
│   └── test_e2e.py         # End-to-end scenarios
└── benchmarks/              # Performance tests
    └── test_performance.py  # Benchmark suites
```

### Essential Test Categories

#### 1. Unit Tests (Component Isolation)
```python
@pytest.mark.asyncio
async def test_proxy_validator_single_proxy():
    """Test ProxyValidator with a single valid proxy."""
    validator = ProxyValidator(timeout=5, max_workers=1)
    proxy = Proxy(ip="1.2.3.4", port=8080, scheme=ProxyScheme.HTTP)
    
    result = await validator.validate_single(proxy)
    
    assert isinstance(result, ValidationResult)
    assert result.proxy == proxy
```

#### 2. Integration Tests (Component Interaction)
```python
@pytest.mark.asyncio
async def test_proxywhirl_full_workflow():
    """Test complete ProxyWhirl workflow from load to validate."""
    loader = TheSpeedXLoader()
    cache = ProxyCache(CacheType.MEMORY)
    
    pw = ProxyWhirl(loaders=[loader], cache=cache)
    await pw.load_proxies()
    
    assert pw.total_proxies > 0
    assert len(await pw.get_valid_proxies()) >= 0
```

#### 3. Performance Tests (Benchmark Integration)
```python
@pytest.mark.benchmark(group="validation")
def test_validation_performance(benchmark):
    """Benchmark proxy validation performance."""
    proxies = [create_test_proxy() for _ in range(100)]
    validator = ProxyValidator()
    
    result = benchmark(validator.validate_batch, proxies)
    
    assert len(result) == 100
```

## Quality Assurance Instructions

### Mandatory Test Execution Commands
Always run these commands before committing:

```bash
# Complete quality pipeline (REQUIRED)
make test                    # Parallel test execution with coverage
make quality                 # Full pipeline: format → lint → test

# Advanced testing patterns
uv run pytest tests/ -v --cov=proxywhirl --cov-branch --cov-report=html
uv run pytest tests/ -n auto --benchmark-only  # Performance validation
```

### Coverage Requirements
Maintain these coverage thresholds:
- **Overall Coverage**: ≥ 90%
- **Branch Coverage**: ≥ 85%
- **Critical Components**: 100% (ProxyWhirl, ProxyValidator, ProxyCache)

### Test Data Management
Use these patterns for test data:

```python
# Fixtures for consistent test data
@pytest.fixture
def sample_proxy():
    """Provide a standard test proxy."""
    return Proxy(
        ip="192.168.1.1",
        port=8080,
        scheme=ProxyScheme.HTTP,
        country="US",
        source="test"
    )

# Property-based testing for robust validation
@given(st.ip_addresses(v=4), st.integers(min_value=1, max_value=65535))
def test_proxy_validation_property_based(ip, port):
    """Test proxy validation with generated data."""
    proxy = Proxy(ip=str(ip), port=port, scheme=ProxyScheme.HTTP)
    assert proxy.ip == str(ip)
    assert proxy.port == port
```

## Error Handling and Edge Cases

### Required Error Scenarios
Test these error conditions:

```python
@pytest.mark.asyncio
async def test_proxy_validation_timeout():
    """Test validator behavior with timeout scenarios."""
    with patch('aiohttp.ClientSession.get') as mock_get:
        mock_get.side_effect = asyncio.TimeoutError()
        
        validator = ProxyValidator(timeout=1)
        proxy = Proxy(ip="1.2.3.4", port=8080, scheme=ProxyScheme.HTTP)
        
        result = await validator.validate_single(proxy)
        assert not result.is_valid
        assert "timeout" in result.error_message.lower()
```

### Network Isolation
Always mock external network calls:

```python
@pytest.fixture
def mock_http_session():
    """Mock aiohttp session for network isolation."""
    with patch('aiohttp.ClientSession') as mock:
        yield mock

# Use in tests to prevent actual network requests
def test_loader_network_isolated(mock_http_session):
    # Test implementation without network dependency
    pass
```

## CI/CD Integration Instructions

### GitHub Actions Test Integration
Ensure tests integrate with CI/CD:

```python
def test_environment_detection():
    """Detect CI environment and adjust test behavior."""
    if os.environ.get("PYTEST_CURRENT_TEST"):
        # Running in CI - use deterministic behavior
        random.seed(42)
    
    # Test implementation
```

### Parallel Test Safety
Write thread-safe and process-safe tests:

```python
# Use temporary directories for file operations
@pytest.fixture
def temp_cache_dir(tmp_path):
    """Provide isolated cache directory for tests."""
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()
    return cache_dir

def test_cache_operations(temp_cache_dir):
    """Test cache with isolated file system."""
    cache = ProxyCache(CacheType.JSON, temp_cache_dir / "test.json")
    # Test implementation
```

## Anti-Patterns (FORBIDDEN)

### Testing Violations
- **FORBIDDEN**: Tests that depend on external network services
- **FORBIDDEN**: Tests that modify global state without cleanup
- **FORBIDDEN**: Non-deterministic tests without proper seeding
- **FORBIDDEN**: Tests without proper async handling (`@pytest.mark.asyncio`)
- **FORBIDDEN**: Skipping error scenario testing
- **FORBIDDEN**: Tests that bypass the quality pipeline (`make test`)
- **FORBIDDEN**: Hardcoded paths or configuration in tests
- **FORBIDDEN**: Tests that don't clean up resources (files, connections)

### Performance Violations
- **FORBIDDEN**: Benchmarks without baseline comparison
- **FORBIDDEN**: Tests that ignore performance regression thresholds
- **FORBIDDEN**: Slow tests without proper categorization (`@pytest.mark.slow`)
- **FORBIDDEN**: Missing timeout configurations for async operations

Follow these instructions consistently for reliable, maintainable, and AI-enhanced testing practices in ProxyWhirl.
