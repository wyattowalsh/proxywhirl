"""Public package API contract tests."""

from __future__ import annotations

from importlib import import_module
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python < 3.11 compatibility
    import tomli as tomllib


EXPECTED_TOP_LEVEL_EXPORTS = [
    "ALL_HTTP_SOURCES",
    "ALL_SOCKS4_SOURCES",
    "ALL_SOCKS5_SOURCES",
    "ALL_SOURCES",
    "API_SOURCES",
    "AsyncCircuitBreaker",
    "AsyncProxyWhirl",
    "AsyncRateLimiter",
    "BackoffStrategy",
    "BootstrapConfig",
    "BrowserRenderError",
    "BrowserRenderer",
    "CSVParser",
    "CacheConfig",
    "CacheCorruptionError",
    "CacheManager",
    "CacheStorageError",
    "CacheValidationError",
    "CircuitBreaker",
    "CircuitBreakerConfig",
    "CircuitBreakerOpenError",
    "CircuitBreakerState",
    "CompositeStrategy",
    "CostAwareStrategy",
    "DataStorageConfig",
    "EventLoopConflictError",
    "FailoverPolicy",
    "FileStorage",
    "GeoTargetedStrategy",
    "HTMLTableParser",
    "HealthMonitor",
    "HealthStatus",
    "JSONParser",
    "LeastUsedStrategy",
    "NonRetryableError",
    "PerformanceBasedStrategy",
    "PlainTextParser",
    "PoolSummary",
    "Proxy",
    "ProxyAuthenticationError",
    "ProxyChain",
    "ProxyConfiguration",
    "ProxyConnectionError",
    "ProxyCredentials",
    "ProxyErrorCode",
    "ProxyFetcher",
    "ProxyFetchError",
    "ProxyFormat",
    "ProxyMetrics",
    "ProxyPool",
    "ProxyPoolEmptyError",
    "ProxyRotationContext",
    "ProxySource",
    "ProxySourceConfig",
    "ProxySourceUnavailableError",
    "ProxyStatus",
    "ProxyStorageError",
    "ProxyValidationError",
    "ProxyValidator",
    "ProxyWhirl",
    "ProxyWhirlError",
    "RECOMMENDED_SOURCES",
    "RandomStrategy",
    "RateLimit",
    "RateLimitEvent",
    "RateLimitExceededError",
    "RateLimiter",
    "RegexComplexityError",
    "RegexTimeoutError",
    "RenderMode",
    "RequestOrchestration",
    "RequestQueueFullError",
    "RequestResult",
    "RetryExecutor",
    "RetryMetrics",
    "RetryPolicy",
    "RetryableError",
    "RotationStrategy",
    "RoundRobinStrategy",
    "SQLiteStorage",
    "SelectionContext",
    "Session",
    "SessionManager",
    "SessionPersistenceStrategy",
    "SourceStats",
    "StorageBackend",
    "StrategyConfig",
    "StrategyRegistry",
    "StrategyState",
    "ValidationLevel",
    "ValidationResult",
    "WeightedStrategy",
    "__version__",
    "configure_logging",
    "create_proxy_from_url",
    "deduplicate_proxies",
    "decrypt_credentials",
    "dict_to_proxy",
    "encrypt_credentials",
    "generate_encryption_key",
    "is_valid_proxy_url",
    "mask_proxy_url",
    "mask_secret_str",
    "parse_proxy_url",
    "proxy_to_dict",
    "public_proxy_url",
    "redact_url",
    "safe_regex_compile",
    "safe_regex_findall",
    "safe_regex_match",
    "safe_regex_search",
    "scrub_credentials_from_dict",
    "validate_proxy_model",
    "validate_regex_pattern",
    "validate_sources",
    "validate_sources_sync",
    "validate_target_url_safe",
]


SURVIVING_PUBLIC_MODULES = [
    "proxywhirl.models",
    "proxywhirl.rotator",
    "proxywhirl.api",
    "proxywhirl.mcp.server",
    "proxywhirl.cache",
    "proxywhirl.retry",
    "proxywhirl.rate_limiting",
    "proxywhirl.strategies",
]


def test_top_level_all_symbols_are_importable() -> None:
    """Every advertised top-level export should resolve on the package object."""
    import proxywhirl

    assert proxywhirl.__all__ == EXPECTED_TOP_LEVEL_EXPORTS
    assert "__version__" in proxywhirl.__all__
    missing = [name for name in proxywhirl.__all__ if not hasattr(proxywhirl, name)]

    assert missing == []


def test_documented_surviving_modules_are_importable() -> None:
    """Restructuring must preserve the documented surviving module entry points."""
    missing = []
    for module_name in SURVIVING_PUBLIC_MODULES:
        try:
            import_module(module_name)
        except Exception as exc:  # pragma: no cover - assertion prints detail
            missing.append(f"{module_name}: {exc!r}")

    assert missing == []


def test_project_scripts_import_declared_entry_points() -> None:
    """Console-script targets in pyproject should stay importable."""
    pyproject_path = Path(__file__).resolve().parents[2] / "pyproject.toml"
    pyproject = tomllib.loads(pyproject_path.read_text())

    assert pyproject["project"]["scripts"] == {
        "proxywhirl": "proxywhirl.cli:app",
        "proxywhirl-mcp": "proxywhirl.mcp.server:main",
    }

    for target in pyproject["project"]["scripts"].values():
        module_name, attribute_name = target.split(":", maxsplit=1)
        module = import_module(module_name)
        assert hasattr(module, attribute_name)


def test_top_level_version_matches_project_metadata() -> None:
    """The runtime package version should stay aligned with pyproject metadata."""
    import proxywhirl

    pyproject_path = Path(__file__).resolve().parents[2] / "pyproject.toml"
    pyproject = tomllib.loads(pyproject_path.read_text())

    assert proxywhirl.__version__ == pyproject["project"]["version"]
