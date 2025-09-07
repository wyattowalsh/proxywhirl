"""proxywhirl -- Python 3.13+ library for rotating proxy management"""

# Initialize the enhanced logger first (auto-configures loguru + rich)
import proxywhirl.logger  # This auto-configures the enhanced logger

# Import core models first to avoid circular imports  
# Modern cache system imports (after models to avoid circular imports)
from proxywhirl.caches import (
    BaseProxyCache,
    CacheFilters,
    CacheMetrics,
    CacheType,
    JsonProxyCache,
    MemoryProxyCache,
)

# Configuration and logging
from proxywhirl.config import LoaderConfig, ProxyWhirlSettings
from proxywhirl.logger import (
    Environment,
    LogLevel,
    bind_context,
    bind_context_async,
    catch_and_log,
    configure_rich_logging,
    get_logger,
    log_api_request,
    log_cache_operation,
    log_operation,
    log_operation_async,
    log_performance,
    log_proxy_operation,
    log_validation_result,
    setup_logger,
)
from proxywhirl.models import Proxy, Scheme

# Core functionality
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
ProxyScheme = Scheme  # Legacy compatibility

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
    "CacheFilters",
    "CacheMetrics",
    "CacheType",
    "ProxyRotator",
    "ProxyValidator",
    "CircuitBreaker",
    "CircuitBreakerOpenError", 
    "ValidationResult",
    "ValidationSummary",
    "QualityLevel",
    "LoaderConfig",
    "ProxyWhirlSettings",
    # Enhanced logger exports
    "setup_logger",
    "get_logger",
    "configure_rich_logging",
    "log_performance",
    "catch_and_log",
    "log_operation",
    "log_operation_async",
    "bind_context", 
    "bind_context_async",
    "log_proxy_operation",
    "log_api_request",
    "log_cache_operation",
    "log_validation_result",
    "LogLevel",
    "Environment",
    # Models
    "Proxy",
    "Scheme", 
    "ProxyScheme",
    # Utils
    "normalize_proxy_url",
    "validate_ip",
] + __all_tui__
