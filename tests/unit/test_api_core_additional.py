"""Additional unit tests for API core coverage."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from fastapi import HTTPException, Request, Response
from fastapi.testclient import TestClient

from proxywhirl.api import app
from proxywhirl.api import core as api_core
from proxywhirl.api.models import (
    CreateProxyRequest,
    HealthCheckRequest,
    HealthCheckResult,
    ProxiedRequest,
    RetryPolicyRequest,
    UpdateConfigRequest,
)
from proxywhirl.exceptions import ProxyValidationError
from proxywhirl.models import HealthStatus, Proxy
from proxywhirl.retry import RetryPolicy


@pytest.fixture
def client() -> TestClient:
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_api_state() -> None:
    """Reset API globals between tests to avoid cross-test pollution."""
    api_core._rotator = None
    api_core._storage = None
    api_core._config = {}
    yield
    api_core._rotator = None
    api_core._storage = None
    api_core._config = {}


class DummyRetryMetrics:
    """Minimal retry metrics stub for API endpoints."""

    def __init__(
        self,
        summary: dict[str, object],
        timeseries: list[dict[str, object]],
        by_proxy: dict[str, dict[str, object]],
        events: list[object] | None = None,
    ) -> None:
        self._summary = summary
        self._timeseries = timeseries
        self._by_proxy = by_proxy
        self.circuit_breaker_events = events or []

    def get_summary(self) -> dict[str, object]:
        return self._summary

    def get_timeseries(self, *, hours: int = 24) -> list[dict[str, object]]:
        return self._timeseries

    def get_by_proxy(self, *, hours: int = 24) -> dict[str, dict[str, object]]:
        return self._by_proxy


def _make_request(
    *,
    path: str = "/test",
    method: str = "GET",
    headers: dict[str, str] | None = None,
    query_string: str = "",
) -> Request:
    raw_headers = [(key.lower().encode(), value.encode()) for key, value in (headers or {}).items()]
    scope = {
        "type": "http",
        "method": method,
        "path": path,
        "headers": raw_headers,
        "query_string": query_string.encode(),
        "client": ("127.0.0.1", 12345),
        "server": ("testserver", 80),
        "scheme": "http",
    }
    return Request(scope)


def test_validate_proxied_request_url_rejects_private() -> None:
    """Invalid target URLs should raise HTTPException."""
    request_data = ProxiedRequest(url="http://127.0.0.1", method="GET")
    with pytest.raises(HTTPException) as exc_info:
        api_core.validate_proxied_request_url(request_data)
    assert exc_info.value.status_code == 400


def test_validate_proxied_request_url_allows_public() -> None:
    """Valid public URLs should pass validation."""
    request_data = ProxiedRequest(url="https://example.com", method="GET")
    assert api_core.validate_proxied_request_url(request_data) is request_data


@pytest.mark.asyncio
async def test_lifespan_initializes_and_saves(tmp_path, monkeypatch) -> None:
    """Lifespan should initialize storage/rotator and save on shutdown."""
    db_path = tmp_path / "proxywhirl.db"
    monkeypatch.setenv("PROXYWHIRL_STORAGE_PATH", str(db_path))
    monkeypatch.setenv("PROXYWHIRL_CORS_ORIGINS", "http://example.com, ,")

    proxy = Proxy(url="http://proxy.example.com:8080")
    with patch.object(api_core.SQLiteStorage, "load", AsyncMock(return_value=[proxy])) as load_mock:
        with patch.object(api_core.SQLiteStorage, "save", AsyncMock()) as save_mock:
            async with api_core.lifespan(app):
                assert api_core._rotator is not None
                assert api_core._storage is not None
                assert api_core._rotator.pool.size == 1
                assert api_core._config["cors_origins"] == ["http://example.com"]
            load_mock.assert_awaited_once()
            save_mock.assert_awaited_once()


@pytest.mark.asyncio
async def test_lifespan_handles_load_failure(tmp_path, monkeypatch) -> None:
    """Lifespan should continue when storage load fails."""
    db_path = tmp_path / "proxywhirl.db"
    monkeypatch.setenv("PROXYWHIRL_STORAGE_PATH", str(db_path))

    with patch.object(api_core.SQLiteStorage, "load", AsyncMock(side_effect=RuntimeError("boom"))):
        async with api_core.lifespan(app):
            assert api_core._rotator is not None


def test_update_prometheus_metrics_no_rotator() -> None:
    """No rotator should cause metrics update to no-op."""
    api_core._rotator = None
    api_core.update_prometheus_metrics()


def test_update_prometheus_metrics_updates_states() -> None:
    """Metrics update should handle OPEN/HALF_OPEN states."""
    rotator = MagicMock()
    rotator.pool.size = 2
    rotator.pool.healthy_count = 1

    class DummyCB:
        def __init__(self, value: str) -> None:
            self.state = SimpleNamespace(value=value)

    rotator.get_circuit_breaker_states.return_value = {
        "proxy1": DummyCB("OPEN"),
        "proxy2": DummyCB("HALF_OPEN"),
    }
    api_core._rotator = rotator
    api_core.update_prometheus_metrics()


def test_update_prometheus_metrics_handles_exception() -> None:
    """Metrics update should swallow circuit breaker errors."""
    rotator = MagicMock()
    rotator.pool.size = 1
    rotator.pool.healthy_count = 1
    rotator.get_circuit_breaker_states.side_effect = RuntimeError("boom")
    api_core._rotator = rotator
    api_core.update_prometheus_metrics()


def _mock_rotator_with_proxy() -> MagicMock:
    rotator = MagicMock()
    rotator.pool = MagicMock()
    rotator.strategy = MagicMock()
    rotator.strategy.select.return_value = Proxy(url="http://proxy.example.com:8080")
    return rotator


def test_request_endpoint_success(client: TestClient) -> None:
    """Successful proxied request should return APIResponse success."""
    rotator = _mock_rotator_with_proxy()
    response = httpx.Response(200, text="ok", headers={"X-Test": "1"})

    with patch("proxywhirl.api.core._rotator", rotator):
        with patch(
            "proxywhirl.api.core.httpx.AsyncClient.request", AsyncMock(return_value=response)
        ):
            result = client.post(
                "/api/v1/request",
                json={"url": "https://example.com", "method": "GET"},
            )

    assert result.status_code == 200
    body = result.json()
    assert body["status"] == "success"
    assert body["data"]["status_code"] == 200


def test_request_endpoint_no_proxies(client: TestClient) -> None:
    """No proxies should return 500 due to catch-all handler."""
    rotator = _mock_rotator_with_proxy()
    rotator.strategy.select.return_value = None

    with patch("proxywhirl.api.core._rotator", rotator):
        result = client.post(
            "/api/v1/request",
            json={"url": "https://example.com", "method": "GET"},
        )

    assert result.status_code == 500


def test_request_endpoint_proxy_error_retries(client: TestClient) -> None:
    """Proxy errors should retry and eventually return 502."""
    rotator = _mock_rotator_with_proxy()

    with patch("proxywhirl.api.core._rotator", rotator):
        with patch(
            "proxywhirl.api.core.httpx.AsyncClient.request",
            AsyncMock(side_effect=httpx.ProxyError("boom")),
        ):
            result = client.post(
                "/api/v1/request",
                json={"url": "https://example.com", "method": "GET"},
            )

    assert result.status_code == 502


def test_request_endpoint_unexpected_error(client: TestClient) -> None:
    """Unexpected errors should return 500."""
    rotator = _mock_rotator_with_proxy()

    with patch("proxywhirl.api.core._rotator", rotator):
        with patch(
            "proxywhirl.api.core.httpx.AsyncClient.request",
            AsyncMock(side_effect=RuntimeError("boom")),
        ):
            result = client.post(
                "/api/v1/request",
                json={"url": "https://example.com", "method": "GET"},
            )

    assert result.status_code == 500


def test_list_proxies_filters(client: TestClient) -> None:
    """List proxies should apply status filters and pagination."""
    rotator = MagicMock()
    proxy_healthy = Proxy(url="http://proxy1.example.com:8080", health_status=HealthStatus.HEALTHY)
    proxy_unhealthy = Proxy(
        url="http://proxy2.example.com:8080", health_status=HealthStatus.UNHEALTHY
    )
    rotator.pool.get_all_proxies.return_value = [proxy_healthy, proxy_unhealthy]

    class DummyCB:
        def __init__(self, value: str) -> None:
            self.state = SimpleNamespace(value=value)

    rotator.get_circuit_breaker_states.return_value = {
        api_core._get_proxy_id(proxy_unhealthy): DummyCB("OPEN")
    }

    with patch("proxywhirl.api.core._rotator", rotator):
        result = client.get("/api/v1/proxies", params={"status_filter": "active", "page": 1})

    assert result.status_code == 200
    body = result.json()
    items = body["data"]["items"]
    assert len(items) == 1
    assert items[0]["health"] == "healthy"


def test_list_proxies_invalid_pagination(client: TestClient) -> None:
    """Invalid pagination should return 400."""
    rotator = MagicMock()
    rotator.pool.get_all_proxies.return_value = []
    rotator.get_circuit_breaker_states.return_value = {}

    with patch("proxywhirl.api.core._rotator", rotator):
        bad_page = client.get("/api/v1/proxies", params={"page": 0})
        bad_size = client.get("/api/v1/proxies", params={"page_size": 101})

    assert bad_page.status_code == 400
    assert bad_size.status_code == 400


@pytest.mark.asyncio
async def test_add_proxy_success_and_duplicate() -> None:
    """Add proxy should handle success and duplicate conflict."""
    rotator = MagicMock()
    rotator.pool.get_all_proxies.return_value = []

    request = SimpleNamespace()
    proxy_data = CreateProxyRequest(url="http://proxy.example.com:8080")

    created = await api_core.add_proxy.__wrapped__(request, proxy_data, rotator, None)
    assert created.status == "success"

    rotator.pool.get_all_proxies.return_value = [Proxy(url="http://proxy.example.com:8080")]
    with pytest.raises(HTTPException) as exc_info:
        await api_core.add_proxy.__wrapped__(request, proxy_data, rotator, None)
    assert exc_info.value.status_code == 409


@pytest.mark.asyncio
async def test_add_proxy_error_path() -> None:
    """Add proxy should return 400 on unexpected errors."""
    rotator = MagicMock()
    rotator.pool.get_all_proxies.return_value = []
    rotator.add_proxy.side_effect = ValueError("boom")

    request = SimpleNamespace()
    proxy_data = CreateProxyRequest(url="http://proxy.example.com:8080")

    with pytest.raises(HTTPException) as exc_info:
        await api_core.add_proxy.__wrapped__(request, proxy_data, rotator, None)
    assert exc_info.value.status_code == 400


def test_get_rotator_raises_when_uninitialized() -> None:
    """get_rotator should raise when rotator is not set."""
    with pytest.raises(HTTPException) as exc_info:
        api_core.get_rotator()
    assert exc_info.value.status_code == 503


@pytest.mark.asyncio
async def test_request_id_middleware_sets_header() -> None:
    """Request ID middleware should preserve provided request ID."""
    middleware = api_core.RequestIDMiddleware(app)
    request = _make_request(headers={"X-Request-ID": "req-123"})

    async def call_next(_: Request) -> Response:
        return Response("ok")

    response = await middleware.dispatch(request, call_next)
    assert response.headers["X-Request-ID"] == "req-123"


@pytest.mark.asyncio
async def test_security_headers_middleware_adds_headers() -> None:
    """Security headers middleware should add expected headers."""
    middleware = api_core.SecurityHeadersMiddleware(app)
    request = _make_request()

    async def call_next(_: Request) -> Response:
        return Response("ok")

    response = await middleware.dispatch(request, call_next)
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"


@pytest.mark.asyncio
async def test_request_logging_middleware_exception_path() -> None:
    """Request logging middleware should re-raise exceptions."""
    middleware = api_core.RequestLoggingMiddleware(app)
    request = _make_request(path="/boom", query_string="token=secret")

    async def call_next(_: Request) -> Response:
        raise RuntimeError("boom")

    with pytest.raises(RuntimeError):
        await middleware.dispatch(request, call_next)


@pytest.mark.asyncio
async def test_not_found_handler_returns_error() -> None:
    """404 handler should return structured error response."""
    request = _make_request(path="/missing")
    response = await api_core.not_found_handler(request, None)
    payload = json.loads(response.body.decode())
    assert response.status_code == 404
    assert payload["status"] == "error"
    assert "Endpoint not found" in payload["error"]["message"]


@pytest.mark.asyncio
async def test_validation_error_handler_formats_details() -> None:
    """Validation handler should convert errors to readable messages."""
    request = _make_request(path="/api/v1/request")

    class DummyValidationError:
        def errors(self) -> list[dict[str, object]]:
            return [
                {
                    "loc": ["body", "url"],
                    "msg": "Value error, invalid url",
                    "type": "value_error",
                }
            ]

    response = await api_core.validation_error_handler(request, DummyValidationError())
    payload = json.loads(response.body.decode())
    assert response.status_code == 400
    assert payload["error"]["details"]["errors"][0]["field"] == "body -> url"


@pytest.mark.asyncio
async def test_internal_error_handler() -> None:
    """Internal error handler should return 500 response."""
    request = _make_request(path="/api/v1/request")
    response = await api_core.internal_error_handler(request, RuntimeError("boom"))
    assert response.status_code == 500


@pytest.mark.asyncio
async def test_proxy_error_handler_maps_status() -> None:
    """Proxy error handler should map known error types to status codes."""
    request = _make_request(path="/api/v1/request")
    exc = ProxyValidationError("Bad proxy URL", proxy_url="http://user:pass@proxy:8080")
    response = await api_core.proxy_error_handler(request, exc)
    payload = json.loads(response.body.decode())
    assert response.status_code == 400
    assert payload["error"]["code"] == "PROXY_ERROR"


@pytest.mark.asyncio
async def test_check_proxy_health_success(monkeypatch) -> None:
    """Proxy health check should return working on success."""
    proxy = Proxy(url="http://proxy.example.com:8080")

    class DummyClient:
        def __init__(self, **_: object) -> None:
            pass

        async def __aenter__(self) -> DummyClient:
            return self

        async def __aexit__(self, *_: object) -> None:
            return None

        async def get(self, _: str) -> httpx.Response:
            return httpx.Response(200, text="ok")

    monkeypatch.setattr(api_core.httpx, "AsyncClient", DummyClient)
    result = await api_core._check_proxy_health(proxy, "https://example.com")
    assert result.status == "working"


@pytest.mark.asyncio
async def test_check_proxy_health_failure(monkeypatch) -> None:
    """Proxy health check should report failures on exceptions."""
    proxy = Proxy(url="http://proxy.example.com:8080")

    class DummyClient:
        def __init__(self, **_: object) -> None:
            pass

        async def __aenter__(self) -> DummyClient:
            return self

        async def __aexit__(self, *_: object) -> None:
            return None

        async def get(self, _: str) -> httpx.Response:
            raise RuntimeError("boom")

    monkeypatch.setattr(api_core.httpx, "AsyncClient", DummyClient)
    result = await api_core._check_proxy_health(proxy, "https://example.com")
    assert result.status == "failed"
    assert result.error == "boom"


@pytest.mark.asyncio
async def test_health_check_proxies_filters_ids() -> None:
    """Health check should filter proxies when IDs are provided."""
    proxy = Proxy(url="http://proxy.example.com:8080")
    rotator = MagicMock()
    rotator.pool.get_all_proxies.return_value = [proxy]

    result_model = HealthCheckResult(
        proxy_id=api_core._get_proxy_id(proxy),
        status="working",
        latency_ms=10,
        error=None,
    )
    with patch("proxywhirl.api.core._check_proxy_health", AsyncMock(return_value=result_model)):
        request_data = HealthCheckRequest(proxy_ids=[api_core._get_proxy_id(proxy)])
        response = await api_core.health_check_proxies(request_data, rotator, None)

    assert response.status == "success"
    assert response.data == [result_model]


@pytest.mark.asyncio
async def test_health_check_proxies_deprecated_calls_new() -> None:
    """Deprecated endpoint should delegate to health_check_proxies."""
    request_data = HealthCheckRequest(proxy_ids=[])
    rotator = MagicMock()

    with patch(
        "proxywhirl.api.core.health_check_proxies",
        AsyncMock(return_value=api_core.APIResponse.success(data=[])),
    ) as handler:
        response = await api_core.health_check_proxies_deprecated(request_data, rotator, None)

    assert response.status == "success"
    handler.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_proxy_found_and_missing() -> None:
    """Get proxy should return data or 404 when missing."""
    proxy = Proxy(url="http://proxy.example.com:8080", health_status=HealthStatus.HEALTHY)
    rotator = MagicMock()
    rotator.pool.get_all_proxies.return_value = [proxy]
    rotator.get_circuit_breaker_states.return_value = {
        api_core._get_proxy_id(proxy): SimpleNamespace(state=SimpleNamespace(value="OPEN"))
    }

    response = await api_core.get_proxy(api_core._get_proxy_id(proxy), rotator, None)
    assert response.status == "success"
    assert response.data.health == "healthy"

    with pytest.raises(HTTPException) as exc_info:
        await api_core.get_proxy("missing", rotator, None)
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_delete_proxy_success_and_missing() -> None:
    """Delete proxy should remove and persist or raise for missing."""
    proxy = Proxy(url="http://proxy.example.com:8080")
    rotator = MagicMock()
    rotator.pool.get_all_proxies.return_value = [proxy]
    rotator.pool.remove_proxy = MagicMock()
    storage = MagicMock()
    storage.save = AsyncMock()

    await api_core.delete_proxy(api_core._get_proxy_id(proxy), rotator, storage, None)
    rotator.pool.remove_proxy.assert_called_once_with(proxy.id)
    storage.save.assert_awaited_once()

    rotator.pool.get_all_proxies.return_value = []
    with pytest.raises(HTTPException) as exc_info:
        await api_core.delete_proxy("missing", rotator, None, None)
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_health_check_status_branches() -> None:
    """Health check should handle unhealthy, degraded, and healthy states."""
    unhealthy_rotator = MagicMock()
    unhealthy_rotator.pool.size = 0
    unhealthy_rotator.pool.healthy_count = 0
    unhealthy_rotator.pool.unhealthy_count = 0
    response = await api_core.health_check(unhealthy_rotator)
    assert response.status_code == 503

    degraded_rotator = MagicMock()
    degraded_rotator.pool.size = 2
    degraded_rotator.pool.healthy_count = 1
    degraded_rotator.pool.unhealthy_count = 2
    response = await api_core.health_check(degraded_rotator)
    assert response.status_code == 200

    healthy_rotator = MagicMock()
    healthy_rotator.pool.size = 2
    healthy_rotator.pool.healthy_count = 2
    healthy_rotator.pool.unhealthy_count = 0
    response = await api_core.health_check(healthy_rotator)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_readiness_check_ready() -> None:
    """Readiness check should report ready when dependencies available."""
    rotator = MagicMock()
    response = await api_core.readiness_check(rotator, None)
    payload = json.loads(response.body.decode())
    assert response.status_code == 200
    assert payload["data"]["ready"] is True


@pytest.mark.asyncio
async def test_get_status_and_stats() -> None:
    """Status and stats endpoints should compute aggregates."""
    proxy = Proxy(url="http://proxy.example.com:8080")
    proxy.requests_started = 5
    proxy.requests_completed = 4
    proxy.total_failures = 1
    proxy.average_response_time_ms = 120

    rotator = MagicMock()
    rotator.pool.size = 1
    rotator.pool.healthy_count = 1
    rotator.pool.get_all_proxies.return_value = [proxy]
    rotator.get_circuit_breaker_states.return_value = {
        api_core._get_proxy_id(proxy): SimpleNamespace(state=SimpleNamespace(value="OPEN"))
    }

    status_response = await api_core.get_status(rotator, None, {"rotation_strategy": "random"})
    assert status_response.status == "success"
    assert status_response.data.pool_stats.failed == 1

    stats_response = await api_core.get_stats(rotator)
    assert stats_response.status == "success"
    assert stats_response.data.requests_total == 5


@pytest.mark.asyncio
async def test_get_and_update_configuration() -> None:
    """Configuration endpoints should read and update settings."""
    config = {
        "rotation_strategy": "round-robin",
        "timeout": 10,
        "max_retries": 2,
        "rate_limits": {"default_limit": 10, "request_endpoint_limit": 5},
        "auth_enabled": False,
        "cors_origins": ["http://example.com"],
    }
    read_response = await api_core.get_configuration(config, None)
    assert read_response.data.timeout == 10

    rotator = MagicMock()
    update_data = UpdateConfigRequest(rotation_strategy="random", timeout=15)
    update_response = await api_core.update_configuration.__wrapped__(
        _make_request(), update_data, config, rotator, None
    )
    assert update_response.data.rotation_strategy == "random"
    rotator.set_strategy.assert_called_once_with("random", atomic=True)

    rotator.set_strategy.reset_mock()
    rotator.set_strategy.side_effect = ValueError("bad strategy")
    update_data = UpdateConfigRequest(rotation_strategy="weighted")
    with pytest.raises(HTTPException) as exc_info:
        await api_core.update_configuration.__wrapped__(
            _make_request(), update_data, config, rotator, None
        )
    assert exc_info.value.status_code == 400


@pytest.mark.asyncio
async def test_retry_policy_endpoints() -> None:
    """Retry policy endpoints should get and update policies."""
    api_core._rotator = None
    with pytest.raises(HTTPException):
        await api_core.get_retry_policy(None)

    retry_policy = RetryPolicy()
    api_core._rotator = MagicMock()
    api_core._rotator.retry_policy = retry_policy
    api_core._rotator.retry_executor = SimpleNamespace(retry_policy=retry_policy)

    response = await api_core.get_retry_policy(None)
    assert response.status == "success"

    update_request = RetryPolicyRequest(max_attempts=5, backoff_strategy="linear")
    update_response = await api_core.update_retry_policy(update_request, None)
    assert update_response.data.max_attempts == 5

    invalid_request = RetryPolicyRequest(retry_status_codes=[200])
    with pytest.raises(HTTPException) as exc_info:
        await api_core.update_retry_policy(invalid_request, None)
    assert exc_info.value.status_code == 400


@pytest.mark.asyncio
async def test_circuit_breaker_endpoints() -> None:
    """Circuit breaker endpoints should return states and metrics."""
    cb = SimpleNamespace(
        state=SimpleNamespace(value="open"),
        failure_count=2,
        failure_threshold=5,
        window_duration=60,
        timeout_duration=30,
        next_test_time=None,
        last_state_change=datetime.now(timezone.utc),
    )
    metrics = DummyRetryMetrics(
        summary={
            "total_retries": 2,
            "success_by_attempt": {0: 1},
            "circuit_breaker_events_count": 1,
            "retention_hours": 24,
        },
        timeseries=[],
        by_proxy={},
        events=[
            SimpleNamespace(
                proxy_id="proxy-1",
                from_state=SimpleNamespace(value="closed"),
                to_state=SimpleNamespace(value="open"),
                timestamp=datetime.now(timezone.utc),
                failure_count=1,
            )
        ],
    )
    api_core._rotator = MagicMock()
    api_core._rotator.get_circuit_breaker_states.return_value = {"proxy-1": cb}
    api_core._rotator.get_retry_metrics.return_value = metrics
    api_core._rotator.reset_circuit_breaker = MagicMock()

    list_response = await api_core.list_circuit_breakers(None)
    assert list_response.status == "success"

    metrics_response = await api_core.get_circuit_breaker_metrics(24, None)
    assert metrics_response.status == "success"

    get_response = await api_core.get_circuit_breaker("proxy-1", None)
    assert get_response.status == "success"

    reset_response = await api_core.reset_circuit_breaker.__wrapped__(
        _make_request(), "proxy-1", None
    )
    assert reset_response.status == "success"

    api_core._rotator.reset_circuit_breaker.side_effect = KeyError("missing")
    with pytest.raises(HTTPException) as exc_info:
        await api_core.reset_circuit_breaker.__wrapped__(_make_request(), "missing", None)
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_retry_metrics_endpoints() -> None:
    """Retry metrics endpoints should return summaries and timeseries data."""
    summary = {
        "total_retries": 2,
        "success_by_attempt": {0: 1, 1: 1},
        "circuit_breaker_events_count": 1,
        "retention_hours": 24,
    }
    timeseries = [
        {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_requests": 3,
            "total_retries": 2,
            "success_rate": 0.5,
            "avg_latency": 0.2,
        }
    ]
    by_proxy = {
        "proxy-1": {
            "proxy_id": "proxy-1",
            "total_attempts": 2,
            "success_count": 1,
            "failure_count": 1,
            "avg_latency": 0.2,
            "circuit_breaker_opens": 1,
        }
    }
    metrics = DummyRetryMetrics(summary=summary, timeseries=timeseries, by_proxy=by_proxy)

    api_core._rotator = MagicMock()
    api_core._rotator.get_retry_metrics.return_value = metrics

    summary_response = await api_core.get_retry_metrics(None)
    assert summary_response.status == "success"

    timeseries_response = await api_core.get_retry_timeseries(24, None)
    assert timeseries_response.status == "success"

    by_proxy_response = await api_core.get_retry_stats_by_proxy(24, None)
    assert by_proxy_response.status == "success"

    json_response = await api_core.get_retry_metrics_endpoint(None, 24, None)
    assert json_response.status_code == 200

    prometheus_response = await api_core.get_retry_metrics_endpoint("prometheus", 24, None)
    assert prometheus_response.status_code == 200


@pytest.mark.asyncio
async def test_circuit_breaker_metrics_endpoint_formats() -> None:
    """Circuit breaker metrics endpoint should support JSON and Prometheus."""
    cb = SimpleNamespace(
        state=SimpleNamespace(value="open"),
        failure_count=2,
        failure_threshold=5,
        window_duration=60,
        timeout_duration=30,
        next_test_time=None,
        last_state_change=datetime.now(timezone.utc),
    )
    metrics = DummyRetryMetrics(
        summary={
            "total_retries": 0,
            "success_by_attempt": {},
            "circuit_breaker_events_count": 1,
            "retention_hours": 24,
        },
        timeseries=[],
        by_proxy={},
        events=[
            SimpleNamespace(
                proxy_id="proxy-1",
                from_state=SimpleNamespace(value="closed"),
                to_state=SimpleNamespace(value="open"),
                timestamp=datetime.now(timezone.utc),
                failure_count=1,
            )
        ],
    )
    api_core._rotator = MagicMock()
    api_core._rotator.get_circuit_breaker_states.return_value = {"proxy-1": cb}
    api_core._rotator.get_retry_metrics.return_value = metrics

    json_response = await api_core.get_circuit_breaker_metrics_endpoint(None, 24, None)
    assert json_response.status_code == 200

    prometheus_response = await api_core.get_circuit_breaker_metrics_endpoint(
        "prometheus", 24, None
    )
    assert prometheus_response.status_code == 200
