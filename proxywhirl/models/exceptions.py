"""proxywhirl/models/exceptions.py -- Exception types for ProxyWhirl

This module contains all exception types used throughout ProxyWhirl for
comprehensive error handling and type safety.

Features:
- Base exception hierarchy for proxy-related errors
- Specific exceptions for different error scenarios
- Type-safe error handling patterns
"""

from __future__ import annotations


class ProxyError(Exception):
    """Base exception for all proxy-related errors."""


class ProxyValidationError(ProxyError):
    """Error during proxy validation or health checking."""


class ProxySourceError(ProxyError):
    """Error loading proxies from a source."""


class ProxyConfigError(ProxyError):
    """Error in proxy configuration."""
