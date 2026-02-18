"""
ProxyWhirl: Advanced Python Proxy Rotation Library

A production-ready library for intelligent proxy rotation with auto-fetching,
validation, and persistence capabilities.
"""

from __future__ import annotations

from proxywhirl.browser import BrowserRenderer
from proxywhirl.cache import CacheManager
from proxywhirl.cache.models import (
    CacheConfig,
    CacheEntry,
    CacheStatistics,
    CacheTierConfig,
    TierStatistics,
)
from proxywhirl.cache.models import (
    HealthStatus as CacheHealthStatus,
)
from proxywhirl.circuit_breaker import AsyncCircuitBreaker, CircuitBreaker, CircuitBreakerState
from proxywhirl.config import DataStorageConfig
from proxywhirl.exceptions import (
    CacheCorruptionError,
    CacheStorageError,
    CacheValidationError,
    ProxyAuthenticationError,
    ProxyConnectionError,
    ProxyFetchError,
    ProxyPoolEmptyError,
    ProxyStorageError,
    ProxyValidationError,
    ProxyWhirlError,
    RequestQueueFullError,
)
from proxywhirl.fetchers import (
    CSVParser,
    HTMLTableParser,
    JSONParser,
    PlainTextParser,
    ProxyFetcher,
    ProxyValidator,
    deduplicate_proxies,
)
from proxywhirl.models import (
    BootstrapConfig,
    CircuitBreakerConfig,
    HealthMonitor,
    HealthStatus,
    Proxy,
    ProxyChain,
    ProxyConfiguration,
    ProxyCredentials,
    ProxyFormat,
    ProxyPool,
    ProxySource,
    ProxySourceConfig,
    RenderMode,
    SelectionContext,
    Session,
    SourceStats,
    StrategyConfig,
    ValidationLevel,
)
from proxywhirl.retry import (
    BackoffStrategy,
    CircuitBreakerEvent,
    HourlyAggregate,
    NonRetryableError,
    RetryableError,
    RetryAttempt,
    RetryExecutor,
    RetryMetrics,
    RetryOutcome,
    RetryPolicy,
)
from proxywhirl.rotator import AsyncProxyWhirl, ProxyWhirl
from proxywhirl.safe_regex import RegexComplexityError, RegexTimeoutError
from proxywhirl.sources import (
    ALL_HTTP_SOURCES,
    ALL_SOCKS4_SOURCES,
    ALL_SOCKS5_SOURCES,
    ALL_SOURCES,
    API_SOURCES,
    GEONODE_HTTP,
    GEONODE_SOCKS4,
    GEONODE_SOCKS5,
    GITHUB_KOMUTAN_HTTP,
    GITHUB_KOMUTAN_SOCKS4,
    GITHUB_KOMUTAN_SOCKS5,
    GITHUB_MONOSANS_HTTP,
    GITHUB_MONOSANS_SOCKS4,
    GITHUB_MONOSANS_SOCKS5,
    GITHUB_PROXIFLY_HTTP,
    GITHUB_PROXIFLY_SOCKS4,
    GITHUB_PROXIFLY_SOCKS5,
    GITHUB_THESPEEDX_HTTP,
    GITHUB_THESPEEDX_SOCKS4,
    GITHUB_THESPEEDX_SOCKS5,
    RECOMMENDED_SOURCES,
)
from proxywhirl.strategies import (
    CompositeStrategy,
    CostAwareStrategy,
    GeoTargetedStrategy,
    LeastUsedStrategy,
    PerformanceBasedStrategy,
    ProxyMetrics,
    RandomStrategy,
    RotationStrategy,
    RoundRobinStrategy,
    SessionPersistenceStrategy,
    StrategyRegistry,
    StrategyState,
    WeightedStrategy,
)
from proxywhirl.utils import (
    configure_logging,
    create_proxy_from_url,
    decrypt_credentials,
    encrypt_credentials,
    generate_encryption_key,
    is_valid_proxy_url,
    parse_proxy_url,
    proxy_to_dict,
    validate_proxy_model,
)

__version__ = "0.3.0"

__all__: list[str] = [
    # Version
    "__version__",
    # Configuration
    "BootstrapConfig",
    "DataStorageConfig",
    # Retry & Failover Components
    "RetryPolicy",
    "BackoffStrategy",
    "CircuitBreaker",
    "AsyncCircuitBreaker",
    "CircuitBreakerConfig",
    "CircuitBreakerState",
    "RetryExecutor",
    "RetryMetrics",
    "RetryAttempt",
    "RetryOutcome",
    "CircuitBreakerEvent",
    "HourlyAggregate",
    # Cache Components
    "CacheManager",
    "CacheConfig",
    "CacheEntry",
    "CacheStatistics",
    "CacheTierConfig",
    "TierStatistics",
    "CacheHealthStatus",
    # Exceptions
    "ProxyWhirlError",
    "ProxyValidationError",
    "ProxyPoolEmptyError",
    "ProxyConnectionError",
    "ProxyAuthenticationError",
    "ProxyFetchError",
    "ProxyStorageError",
    "CacheCorruptionError",
    "CacheStorageError",
    "CacheValidationError",
    "RequestQueueFullError",
    "RetryableError",
    "NonRetryableError",
    "RegexTimeoutError",
    "RegexComplexityError",
    # Models
    "Proxy",
    "ProxyChain",
    "ProxyCredentials",
    "ProxyConfiguration",
    "ProxySourceConfig",
    "SelectionContext",
    "Session",
    "SourceStats",
    "StrategyConfig",
    "ProxyPool",
    "HealthMonitor",
    # Enums
    "HealthStatus",
    "ProxySource",
    "ProxyFormat",
    "RenderMode",
    "ValidationLevel",
    # Core Classes
    "ProxyWhirl",
    "AsyncProxyWhirl",
    "ProxyFetcher",
    "ProxyValidator",
    "BrowserRenderer",
    # Protocols
    "RotationStrategy",
    # Strategy Registry
    "StrategyRegistry",
    # Strategy State Management
    "StrategyState",
    "ProxyMetrics",
    # Strategies
    "CompositeStrategy",
    "CostAwareStrategy",
    "RoundRobinStrategy",
    "RandomStrategy",
    "WeightedStrategy",
    "LeastUsedStrategy",
    "PerformanceBasedStrategy",
    "SessionPersistenceStrategy",
    "GeoTargetedStrategy",
    # Parsers
    "JSONParser",
    "CSVParser",
    "PlainTextParser",
    "HTMLTableParser",
    # Utilities
    "configure_logging",
    "is_valid_proxy_url",
    "parse_proxy_url",
    "validate_proxy_model",
    "encrypt_credentials",
    "decrypt_credentials",
    "generate_encryption_key",
    "proxy_to_dict",
    "create_proxy_from_url",
    "deduplicate_proxies",
    # Built-in Proxy Sources (Individual)
    "GEONODE_HTTP",
    "GEONODE_SOCKS4",
    "GEONODE_SOCKS5",
    "GITHUB_THESPEEDX_HTTP",
    "GITHUB_THESPEEDX_SOCKS4",
    "GITHUB_THESPEEDX_SOCKS5",
    "GITHUB_MONOSANS_HTTP",
    "GITHUB_MONOSANS_SOCKS4",
    "GITHUB_MONOSANS_SOCKS5",
    "GITHUB_PROXIFLY_HTTP",
    "GITHUB_PROXIFLY_SOCKS4",
    "GITHUB_PROXIFLY_SOCKS5",
    "GITHUB_KOMUTAN_HTTP",
    "GITHUB_KOMUTAN_SOCKS4",
    "GITHUB_KOMUTAN_SOCKS5",
    # Built-in Proxy Sources (Collections)
    "ALL_HTTP_SOURCES",
    "ALL_SOCKS4_SOURCES",
    "ALL_SOCKS5_SOURCES",
    "ALL_SOURCES",
    "RECOMMENDED_SOURCES",
    "API_SOURCES",
]
