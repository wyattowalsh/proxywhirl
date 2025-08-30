"""proxywhirl -- Python 3.13+ library for rotating proxy management"""

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
from proxywhirl.logger import configure_rich_logging, get_logger, setup_logger
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
    "setup_logger",
    "get_logger",
    "configure_rich_logging",
    "Proxy",
    "Scheme", 
    "ProxyScheme",
    "normalize_proxy_url",
    "validate_ip",
] + __all_tui__

# For now, avoid complex imports due to circular dependency issues with models/ package
# Users can import specific modules directly: from proxywhirl.proxywhirl import ProxyWhirl

__version__ = "0.1.0"

# Primary exports that don't cause circular imports
from proxywhirl.proxywhirl import ProxyWhirl

# Legacy alias for backward compatibility  
ProxyWhirlClient = ProxyWhirl

# TUI functionality (optional import)
try:
    from proxywhirl.tui import ProxyWhirlTUI, run_tui

    __all_tui__ = ["ProxyWhirlTUI", "run_tui"]
except ImportError:
    __all_tui__ = []

__all__ = [
    "ProxyWhirl",
    "ProxyWhirlClient",
] + __all_tui__
