"""ProxyWhirl: Python proxy rotation with fetching, validation, and persistence.

Public symbols are resolved lazily via PEP 562 ``__getattr__`` to keep import
time small while preserving SemVer-safe ``from proxywhirl import X`` paths.
"""

from __future__ import annotations

from importlib import import_module
from importlib.metadata import PackageNotFoundError, version
from typing import Any

try:
    __version__ = version("proxywhirl")
except PackageNotFoundError:  # pragma: no cover - editable source tree fallback
    __version__ = "0.0.0"

# module path -> attribute name (or None to use same name)
_LAZY_EXPORTS: dict[str, tuple[str, str | None]] = {
    # browser
    "BrowserRenderer": ("proxywhirl.browser", None),
    # cache
    "CacheConfig": ("proxywhirl.cache", None),
    "CacheManager": ("proxywhirl.cache", None),
    # circuit breaker
    "AsyncCircuitBreaker": ("proxywhirl.circuit_breaker", None),
    "CircuitBreaker": ("proxywhirl.circuit_breaker", None),
    "CircuitBreakerState": ("proxywhirl.circuit_breaker", None),
    # config
    "DataStorageConfig": ("proxywhirl.config", None),
    # exceptions
    "BrowserRenderError": ("proxywhirl.exceptions", None),
    "CacheCorruptionError": ("proxywhirl.exceptions", None),
    "CacheStorageError": ("proxywhirl.exceptions", None),
    "CacheValidationError": ("proxywhirl.exceptions", None),
    "CircuitBreakerOpenError": ("proxywhirl.exceptions", None),
    "EventLoopConflictError": ("proxywhirl.exceptions", None),
    "ProxyAuthenticationError": ("proxywhirl.exceptions", None),
    "ProxyConnectionError": ("proxywhirl.exceptions", None),
    "ProxyErrorCode": ("proxywhirl.exceptions", None),
    "ProxyFetchError": ("proxywhirl.exceptions", None),
    "ProxyPoolEmptyError": ("proxywhirl.exceptions", None),
    "ProxySourceUnavailableError": ("proxywhirl.exceptions", None),
    "ProxyStorageError": ("proxywhirl.exceptions", None),
    "ProxyValidationError": ("proxywhirl.exceptions", None),
    "ProxyWhirlError": ("proxywhirl.exceptions", None),
    "RateLimitExceededError": ("proxywhirl.exceptions", None),
    "RequestQueueFullError": ("proxywhirl.exceptions", None),
    "redact_url": ("proxywhirl.exceptions", None),
    # fetchers
    "CSVParser": ("proxywhirl.fetchers", None),
    "HTMLTableParser": ("proxywhirl.fetchers", None),
    "JSONParser": ("proxywhirl.fetchers", None),
    "PlainTextParser": ("proxywhirl.fetchers", None),
    "ProxyFetcher": ("proxywhirl.fetchers", None),
    "ProxyValidator": ("proxywhirl.fetchers", None),
    "ValidationResult": ("proxywhirl.fetchers", None),
    "deduplicate_proxies": ("proxywhirl.fetchers", None),
    # models
    "BootstrapConfig": ("proxywhirl.models", None),
    "CircuitBreakerConfig": ("proxywhirl.models", None),
    "HealthMonitor": ("proxywhirl.models", None),
    "HealthStatus": ("proxywhirl.models", None),
    "PoolSummary": ("proxywhirl.models", None),
    "Proxy": ("proxywhirl.models", None),
    "ProxyChain": ("proxywhirl.models", None),
    "ProxyCredentials": ("proxywhirl.models", None),
    "ProxyFormat": ("proxywhirl.models", None),
    "ProxyPool": ("proxywhirl.models", None),
    "ProxySource": ("proxywhirl.models", None),
    "ProxySourceConfig": ("proxywhirl.models", None),
    "ProxyStatus": ("proxywhirl.models", None),
    "RenderMode": ("proxywhirl.models", None),
    "RequestResult": ("proxywhirl.models", None),
    "SelectionContext": ("proxywhirl.models", None),
    "Session": ("proxywhirl.models", None),
    "SourceStats": ("proxywhirl.models", None),
    "StorageBackend": ("proxywhirl.models", None),
    "StrategyConfig": ("proxywhirl.models", None),
    "ValidationLevel": ("proxywhirl.models", None),
    # orchestration
    "FailoverPolicy": ("proxywhirl.orchestration", None),
    "ProxyRotationContext": ("proxywhirl.orchestration", None),
    "RequestOrchestration": ("proxywhirl.orchestration", None),
    # rate limiting
    "AsyncRateLimiter": ("proxywhirl.rate_limiting", None),
    "RateLimit": ("proxywhirl.rate_limiting", None),
    "RateLimitEvent": ("proxywhirl.rate_limiting", None),
    "RateLimiter": ("proxywhirl.rate_limiting", None),
    # retry
    "BackoffStrategy": ("proxywhirl.retry", None),
    "NonRetryableError": ("proxywhirl.retry", None),
    "RetryableError": ("proxywhirl.retry", None),
    "RetryExecutor": ("proxywhirl.retry", None),
    "RetryMetrics": ("proxywhirl.retry", None),
    "RetryPolicy": ("proxywhirl.retry", None),
    # rotator
    "AsyncProxyWhirl": ("proxywhirl.rotator", None),
    "ProxyWhirl": ("proxywhirl.rotator", None),
    # safe_regex
    "RegexComplexityError": ("proxywhirl.safe_regex", None),
    "RegexTimeoutError": ("proxywhirl.safe_regex", None),
    "safe_regex_compile": ("proxywhirl.safe_regex", None),
    "safe_regex_findall": ("proxywhirl.safe_regex", None),
    "safe_regex_match": ("proxywhirl.safe_regex", None),
    "safe_regex_search": ("proxywhirl.safe_regex", None),
    "validate_regex_pattern": ("proxywhirl.safe_regex", None),
    # settings
    "ProxyConfiguration": ("proxywhirl.settings", None),
    # sources
    "ALL_HTTP_SOURCES": ("proxywhirl.sources", None),
    "ALL_SOCKS4_SOURCES": ("proxywhirl.sources", None),
    "ALL_SOCKS5_SOURCES": ("proxywhirl.sources", None),
    "ALL_SOURCES": ("proxywhirl.sources", None),
    "API_SOURCES": ("proxywhirl.sources", None),
    "RECOMMENDED_SOURCES": ("proxywhirl.sources", None),
    "validate_sources": ("proxywhirl.sources", None),
    "validate_sources_sync": ("proxywhirl.sources", None),
    # storage
    "FileStorage": ("proxywhirl.storage", None),
    "SQLiteStorage": ("proxywhirl.storage", None),
    "dict_to_proxy": ("proxywhirl.storage", None),
    # strategies
    "CompositeStrategy": ("proxywhirl.strategies", None),
    "CostAwareStrategy": ("proxywhirl.strategies", None),
    "GeoTargetedStrategy": ("proxywhirl.strategies", None),
    "LeastUsedStrategy": ("proxywhirl.strategies", None),
    "PerformanceBasedStrategy": ("proxywhirl.strategies", None),
    "ProxyMetrics": ("proxywhirl.strategies", None),
    "RandomStrategy": ("proxywhirl.strategies", None),
    "RotationStrategy": ("proxywhirl.strategies", None),
    "RoundRobinStrategy": ("proxywhirl.strategies", None),
    "SessionManager": ("proxywhirl.strategies", None),
    "SessionPersistenceStrategy": ("proxywhirl.strategies", None),
    "StrategyRegistry": ("proxywhirl.strategies", None),
    "StrategyState": ("proxywhirl.strategies", None),
    "WeightedStrategy": ("proxywhirl.strategies", None),
    # utils
    "configure_logging": ("proxywhirl.utils", None),
    "create_proxy_from_url": ("proxywhirl.utils", None),
    "decrypt_credentials": ("proxywhirl.utils", None),
    "encrypt_credentials": ("proxywhirl.utils", None),
    "generate_encryption_key": ("proxywhirl.utils", None),
    "is_valid_proxy_url": ("proxywhirl.utils", None),
    "mask_proxy_url": ("proxywhirl.utils", None),
    "mask_secret_str": ("proxywhirl.utils", None),
    "parse_proxy_url": ("proxywhirl.utils", None),
    "proxy_to_dict": ("proxywhirl.utils", None),
    "public_proxy_url": ("proxywhirl.utils", None),
    "scrub_credentials_from_dict": ("proxywhirl.utils", None),
    "validate_proxy_model": ("proxywhirl.utils", None),
    "validate_target_url_safe": ("proxywhirl.utils", None),
}


def __getattr__(name: str) -> Any:
    """Lazily resolve public exports (PEP 562)."""
    if name == "__version__":
        return __version__

    target = _LAZY_EXPORTS.get(name)
    if target is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    module_path, attr_name = target
    module = import_module(module_path)
    value = getattr(module, attr_name or name)

    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted({*globals(), *__all__})


__all__ = [
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
