"""proxywhirl -- Python 3.13+ library for rotating proxy management"""

# Modern cache system imports
from proxywhirl.caches import (  # TODO: Add SQLite cache classes when implemented; AsyncSQLiteProxyCache,; SQLiteProxyCache,
    BaseProxyCache,
    CacheFilters,
    CacheMetrics,
    JsonProxyCache,
    MemoryProxyCache,
)
from proxywhirl.caches import CacheType
from proxywhirl.config import LoaderConfig, ProxyWhirlSettings
from proxywhirl.logger import configure_rich_logging, get_logger, setup_logger
from proxywhirl.models import (
    AnonymityLevel,
    Proxy,
    ProxyError,
    ProxyScheme,
    ProxySourceError,
    ProxyValidationError,
    RotationStrategy,
    Scheme,
)
from proxywhirl.proxywhirl import ProxyWhirl
from proxywhirl.rotator import ProxyRotator
from proxywhirl.utils import normalize_proxy_url, validate_ip
from proxywhirl.validator import (
    CircuitBreaker,
    CircuitBreakerOpenError,
    ProxyValidator,
    QualityLevel,
    ValidationResult,
    ValidationSummary,
)

# Legacy alias for backward compatibility
ProxyWhirlClient = ProxyWhirl

# TUI functionality (optional import)
try:
    from proxywhirl.tui import ProxyWhirlTUI, run_tui

    __all_tui__ = ["ProxyWhirlTUI", "run_tui"]
except ImportError:
    __all_tui__ = []

__version__ = "0.1.0"
__all__ = [
    "ProxyWhirl",
    "ProxyWhirlClient",
    # Modern cache system exports
    "BaseProxyCache",
    "MemoryProxyCache",
    "JsonProxyCache",
    # TODO: Add SQLite cache classes when implemented
    # "SQLiteProxyCache",
    # "AsyncSQLiteProxyCache",
    "CacheFilters",
    "CacheMetrics",
    "ProxyRotator",
    "ProxyValidator",
    "CircuitBreaker",
    "CircuitBreakerOpenError",
    "ValidationResult",
    "ValidationSummary",
    "QualityLevel",
    "LoaderConfig",
    "ProxyWhirlSettings",
    "setup_logger",
    "get_logger",
    "configure_rich_logging",
    "AnonymityLevel",
    "CacheType",
    "Proxy",
    "ProxyError",
    "ProxySourceError",
    "ProxyValidationError",
    "RotationStrategy",
    "Scheme",
    "ProxyScheme",
    "normalize_proxy_url",
    "validate_ip",
] + __all_tui__
