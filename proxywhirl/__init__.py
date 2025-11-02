"""
ProxyWhirl: Advanced Python Proxy Rotation Library

A production-ready library for intelligent proxy rotation with auto-fetching,
validation, and persistence capabilities.
"""

from proxywhirl.analytics_engine import AnalyticsEngine
from proxywhirl.analytics_models import (
    AnalysisConfig,
    AnalysisReport,
    AnalysisType,
    AnalyticsQuery,
    Anomaly,
    AnomalyType,
    ExportFormat,
    FailureCluster,
    PerformanceScore,
    Prediction,
    ProxyPerformanceMetrics,
    Recommendation,
    RecommendationPriority,
    TimeSeriesData,
    TrendDirection,
    UsagePattern,
)
from proxywhirl.browser import BrowserRenderer
from proxywhirl.circuit_breaker import CircuitBreaker, CircuitBreakerState
from proxywhirl.retry_executor import RetryExecutor
from proxywhirl.retry_metrics import (
    CircuitBreakerEvent,
    HourlyAggregate,
    RetryAttempt,
    RetryMetrics,
    RetryOutcome,
)
from proxywhirl.retry_policy import BackoffStrategy, RetryPolicy
from proxywhirl.cache import CacheManager
from proxywhirl.cost_analyzer import CostAnalyzer
from proxywhirl.failure_analyzer import FailureAnalyzer
from proxywhirl.pattern_detector import PatternDetector
from proxywhirl.performance_analyzer import PerformanceAnalyzer
from proxywhirl.predictive_analytics import PredictiveAnalytics
from proxywhirl.cache_models import (
    CacheConfig,
    CacheEntry,
    CacheStatistics,
    CacheTierConfig,
    HealthStatus as CacheHealthStatus,
    TierStatistics,
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
from proxywhirl.export_manager import ExportManager
from proxywhirl.export_models import (
    CompressionType,
    ConfigurationExportFilter,
    ExportConfig,
    ExportDestination,
    ExportDestinationType,
    ExportFormat,
    ExportHistoryEntry,
    ExportJob,
    ExportMetadata,
    ExportProgress,
    ExportResult,
    ExportStatus,
    ExportType,
    HTTPDestination,
    LocalFileDestination,
    LogExportFilter,
    MemoryDestination,
    MetricsExportFilter,
    ProxyExportFilter,
    S3Destination,
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
# Health monitoring (Feature 006)
from proxywhirl.health import HealthChecker
from proxywhirl.health_models import (
    HealthCheckConfig,
    HealthCheckResult,
    HealthEvent,
    HealthStatus as HealthMonitoringStatus,
    PoolStatus,
    ProxyHealthState,
    SourceStatus,
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
    # Retry & Failover Components
    "RetryPolicy",
    "BackoffStrategy",
    "CircuitBreaker",
    "CircuitBreakerState",
    "RetryExecutor",
    "RetryMetrics",
    "RetryAttempt",
    "RetryOutcome",
    "CircuitBreakerEvent",
    "HourlyAggregate",
    # Analytics Components
    "AnalyticsEngine",
    "PerformanceAnalyzer",
    "PatternDetector",
    "FailureAnalyzer",
    "CostAnalyzer",
    "PredictiveAnalytics",
    # Analytics Models
    "AnalysisConfig",
    "AnalysisReport",
    "AnalysisType",
    "AnalyticsQuery",
    "ProxyPerformanceMetrics",
    "PerformanceScore",
    "UsagePattern",
    "FailureCluster",
    "Prediction",
    "Recommendation",
    "RecommendationPriority",
    "Anomaly",
    "AnomalyType",
    "TimeSeriesData",
    "TrendDirection",
    "ExportFormat",
    # Cache Components
    "CacheManager",
    "CacheConfig",
    "CacheEntry",
    "CacheStatistics",
    "CacheTierConfig",
    "TierStatistics",
    "CacheHealthStatus",
    # Health Monitoring (Feature 006)
    "HealthChecker",
    "HealthCheckConfig",
    "HealthCheckResult",
    "HealthEvent",
    "HealthMonitoringStatus",
    "PoolStatus",
    "SourceStatus",
    "ProxyHealthState",
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
    # Export Components
    "ExportManager",
    "ExportConfig",
    "ExportJob",
    "ExportResult",
    "ExportMetadata",
    "ExportProgress",
    "ExportHistoryEntry",
    "ProxyExportFilter",
    "MetricsExportFilter",
    "LogExportFilter",
    "ConfigurationExportFilter",
    "LocalFileDestination",
    "MemoryDestination",
    "S3Destination",
    "HTTPDestination",
    "ExportDestination",
    # Export Enums
    "ExportType",
    "ExportFormat",
    "ExportStatus",
    "CompressionType",
    "ExportDestinationType",
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
