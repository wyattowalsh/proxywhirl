"""
ProxyWhirl: Advanced Python Proxy Rotation Library

A production-ready library for intelligent proxy rotation with auto-fetching,
validation, and persistence capabilities.
"""

from proxywhirl.browser import BrowserRenderer
from proxywhirl.cache import CacheManager
from proxywhirl.cache_models import (
    CacheConfig,
    CacheEntry,
    CacheStatistics,
    CacheTierConfig,
    HealthStatus as CacheHealthStatus,
    TierStatistics,
)
from proxywhirl.config import (
    ConfigurationManager,
    load_yaml_config,
    parse_cli_args,
    validate_config,
)
from proxywhirl.config_models import (
    ConfigUpdate,
    ConfigurationSnapshot,
    ConfigurationSource,
    ProxyWhirlSettings,
    User,
    ValidationError,
    ValidationResult,
)
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
    HealthMonitor,
    HealthStatus,
    Proxy,
    ProxyConfiguration,
    ProxyCredentials,
    ProxyFormat,
    ProxyPool,
    ProxySource,
    ProxySourceConfig,
    RenderMode,
    SourceStats,
    ValidationLevel,
)
from proxywhirl.rotator import ProxyRotator
from proxywhirl.sources import (
    ALL_HTTP_SOURCES,
    ALL_SOCKS4_SOURCES,
    ALL_SOCKS5_SOURCES,
    ALL_SOURCES,
    API_SOURCES,
    FREE_PROXY_LIST,
    GEONODE_HTTP,
    GEONODE_SOCKS4,
    GEONODE_SOCKS5,
    GITHUB_CLARKETM_HTTP,
    GITHUB_HOOKZOF_HTTP,
    GITHUB_MONOSANS_HTTP,
    GITHUB_MONOSANS_SOCKS4,
    GITHUB_MONOSANS_SOCKS5,
    GITHUB_THESPECBAY_HTTP,
    GITHUB_THESPECBAY_SOCKS4,
    GITHUB_THESPECBAY_SOCKS5,
    PROXY_NOVA,
    PROXY_SCRAPE_HTTP,
    PROXY_SCRAPE_SOCKS4,
    PROXY_SCRAPE_SOCKS5,
    RECOMMENDED_SOURCES,
)
from proxywhirl.strategies import (
    CompositeStrategy,
    GeoTargetedStrategy,
    LeastUsedStrategy,
    PerformanceBasedStrategy,
    RandomStrategy,
    RotationStrategy,
    RoundRobinStrategy,
    SessionPersistenceStrategy,
    StrategyRegistry,
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

__version__ = "1.0.0"

__all__: list[str] = [
    # Version
    "__version__",
    # Configuration Management
    "ConfigurationManager",
    "ProxyWhirlSettings",
    "User",
    "ConfigurationSource",
    "ConfigurationSnapshot",
    "ConfigUpdate",
    "ValidationResult",
    "ValidationError",
    "load_yaml_config",
    "parse_cli_args",
    "validate_config",
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
    # Models
    "Proxy",
    "ProxyCredentials",
    "ProxyConfiguration",
    "ProxySourceConfig",
    "SourceStats",
    "ProxyPool",
    "HealthMonitor",
    # Enums
    "HealthStatus",
    "ProxySource",
    "ProxyFormat",
    "RenderMode",
    "ValidationLevel",
    # Core Classes
    "ProxyRotator",
    "ProxyFetcher",
    "ProxyValidator",
    "BrowserRenderer",
    # Protocols
    "RotationStrategy",
    # Strategy Registry
    "StrategyRegistry",
    # Strategies
    "CompositeStrategy",
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
    "FREE_PROXY_LIST",
    "PROXY_SCRAPE_HTTP",
    "PROXY_SCRAPE_SOCKS4",
    "PROXY_SCRAPE_SOCKS5",
    "GEONODE_HTTP",
    "GEONODE_SOCKS4",
    "GEONODE_SOCKS5",
    "PROXY_NOVA",
    "GITHUB_CLARKETM_HTTP",
    "GITHUB_THESPECBAY_HTTP",
    "GITHUB_THESPECBAY_SOCKS4",
    "GITHUB_THESPECBAY_SOCKS5",
    "GITHUB_MONOSANS_HTTP",
    "GITHUB_MONOSANS_SOCKS4",
    "GITHUB_MONOSANS_SOCKS5",
    "GITHUB_HOOKZOF_HTTP",
    # Built-in Proxy Sources (Collections)
    "ALL_HTTP_SOURCES",
    "ALL_SOCKS4_SOURCES",
    "ALL_SOCKS5_SOURCES",
    "ALL_SOURCES",
    "RECOMMENDED_SOURCES",
    "API_SOURCES",
]
