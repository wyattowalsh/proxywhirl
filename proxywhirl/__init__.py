"""
ProxyWhirl: Advanced Python Proxy Rotation Library

A production-ready library for intelligent proxy rotation with auto-fetching,
validation, and persistence capabilities.
"""

from __future__ import annotations

from proxywhirl.advanced_logging import (
    LogAggregator,
    LogEntry,
    LogLevel,
    PerformanceMonitor,
    StructuredLogger,
)
from proxywhirl.api_versioning import (
    APICompatibility,
    APIVersion,
    MigrationGuide,
    VersionedEndpoint,
    VersionedResponse,
    VersionRouter,
)
from proxywhirl.audit_trail import AuditAction, AuditEntry, AuditTrail
from proxywhirl.blue_green_deployment import (
    BlueGreenDeployment,
    DeploymentPlan,
    DeploymentStatus,
    EnvironmentColor,
    EnvironmentSnapshot,
)
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
from proxywhirl.cache_optimization import (
    CachePolicy,
    CacheWarmup,
    OptimizedCache,
)
from proxywhirl.canary_deployment import (
    CanaryDeployment,
    CanaryMetrics,
    CanaryPhase,
    TrafficAllocation,
)
from proxywhirl.circuit_breaker import AsyncCircuitBreaker, CircuitBreaker, CircuitBreakerState
from proxywhirl.compression import (
    CompressionAlgorithm,
    CompressionConfig,
    CompressionLevel,
    CompressionManager,
    parse_content_encoding,
)
from proxywhirl.config import DataStorageConfig
from proxywhirl.connection_pooling import (
    ConnectionPool,
    ConnectionPoolManager,
    ConnectionPoolStats,
)
from proxywhirl.credentials_manager import Credential, CredentialsManager
from proxywhirl.custom_headers import (
    HeaderConfig,
    HeaderManager,
    HeaderPolicy,
    HeaderTemplate,
    RateLimitHeaderPolicy,
    SecurityHeaderPolicy,
    UserAgentPolicy,
)
from proxywhirl.data_export import (
    DataExporter,
    ExportFormat,
    FileExporter,
)
from proxywhirl.data_persistence import (
    DataPersistence,
    PersistenceFormat,
    PersistenceMetadata,
)
from proxywhirl.datasource_poller import (
    DatasourcePoller,
    PollingConfig,
    PollingStats,
    PollingStrategy,
)
from proxywhirl.datasource_webhooks import (
    WebhookConfig,
    WebhookEvent,
    WebhookManager,
    WebhookPayload,
)
from proxywhirl.db_backup import BackupInfo, DatabaseBackup
from proxywhirl.db_monitoring import DatabaseMetrics, DatabaseMonitor, QueryPerformance, TableStats
from proxywhirl.deadletter_queue import (
    DeadLetterEntry,
    DeadLetterQueue,
    FailureReason,
)
from proxywhirl.deprecation import (
    DeprecationInfo,
    DeprecationManager,
    deprecated,
    get_deprecation_manager,
)
from proxywhirl.diversity_metrics import (
    DiversityAnalyzer,
    DiversityMetrics,
)
from proxywhirl.docker_compose_config import (
    BuildContext,
    DockerComposeConfig,
    HealthCheck,
    Network,
    Port,
    Service,
    ServiceType,
    Volume,
    VolumeMount,
)
from proxywhirl.error_recovery import (
    CircuitBreakerRecovery,
    ErrorContext,
    ErrorHandler,
    ErrorRecovery,
    RecoveryAction,
    RecoveryStrategy,
)
from proxywhirl.events import (
    Event,
    EventBus,
    EventHandler,
    EventSubscriber,
    EventType,
    get_event_bus,
    set_event_bus,
)
from proxywhirl.exceptions import (
    BrowserRenderError,
    CacheCorruptionError,
    CacheStorageError,
    CacheTierError,
    CacheValidationError,
    CircuitBreakerOpenError,
    EventLoopConflictError,
    GeoIPLookupError,
    MaxRetriesExhaustedError,
    ProxyAuthenticationError,
    ProxyConnectionContextError,
    ProxyConnectionError,
    ProxyFetchError,
    ProxyPoolEmptyError,
    ProxySourceUnavailableError,
    ProxyStorageError,
    ProxyValidationError,
    ProxyValidationPathError,
    ProxyWhirlError,
    RateLimitExceededError,
    RequestQueueFullError,
    SchemaMigrationError,
    StorageRecoveryError,
    TimeoutError,
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
from proxywhirl.health_check import (
    CompositeHealthChecker,
    HealthChecker,
    HealthCheckResult,
    SimpleHealthCheck,
    ThresholdHealthCheck,
)
from proxywhirl.health_check import (
    HealthStatus as HealthCheckStatus,
)
from proxywhirl.helm_chart import (
    ChartDependency,
    ChartMaintainer,
    ChartRenderer,
    HelmChart,
    HelmChartBuilder,
    ValuesConfig,
)
from proxywhirl.k8s_manifests import (
    ConfigMapBuilder,
    Container,
    DeploymentBuilder,
    ManifestGenerator,
    ObjectMeta,
    ResourceKind,
    ResourceRequirements,
    RestartPolicy,
    ServiceBuilder,
)
from proxywhirl.k8s_manifests import (
    ServiceType as K8sServiceType,
)
from proxywhirl.middleware_pipeline import (
    HeaderMiddleware,
    LoggingMiddleware,
    MiddlewareContext,
    MiddlewarePipeline,
    RateLimitMiddleware,
    ValidationMiddleware,
)
from proxywhirl.migration_docs import (
    Migration,
    MigrationDocumenter,
    MigrationRegistry,
    MigrationStatus,
    MigrationType,
    create_migration,
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
from proxywhirl.observability import (
    MetricsCollector,
    ObservabilityContext,
    Span,
    SpanContext,
    Tracer,
)
from proxywhirl.observability_dashboard import (
    Alert,
    AlertLevel,
    DashboardWidget,
    MetricPoint,
    ObservabilityDashboard,
    TimeSeries,
)
from proxywhirl.observability_dashboard import (
    MetricType as DashboardMetricType,
)
from proxywhirl.plugins import (
    HookPlugin,
    MiddlewarePlugin,
    ParserPlugin,
    PluginError,
    PluginInterface,
    PluginLoader,
    PluginRegistry,
    StrategyPlugin,
    get_plugin_registry,
    set_plugin_registry,
)
from proxywhirl.pool_optimizer import (
    OptimizationStrategy,
    PoolOptimizationResult,
    PoolOptimizer,
)
from proxywhirl.proxy_filtering import (
    FilterOperator,
    FilterRule,
    ProxyFilter,
    ProxyGrouping,
    ProxySelector,
)
from proxywhirl.queue_management import (
    PriorityQueue,
    QueueItem,
    QueuePriority,
    RetryQueue,
    RoundRobinQueue,
)
from proxywhirl.request_builder import (
    RequestBuilder,
    ResponseSerializer,
)
from proxywhirl.request_deduplication import (
    DedupDecorator,
    DedupEntry,
    RequestDeduplicator,
)
from proxywhirl.resource_management import (
    ResourceMonitor,
    ResourcePool,
    ResourceQuota,
    ResourceStats,
)
from proxywhirl.response_validation import (
    ResponseContentType,
    ResponseParser,
    ResponseQualityChecker,
    ResponseValidator,
    ValidationRule,
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
from proxywhirl.service_metrics import (
    AlertManager,
    ServiceHealthChecker,
    ServiceMetrics,
)
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
from proxywhirl.statistics_reporter import (
    Metric,
    MetricType,
    StatisticsCollector,
    StatisticsReport,
    StatisticsReporter,
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
from proxywhirl.task_scheduling import (
    CronScheduler,
    Task,
    TaskPriority,
    TaskScheduler,
    TaskStatus,
)
from proxywhirl.types import (
    AsyncHttpRequestCallback,
    CacheEvictionCallback,
    CacheFormat,
    ConfigAction,
    ErrorHandlerCallback,
    HealthCheckCallback,
    HttpRequestCallback,
    LoggingCallback,
    MCPMiddlewareCallback,
    MetricsCallback,
    PerformanceLevel,
    PoolAction,
    Protocol,
    ProxyAddCallback,
    ProxyProtocol,
    ProxyRemoveCallback,
    ProxySelectionCallback,
    ProxyType,
    ProxywhirlAction,
    RetryCallback,
    SessionCallback,
    SessionEvictionCallback,
)
from proxywhirl.types import (
    ValidationLevel as ValidationLevelType,
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
from proxywhirl.validators import (
    is_dead_status,
    is_degraded_status,
    is_health_status,
    is_healthy_proxy,
    is_healthy_proxy_list,
    is_healthy_status,
    is_non_negative,
    is_pool,
    is_positive,
    is_proxy,
    is_proxy_dict,
    is_proxy_list,
    is_session,
    is_success_rate,
    is_valid_host,
    is_valid_port,
    is_valid_proxy,
    is_working_proxy,
)
from proxywhirl.validators import (
    is_valid_proxy_url as is_valid_proxy_url_guard,
)

__version__ = "0.3.3"

__all__: list[str] = [
    # Version
    "__version__",
    # Configuration
    "BootstrapConfig",
    "DataStorageConfig",
    # Audit Trail
    "AuditTrail",
    "AuditEntry",
    "AuditAction",
    # Database Backup
    "DatabaseBackup",
    "BackupInfo",
    # Database Monitoring
    "DatabaseMonitor",
    "DatabaseMetrics",
    "TableStats",
    "QueryPerformance",
    # Migrations
    "Migration",
    "MigrationRegistry",
    "MigrationDocumenter",
    "MigrationStatus",
    "MigrationType",
    "create_migration",
    # Credentials Manager
    "Credential",
    "CredentialsManager",
    # Queue Management
    "QueuePriority",
    "QueueItem",
    "PriorityQueue",
    "RetryQueue",
    "RoundRobinQueue",
    # Resource Management
    "ResourceStats",
    "ResourceQuota",
    "ResourcePool",
    "ResourceMonitor",
    # API Versioning
    "APIVersion",
    "VersionedEndpoint",
    "VersionRouter",
    "APICompatibility",
    "VersionedResponse",
    "MigrationGuide",
    # Data Export
    "ExportFormat",
    "DataExporter",
    "FileExporter",
    # Diversity Metrics
    "DiversityMetrics",
    "DiversityAnalyzer",
    # Task Scheduling
    "TaskStatus",
    "TaskPriority",
    "Task",
    "TaskScheduler",
    "CronScheduler",
    # Docker Compose
    "ServiceType",
    "BuildContext",
    "HealthCheck",
    "Port",
    "VolumeMount",
    "Service",
    "Network",
    "Volume",
    "DockerComposeConfig",
    # Kubernetes Manifests
    "ResourceKind",
    "RestartPolicy",
    "ObjectMeta",
    "ResourceRequirements",
    "Container",
    "DeploymentBuilder",
    "ServiceBuilder",
    "ConfigMapBuilder",
    "ManifestGenerator",
    "K8sServiceType",
    # Helm Charts
    "ChartMaintainer",
    "ChartDependency",
    "HelmChart",
    "HelmValue",
    "ValuesConfig",
    "HelmChartBuilder",
    "ChartRenderer",
    # Observability Dashboard
    "DashboardMetricType",
    "AlertLevel",
    "MetricPoint",
    "TimeSeries",
    "Alert",
    "DashboardWidget",
    "ObservabilityDashboard",
    # Blue-Green Deployment
    "EnvironmentColor",
    "DeploymentStatus",
    "EnvironmentSnapshot",
    "DeploymentPlan",
    "BlueGreenDeployment",
    # Canary Deployment
    "CanaryPhase",
    "TrafficAllocation",
    "CanaryMetrics",
    "CanaryDeployment",
    # Datasource Components
    "DatasourcePoller",
    "PollingConfig",
    "PollingStats",
    "PollingStrategy",
    # Dead-Letter Queue
    "DeadLetterQueue",
    "DeadLetterEntry",
    "FailureReason",
    # Compression
    "CompressionManager",
    "CompressionConfig",
    "CompressionAlgorithm",
    "CompressionLevel",
    "parse_content_encoding",
    # Custom Headers
    "HeaderManager",
    "HeaderConfig",
    "HeaderTemplate",
    "HeaderPolicy",
    "UserAgentPolicy",
    "RateLimitHeaderPolicy",
    "SecurityHeaderPolicy",
    # Webhooks
    "WebhookManager",
    "WebhookConfig",
    "WebhookPayload",
    "WebhookEvent",
    # Deprecation
    "deprecated",
    "DeprecationInfo",
    "DeprecationManager",
    "get_deprecation_manager",
    # Health Checks
    "HealthCheckStatus",
    "HealthCheckResult",
    "HealthChecker",
    "CompositeHealthChecker",
    "SimpleHealthCheck",
    "ThresholdHealthCheck",
    # Request Deduplication
    "RequestDeduplicator",
    "DedupEntry",
    "DedupDecorator",
    # Response Validation
    "ResponseValidator",
    "ResponseParser",
    "ResponseQualityChecker",
    "ResponseContentType",
    "ValidationRule",
    # Statistics Reporting
    "StatisticsCollector",
    "StatisticsReporter",
    "StatisticsReport",
    "Metric",
    "MetricType",
    # Pool Optimization
    "PoolOptimizer",
    "PoolOptimizationResult",
    "OptimizationStrategy",
    # Connection Pooling
    "ConnectionPool",
    "ConnectionPoolManager",
    "ConnectionPoolStats",
    # Proxy Filtering
    "ProxyFilter",
    "FilterOperator",
    "FilterRule",
    "ProxySelector",
    "ProxyGrouping",
    # Request Building
    "RequestBuilder",
    "ResponseSerializer",
    # Error Recovery
    "ErrorHandler",
    "ErrorRecovery",
    "ErrorContext",
    "RecoveryAction",
    "RecoveryStrategy",
    "CircuitBreakerRecovery",
    # Cache Optimization
    "OptimizedCache",
    "CacheWarmup",
    "CachePolicy",
    "CacheEntry",
    "CacheStatistics",
    # Advanced Logging
    "StructuredLogger",
    "LogLevel",
    "LogEntry",
    "PerformanceMonitor",
    "LogAggregator",
    # Data Persistence
    "DataPersistence",
    "PersistenceFormat",
    "PersistenceMetadata",
    # Service Metrics
    "ServiceMetrics",
    "ServiceHealthChecker",
    "MetricsCollector",
    "AlertManager",
    # Middleware Pipeline
    "MiddlewarePipeline",
    "MiddlewareContext",
    "HeaderMiddleware",
    "RateLimitMiddleware",
    "ValidationMiddleware",
    "LoggingMiddleware",
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
    # Plugin System
    "PluginInterface",
    "PluginError",
    "StrategyPlugin",
    "ParserPlugin",
    "MiddlewarePlugin",
    "HookPlugin",
    "PluginRegistry",
    "PluginLoader",
    "get_plugin_registry",
    "set_plugin_registry",
    # Event System
    "Event",
    "EventBus",
    "EventType",
    "EventHandler",
    "EventSubscriber",
    "get_event_bus",
    "set_event_bus",
    # Observability
    "Tracer",
    "Span",
    "SpanContext",
    "MetricsCollector",
    "ObservabilityContext",
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
    "RateLimitExceededError",
    "MaxRetriesExhaustedError",
    "CircuitBreakerOpenError",
    "ProxyConnectionContextError",
    "CacheTierError",
    "ProxyValidationPathError",
    "GeoIPLookupError",
    "BrowserRenderError",
    "ProxySourceUnavailableError",
    "EventLoopConflictError",
    "SchemaMigrationError",
    "TimeoutError",
    "StorageRecoveryError",
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
    # TypeGuard Validators
    "is_valid_proxy",
    "is_healthy_proxy",
    "is_working_proxy",
    "is_pool",
    "is_session",
    "is_valid_proxy_url_guard",
    "is_valid_host",
    "is_valid_port",
    "is_valid_proxy",
    "is_health_status",
    "is_healthy_status",
    "is_degraded_status",
    "is_dead_status",
    "is_proxy",
    "is_proxy_list",
    "is_healthy_proxy_list",
    "is_proxy_dict",
    "is_success_rate",
    "is_non_negative",
    "is_positive",
    # Type Aliases (String Literals)
    "PoolAction",
    "ConfigAction",
    "ProxywhirlAction",
    "LogLevel",
    "CacheFormat",
    "Protocol",
    "ProxyProtocol",
    "ProxyType",
    "ValidationLevelType",
    "PerformanceLevel",
    # Type Aliases (Callbacks)
    "HttpRequestCallback",
    "AsyncHttpRequestCallback",
    "CacheEvictionCallback",
    "ProxyAddCallback",
    "ProxyRemoveCallback",
    "ProxySelectionCallback",
    "HealthCheckCallback",
    "SessionCallback",
    "SessionEvictionCallback",
    "RetryCallback",
    "ErrorHandlerCallback",
    "MetricsCallback",
    "LoggingCallback",
    "MCPMiddlewareCallback",
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
