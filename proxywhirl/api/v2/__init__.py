"""ProxyWhirl API v2 - Enhanced REST API with breaking changes.

v2 Features:
- Structured request/response envelopes with metadata
- Per-API-key rate limiting
- Webhook signing and verification
- Streaming responses (SSE, NDJSON, CSV)
- Distributed tracing support
- Async-first design
"""

from proxywhirl.api.v2.auth import (
    APIKeyAuth,
    KeyRotationPolicy,
    RateLimitKey,
    WebhookSignature,
    WebhookSigner,
    create_api_key,
)
from proxywhirl.api.v2.core import app
from proxywhirl.api.v2.models import (
    APIResponse,
    ErrorCode,
    ErrorDetail,
    PaginatedResponse,
    ProxyResourceV2,
    RateLimitInfo,
    RequestMetadata,
    ResponseMetadata,
    StreamingOptions,
)
from proxywhirl.api.v2.streaming import (
    ChunkedResponse,
    StreamingFormatter,
    stream_proxies,
)

__all__ = [
    "app",
    "APIResponse",
    "ErrorCode",
    "ErrorDetail",
    "PaginatedResponse",
    "ProxyResourceV2",
    "RateLimitInfo",
    "RequestMetadata",
    "ResponseMetadata",
    "StreamingOptions",
    "APIKeyAuth",
    "KeyRotationPolicy",
    "RateLimitKey",
    "WebhookSignature",
    "WebhookSigner",
    "create_api_key",
    "ChunkedResponse",
    "StreamingFormatter",
    "stream_proxies",
]
