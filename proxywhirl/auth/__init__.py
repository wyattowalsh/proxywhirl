"""
Authentication and authorization module for ProxyWhirl.

Provides:
- API key authentication
- Per-key rate limiting
- Webhook request signing/verification
"""

from __future__ import annotations

from .api_key import APIKey, APIKeyManager, APIKeyRotation
from .rate_limiter import KeyRateLimiter, RateLimitQuota
from .signing import WebhookSigner, WebhookVerifier

__all__ = [
    "APIKey",
    "APIKeyManager",
    "APIKeyRotation",
    "KeyRateLimiter",
    "RateLimitQuota",
    "WebhookSigner",
    "WebhookVerifier",
]
