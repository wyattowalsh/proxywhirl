"""proxywhirl -- Python 3.13+ library for rotating proxy management"""

from proxywhirl.cache import ProxyCache
from proxywhirl.models import (
    AnonymityLevel,
    CacheType,
    CoreProxy,
    Proxy,
    ProxyError,
    ProxySourceError,
    ProxyValidationError,
    RotationStrategy,
    Scheme,
)
from proxywhirl.proxywhirl import ProxyWhirl
from proxywhirl.rotator import ProxyRotator
from proxywhirl.validator import (
    CircuitBreaker,
    CircuitBreakerOpenError,
    ProxyValidator,
    ValidationResult,
    ValidationSummary,
)

# Legacy alias for backward compatibility
ProxyWhirlClient = ProxyWhirl

__version__ = "0.1.0"
__all__ = [
    "ProxyWhirl",
    "ProxyWhirlClient",
    "ProxyCache",
    "ProxyRotator",
    "ProxyValidator",
    "CircuitBreaker",
    "CircuitBreakerOpenError",
    "ValidationResult",
    "ValidationSummary",
    "CoreProxy",
    "Proxy",
    "AnonymityLevel",
    "Scheme",
    "CacheType",
    "RotationStrategy",
    "ProxyError",
    "ProxySourceError",
    "ProxyValidationError",
]
