"""ProxyWhirl CLI (thin package entry).

Console script entry: ``proxywhirl.cli:app``.
"""

from __future__ import annotations

import socket

from proxywhirl.cli._impl import (
    CommandContext,
    _proxy_reference_matches,
    app,
    config,
    config_app,
    export,
    fetch,
    get_context,
    health,
    import_proxies,
    main,
    pool,
    pool_app,
    render_csv,
    render_json,
    render_output,
    render_text,
    render_yaml,
    request,
    sources,
    validate_proxy,
    validate_target_url,
)
from proxywhirl.config import load_config

__all__ = [
    "CommandContext",
    "_proxy_reference_matches",
    "app",
    "config",
    "config_app",
    "export",
    "fetch",
    "get_context",
    "health",
    "import_proxies",
    "load_config",
    "main",
    "pool",
    "pool_app",
    "render_csv",
    "render_json",
    "render_output",
    "render_text",
    "render_yaml",
    "request",
    "socket",
    "sources",
    "validate_proxy",
    "validate_target_url",
]
