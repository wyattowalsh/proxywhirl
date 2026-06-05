"""Contract snapshots for the focused ProxyWhirl restructuring.

These snapshots pin the current model/API/MCP output shapes before pruning and
moving modules. They intentionally use deterministic values so later refactors
can change internals without accidentally changing user-visible payloads.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from inspect import signature
from typing import Any, cast, get_args
from uuid import UUID

import pytest

from proxywhirl.api.models import (
    APIResponse,
    ErrorCode,
    ErrorDetail,
    HealthResponse,
    MetaInfo,
    PaginatedResponse,
    ProxiedResponse,
    ProxyPoolStats,
    ProxyResource,
    StatusResponse,
)
from proxywhirl.cache.models import CacheConfig, CacheEntry
from proxywhirl.fetchers import ValidationResult
from proxywhirl.mcp.server import (
    ProxywhirlAction,
    _get_proxy_config_impl,
    _get_proxy_health_impl,
    _proxy_selection_workflow_prompt,
    _proxywhirl_tool,
    _troubleshooting_workflow_prompt,
)
from proxywhirl.mcp.server import (
    proxywhirl as registered_proxywhirl_tool,
)
from proxywhirl.models import (
    HealthStatus,
    Proxy,
    ProxyFormat,
    ProxyPool,
    ProxySource,
    ProxySourceConfig,
    RenderMode,
    Session,
    SourceStats,
)

FIXED_NOW = datetime(2026, 5, 22, 12, 0, 0, tzinfo=timezone.utc)
FIXED_UUID = UUID("12345678-1234-5678-1234-567812345678")
EXPECTED_MCP_ACTIONS = (
    "list",
    "rotate",
    "status",
    "recommend",
    "health",
    "reset_cb",
    "add",
    "remove",
    "fetch",
    "validate",
    "set_strategy",
)


def _dump(value: Any) -> object:
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    return value


@pytest.mark.snapshot
def test_core_model_output_contracts(snapshot) -> None:
    proxy = Proxy(
        id=FIXED_UUID,
        url="http://proxy.example.com:8080",
        protocol="http",
        health_status=HealthStatus.HEALTHY,
        last_success_at=FIXED_NOW,
        total_requests=12,
        total_successes=11,
        total_failures=1,
        average_response_time_ms=123.45,
        latency_ms=111.0,
        country_code="US",
        tags={"free"},
        source=ProxySource.FETCHED,
        source_url=cast(Any, "https://sources.example.com/list.txt"),
        created_at=FIXED_NOW,
        updated_at=FIXED_NOW,
    )
    pool = ProxyPool(
        id=FIXED_UUID,
        name="contract-pool",
        proxies=[proxy],
        max_pool_size=10,
        created_at=FIXED_NOW,
        updated_at=FIXED_NOW,
    )
    session = Session(
        session_id="session-1",
        proxy_id=str(FIXED_UUID),
        created_at=FIXED_NOW,
        expires_at=FIXED_NOW + timedelta(minutes=5),
        last_used_at=FIXED_NOW,
        request_count=3,
    )
    source = ProxySourceConfig(
        url=cast(Any, "https://sources.example.com/list.txt"),
        format=ProxyFormat.PLAIN_TEXT,
        render_mode=RenderMode.STATIC,
        protocol="http",
        refresh_interval=600,
        enabled=True,
        priority=10,
        trusted=False,
        metadata={"owner": "contract"},
    )
    stats = SourceStats(
        source_url="https://sources.example.com/list.txt",
        total_fetched=20,
        valid_count=15,
        invalid_count=5,
        last_fetch_at=FIXED_NOW,
        last_fetch_duration_ms=42.5,
        fetch_failure_count=1,
        last_error="timeout",
    )
    cache_entry = CacheEntry(
        key="proxy:contract",
        proxy_url="http://proxy.example.com:8080",
        username=None,
        password=None,
        source="contract-source",
        fetch_time=FIXED_NOW,
        last_accessed=FIXED_NOW,
        access_count=2,
        ttl_seconds=3600,
        expires_at=FIXED_NOW + timedelta(hours=1),
        health_status=HealthStatus.HEALTHY,
        last_health_check=None,
        next_check_time=None,
        last_health_error=None,
    )

    assert {
        "proxy": _dump(proxy),
        "pool": _dump(pool),
        "session": _dump(session),
        "source": _dump(source),
        "source_stats": _dump(stats),
        "cache_config": _dump(CacheConfig(encryption_key=None)),
        "cache_entry": _dump(cache_entry),
        "validation_result": ValidationResult(True, 87.5)._asdict(),
    } == snapshot


@pytest.mark.snapshot
def test_api_response_body_contracts(snapshot) -> None:
    meta = MetaInfo(
        request_id="contract-request",
        timestamp=FIXED_NOW,
        version="1.0.0",
    )
    proxy_resource = ProxyResource(
        id=str(FIXED_UUID),
        url="http://proxy.example.com:8080",
        protocol="http",
        status="healthy",
        health="healthy",
        stats={
            "total_requests": 12,
            "successful_requests": 11,
            "failed_requests": 1,
            "avg_latency_ms": 123.45,
        },
        created_at=FIXED_NOW,
        updated_at=FIXED_NOW,
    )

    assert {
        "health": _dump(
            HealthResponse(
                status="healthy",
                uptime_seconds=60,
                version="1.0.0",
                timestamp=FIXED_NOW,
            )
        ),
        "status": _dump(
            StatusResponse(
                pool_stats=ProxyPoolStats(
                    total=1,
                    active=1,
                    failed=0,
                    healthy_percentage=100.0,
                    last_rotation=FIXED_NOW,
                ),
                rotation_strategy="round-robin",
                storage_backend="memory",
                config_source="defaults",
            )
        ),
        "proxies": _dump(
            APIResponse[PaginatedResponse[ProxyResource]].success(
                PaginatedResponse[ProxyResource](
                    items=[proxy_resource],
                    total=1,
                    page=1,
                    page_size=20,
                    has_next=False,
                    has_prev=False,
                ),
                meta=meta,
            )
        ),
        "request": _dump(
            APIResponse[ProxiedResponse].success(
                ProxiedResponse(
                    status_code=200,
                    headers={"content-type": "application/json"},
                    body='{"ok": true}',
                    proxy_used="http://proxy.example.com:8080",
                    elapsed_ms=125,
                ),
                meta=meta,
            )
        ),
        "error": _dump(
            APIResponse[object](
                status="error",
                data=None,
                error=ErrorDetail(
                    code=ErrorCode.PROXY_POOL_EMPTY,
                    message="No proxies available in the pool",
                    details={"available_proxies": 0},
                    timestamp=FIXED_NOW,
                ),
                meta=meta,
            )
        ),
    } == snapshot


@pytest.mark.snapshot
async def test_mcp_structured_output_contracts(snapshot, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PROXYWHIRL_MCP_ALLOW_UNAUTHENTICATED_WRITES", "true")

    assert {
        "status_requires_proxy_id": await _proxywhirl_tool(action="status"),
        "add_requires_proxy_url": await _proxywhirl_tool(action="add"),
        "set_strategy_requires_strategy": await _proxywhirl_tool(action="set_strategy"),
        "unknown_action": await _proxywhirl_tool(action="unknown"),  # type: ignore[arg-type]
        "selection_prompt": (await _proxy_selection_workflow_prompt()).splitlines(),
    } == snapshot


async def test_mcp_registered_surface_contract() -> None:
    """MCP exposes the curated action set without model-visible credentials."""
    tool_signature = signature(registered_proxywhirl_tool)

    assert get_args(ProxywhirlAction) == EXPECTED_MCP_ACTIONS
    assert "api_key" not in tool_signature.parameters
    assert "proxy_id" in tool_signature.parameters
    assert "proxy_url" in tool_signature.parameters
    assert "strategy" in tool_signature.parameters

    assert callable(_get_proxy_health_impl)
    assert callable(_get_proxy_config_impl)
    assert "# Proxy Selection Workflow" in await _proxy_selection_workflow_prompt()
    assert "# Proxy Troubleshooting Workflow" in await _troubleshooting_workflow_prompt()
