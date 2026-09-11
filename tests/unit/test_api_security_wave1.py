"""Wave 1 API security packs (P-A-01 through P-A-10)."""

from __future__ import annotations

import asyncio
import json
import os
from unittest.mock import MagicMock, patch

import httpx
import pytest
from fastapi import FastAPI, HTTPException, Request
from fastapi.testclient import TestClient
from loguru import logger
from pydantic import ValidationError

import proxywhirl.api.routes.proxies as proxy_routes
from proxywhirl.api import app
from proxywhirl.api.core import (
    AuditLoggingMiddleware,
    RequestLoggingMiddleware,
    http_exception_handler,
    internal_error_handler,
    proxy_error_handler,
)
from proxywhirl.api.middleware.auth import APIKeyMiddleware
from proxywhirl.api.models import ProxiedRequest
from proxywhirl.api.runtime import (
    request_requires_api_key,
    secure_compare_digest,
)
from proxywhirl.exceptions import ProxyConnectionError
from proxywhirl.models import HealthStatus, Proxy
from proxywhirl.rotator import ProxyWhirl
from proxywhirl.settings import ProxyConfiguration


@pytest.fixture
def mock_rotator():
    rotator = MagicMock()
    metrics = MagicMock()
    metrics.get_timeseries.return_value = []
    rotator.get_retry_metrics.return_value = metrics
    return rotator


@pytest.mark.parametrize(
    ("method", "path", "expected"),
    [
        ("POST", "/api/request", True),
        ("GET", "/api/rotate", True),
        ("POST", "/api/proxies/health-check", True),
        ("POST", "/api/proxies/test", True),
        ("GET", "/api/proxies", True),
        ("GET", "/api/proxies/stream", True),
        ("GET", "/api/proxies/export", True),
        ("GET", "/api/proxies/abc123", True),
        ("GET", "/api/status", True),
        ("GET", "/api/stats", True),
        ("GET", "/api/config", True),
        ("GET", "/api/circuit-breakers", True),
        ("GET", "/api/circuit-breakers/proxy-1", True),
        ("GET", "/api/metrics", True),
        ("GET", "/api/metrics/retries", True),
        ("GET", "/api/metrics/retries/timeseries", True),
        ("GET", "/api/metrics/retries/by-proxy", True),
        ("GET", "/api/metrics/circuit-breakers", True),
        ("GET", "/api/retry/policy", True),
        ("PUT", "/api/retry/policy", True),
        ("GET", "/api/health", False),
        ("GET", "/api/ready", False),
    ],
)
def test_force_auth_matrix_when_global_auth_disabled(
    method: str, path: str, expected: bool
) -> None:
    assert request_requires_api_key(method, path, require_auth=False) is expected


def test_force_auth_list_proxies_requires_key() -> None:
    mini = FastAPI()
    mini.add_middleware(APIKeyMiddleware)

    @mini.get("/api/proxies")
    def list_proxies() -> dict[str, str]:
        return {"status": "ok"}

    client = TestClient(mini)
    with patch.dict(os.environ, {}, clear=True):
        assert client.get("/api/proxies").status_code == 503

    with patch.dict(os.environ, {"PROXYWHIRL_API_KEY": "secret-key-123"}, clear=True):
        assert client.get("/api/proxies").status_code == 401
        ok = client.get("/api/proxies", headers={"X-API-Key": "secret-key-123"})
        assert ok.status_code == 200


def test_force_auth_retry_policy_read_requires_key() -> None:
    mini = FastAPI()
    mini.add_middleware(APIKeyMiddleware)

    @mini.get("/api/retry/policy")
    def get_retry_policy() -> dict[str, str]:
        return {"status": "ok"}

    client = TestClient(mini)
    with patch.dict(os.environ, {"PROXYWHIRL_API_KEY": "secret-key-123"}, clear=True):
        assert client.get("/api/retry/policy").status_code == 401
        response = client.get(
            "/api/retry/policy",
            headers={"X-API-Key": "secret-key-123"},
        )
        assert response.status_code == 200


def test_secure_compare_digest_rejects_length_mismatch() -> None:
    assert secure_compare_digest("short", "much-longer-expected-key") is False
    assert secure_compare_digest(None, "expected-key") is False
    assert secure_compare_digest("expected-key", "expected-key") is True


def test_refuse_non_loopback_bind_without_insecure_override() -> None:
    from proxywhirl.api.core import lifespan

    with (
        patch.dict(
            os.environ,
            {
                "PROXYWHIRL_BIND_HOST": "0.0.0.0",
                "PROXYWHIRL_REQUIRE_AUTH": "false",
            },
            clear=True,
        ),
        pytest.raises(RuntimeError, match="Refusing to start API"),
    ):
        import asyncio

        async def _run() -> None:
            async with lifespan(app):
                pass

        asyncio.run(_run())


@pytest.mark.parametrize("api_key", [None, "", "changeme", "your-api-key-here"])
def test_refuse_non_loopback_bind_without_usable_api_key(api_key: str | None) -> None:
    """Auth mode alone cannot expose the API without usable secret material."""
    from proxywhirl.api.core import lifespan

    environment = {
        "PROXYWHIRL_BIND_HOST": "0.0.0.0",
        "PROXYWHIRL_REQUIRE_AUTH": "true",
    }
    if api_key is not None:
        environment["PROXYWHIRL_API_KEY"] = api_key

    with (
        patch.dict(os.environ, environment, clear=True),
        pytest.raises(RuntimeError, match="usable PROXYWHIRL_API_KEY"),
    ):
        import asyncio

        async def _run() -> None:
            async with lifespan(app):
                pass

        asyncio.run(_run())


def test_allow_non_loopback_bind_when_auth_required() -> None:
    """Container posture: 0.0.0.0 + REQUIRE_AUTH=true is permitted."""
    from proxywhirl.api.core import lifespan

    with (
        patch.dict(
            os.environ,
            {
                "PROXYWHIRL_BIND_HOST": "0.0.0.0",
                "PROXYWHIRL_REQUIRE_AUTH": "true",
                "PROXYWHIRL_API_KEY": "container-api-key",
            },
            clear=True,
        ),
        patch("proxywhirl.api.core.ProxyWhirl"),
        patch("proxywhirl.api.core.set_rotator"),
        patch("proxywhirl.api.core.set_storage"),
        patch("proxywhirl.api.core.set_config"),
        patch("proxywhirl.api.core.get_storage", return_value=None),
        patch("proxywhirl.api.core.get_current_rotator", return_value=None),
    ):
        import asyncio

        async def _run() -> None:
            async with lifespan(app):
                pass

        asyncio.run(_run())


def test_allow_non_loopback_bind_with_explicit_local_override() -> None:
    """The documented local-only override bypasses the non-loopback startup guard."""
    from proxywhirl.api.core import lifespan

    with (
        patch.dict(
            os.environ,
            {
                "PROXYWHIRL_ALLOW_INSECURE_BIND": "1",
                "PROXYWHIRL_BIND_HOST": "0.0.0.0",
                "PROXYWHIRL_REQUIRE_AUTH": "false",
            },
            clear=True,
        ),
        patch("proxywhirl.api.core.ProxyWhirl"),
        patch("proxywhirl.api.core.set_rotator"),
        patch("proxywhirl.api.core.set_storage"),
        patch("proxywhirl.api.core.set_config"),
        patch("proxywhirl.api.core.get_storage", return_value=None),
        patch("proxywhirl.api.core.get_current_rotator", return_value=None),
    ):
        import asyncio

        async def _run() -> None:
            async with lifespan(app):
                pass

        asyncio.run(_run())


def test_docs_disabled_by_default_when_require_auth() -> None:
    from proxywhirl.settings import APISettings

    with patch.dict(
        os.environ,
        {"PROXYWHIRL_REQUIRE_AUTH": "true", "PROXYWHIRL_API_KEY": "k"},
        clear=True,
    ):
        assert APISettings().docs_enabled is False


def test_docs_enabled_when_expose_docs_set() -> None:
    from proxywhirl.settings import APISettings

    with patch.dict(
        os.environ,
        {
            "PROXYWHIRL_REQUIRE_AUTH": "true",
            "PROXYWHIRL_API_KEY": "k",
            "PROXYWHIRL_EXPOSE_DOCS": "true",
        },
        clear=True,
    ):
        assert APISettings().docs_enabled is True


def test_docs_default_on_when_auth_disabled() -> None:
    from proxywhirl.settings import APISettings

    with patch.dict(os.environ, {"PROXYWHIRL_REQUIRE_AUTH": "false"}, clear=True):
        assert APISettings().docs_enabled is True


def test_force_auth_status_and_stats_require_key() -> None:
    mini = FastAPI()
    mini.add_middleware(APIKeyMiddleware)

    @mini.get("/api/status")
    def status() -> dict[str, str]:
        return {"status": "ok"}

    @mini.get("/api/stats")
    def stats() -> dict[str, str]:
        return {"status": "ok"}

    @mini.get("/api/config")
    def config() -> dict[str, str]:
        return {"status": "ok"}

    client = TestClient(mini)
    with patch.dict(os.environ, {"PROXYWHIRL_API_KEY": "secret-key-123"}, clear=True):
        assert client.get("/api/status").status_code == 401
        assert client.get("/api/stats").status_code == 401
        assert client.get("/api/config").status_code == 401
        assert client.get("/api/status", headers={"X-API-Key": "secret-key-123"}).status_code == 200


def test_audit_body_redacts_url_and_credentials() -> None:
    middleware = AuditLoggingMiddleware(None)
    redacted = middleware._redact_body(
        {
            "url": "http://user:pass@proxy.example.com:8080/path",
            "authorization": "Bearer secret-token-value",
            "nested": {
                "api_key": "nested-secret",
                "client_secret": "compound-secret",
            },
        }
    )
    assert "user:pass" not in str(redacted)
    assert "secret-token-value" not in str(redacted)
    assert redacted["nested"]["api_key"] == "***REDACTED***"
    assert redacted["nested"]["client_secret"] == "***REDACTED***"


def test_proxied_request_body_limit_counts_utf8_bytes() -> None:
    body = "\u20ac" * 349_526  # 1,048,578 UTF-8 bytes, but fewer than 1,048,576 chars.

    with pytest.raises(ValidationError, match="1,048,576 bytes"):
        ProxiedRequest(url="https://example.com", method="POST", body=body)


def test_request_body_limit_stops_stream_before_downstream_completion() -> None:
    from proxywhirl.api.middleware.body_limit import RequestBodyLimitMiddleware

    received_chunks = 0
    receive_calls = 0
    downstream_completed = False
    sent: list[dict[str, object]] = []

    async def downstream(scope, receive, send) -> None:
        nonlocal downstream_completed, received_chunks
        while True:
            message = await receive()
            received_chunks += 1
            if message["type"] == "http.request" and not message.get("more_body", False):
                break
        downstream_completed = True

    async def exercise() -> None:
        chunks: list[dict[str, object]] = [
            {"type": "http.request", "body": b"abc", "more_body": True},
            {"type": "http.request", "body": b"def", "more_body": True},
            {"type": "http.request", "body": b"never-read", "more_body": False},
        ]

        async def receive() -> dict[str, object]:
            nonlocal receive_calls
            receive_calls += 1
            return chunks.pop(0)

        async def send(message: dict[str, object]) -> None:
            sent.append(message)

        scope = {
            "type": "http",
            "asgi": {"version": "3.0"},
            "http_version": "1.1",
            "method": "POST",
            "scheme": "http",
            "path": "/api/request",
            "raw_path": b"/api/request",
            "query_string": b"",
            "root_path": "",
            "headers": [],
            "client": ("127.0.0.1", 1234),
            "server": ("testserver", 80),
        }
        middleware = RequestBodyLimitMiddleware(downstream, max_body_bytes=5)
        await middleware(scope, receive, send)

    asyncio.run(exercise())

    response_start = next(message for message in sent if message["type"] == "http.response.start")
    assert response_start["status"] == 413
    assert receive_calls == 2
    assert received_chunks == 1
    assert downstream_completed is False


def test_request_body_limit_is_outermost_app_middleware() -> None:
    from proxywhirl.api.middleware.body_limit import RequestBodyLimitMiddleware

    assert app.user_middleware[0].cls is RequestBodyLimitMiddleware


def test_streamed_body_limit_survives_full_middleware_stack(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("PROXYWHIRL_API_KEY", "test-key")
    sent: list[dict[str, object]] = []
    receive_calls = 0

    async def exercise() -> None:
        chunks: list[dict[str, object]] = [
            {"type": "http.request", "body": b"x" * 600_000, "more_body": True},
            {"type": "http.request", "body": b"y" * 600_000, "more_body": True},
            {"type": "http.request", "body": b"never-read", "more_body": False},
        ]

        async def receive() -> dict[str, object]:
            nonlocal receive_calls
            receive_calls += 1
            return chunks.pop(0)

        async def send(message: dict[str, object]) -> None:
            sent.append(message)

        scope = {
            "type": "http",
            "asgi": {"version": "3.0"},
            "http_version": "1.1",
            "method": "POST",
            "scheme": "http",
            "path": "/api/request",
            "raw_path": b"/api/request",
            "query_string": b"",
            "root_path": "",
            "headers": [
                (b"x-api-key", b"test-key"),
                (b"content-type", b"application/json"),
            ],
            "client": ("127.0.0.1", 1234),
            "server": ("testserver", 80),
        }
        await app(scope, receive, send)

    asyncio.run(exercise())

    response_starts = [message for message in sent if message["type"] == "http.response.start"]
    assert [message["status"] for message in response_starts] == [413]
    assert receive_calls == 2


def test_request_logging_redacts_secret_like_query_names() -> None:
    middleware = RequestLoggingMiddleware(None)
    query = "access_token=token-value&client_secret=secret-value&api-key=key-value&normal=visible"

    redacted = middleware._redact_query_string(query)

    assert "token-value" not in redacted
    assert "secret-value" not in redacted
    assert "key-value" not in redacted
    assert "normal=visible" in redacted


def test_auth_audit_logging_does_not_reveal_key_fragments() -> None:
    middleware = AuditLoggingMiddleware(None)

    redacted = middleware._redact_api_key("prefix-sensitive-value-suffix")

    assert redacted == "***REDACTED***"
    assert "prefix" not in redacted
    assert "suffix" not in redacted


def test_request_failure_log_omits_raw_exception_and_query_secrets() -> None:
    middleware = RequestLoggingMiddleware(None)
    messages: list[str] = []
    sink_id = logger.add(messages.append, format="{message} {extra}")
    request = Request(
        {
            "type": "http",
            "http_version": "1.1",
            "method": "GET",
            "scheme": "http",
            "path": "/boom",
            "raw_path": b"/boom",
            "query_string": b"access_token=query-secret-value",
            "headers": [],
            "client": ("127.0.0.1", 1234),
            "server": ("testserver", 80),
        }
    )

    async def fail(_request: Request):
        raise RuntimeError("raw-exception-secret-value")

    try:
        with pytest.raises(RuntimeError):
            asyncio.run(middleware.dispatch(request, fail))
    finally:
        logger.remove(sink_id)

    log_output = "\n".join(messages)
    assert "query-secret-value" not in log_output
    assert "raw-exception-secret-value" not in log_output


def test_error_handlers_omit_raw_exception_details() -> None:
    request = Request(
        {
            "type": "http",
            "http_version": "1.1",
            "method": "GET",
            "scheme": "http",
            "path": "/api/request",
            "raw_path": b"/api/request",
            "query_string": b"",
            "headers": [],
            "client": ("127.0.0.1", 1234),
            "server": ("testserver", 80),
        }
    )
    raw_detail = "raw-exception-secret-value"
    messages: list[str] = []
    sink_id = logger.add(messages.append, format="{message} {extra}")

    try:
        internal = asyncio.run(internal_error_handler(request, RuntimeError(raw_detail)))
        http_error = asyncio.run(
            http_exception_handler(request, HTTPException(status_code=500, detail=raw_detail))
        )
        proxy_error = asyncio.run(proxy_error_handler(request, ProxyConnectionError(raw_detail)))
    finally:
        logger.remove(sink_id)

    for response in (internal, http_error, proxy_error):
        payload = json.loads(response.body)
        assert raw_detail not in json.dumps(payload)
    assert raw_detail not in "\n".join(messages)


def test_sync_rotator_bounds_response_while_streaming(monkeypatch: pytest.MonkeyPatch) -> None:
    class CountingStream(httpx.SyncByteStream):
        def __init__(self) -> None:
            self.chunks_yielded = 0
            self.closed = False

        def __iter__(self):
            for chunk in (b"abc", b"def", b"never-read"):
                self.chunks_yielded += 1
                yield chunk

        def close(self) -> None:
            self.closed = True

    stream = CountingStream()
    upstream_request = httpx.Request("GET", "https://example.com")
    upstream_response = httpx.Response(200, request=upstream_request, stream=stream)
    fake_client = MagicMock()
    fake_client.build_request.return_value = upstream_request
    fake_client.send.return_value = upstream_response
    fake_client.request.side_effect = AssertionError("buffering request path must not be used")

    rotator = ProxyWhirl(
        proxies=[
            Proxy(
                url="http://proxy.example.com:8080",
                health_status=HealthStatus.HEALTHY,
            )
        ],
        bootstrap=False,
    )
    monkeypatch.setattr(rotator, "_get_or_create_client", lambda *_args: fake_client)

    response = rotator._make_request(
        "GET",
        "https://example.com",
        _response_body_limit_bytes=5,
    )

    assert response.content == b"abcde"
    assert response.extensions["proxywhirl_response_truncated"] is True
    assert stream.chunks_yielded == 2
    assert stream.closed is True
    fake_client.send.assert_called_once_with(upstream_request, stream=True)
    fake_client.request.assert_not_called()


def test_sync_rotator_queue_preserves_response_limit(monkeypatch: pytest.MonkeyPatch) -> None:
    class BoundedStream(httpx.SyncByteStream):
        def __iter__(self):
            yield b"abcdef"

    upstream_request = httpx.Request("GET", "https://example.com")
    upstream_response = httpx.Response(
        200,
        request=upstream_request,
        stream=BoundedStream(),
    )
    fake_client = MagicMock()
    fake_client.build_request.return_value = upstream_request
    fake_client.send.return_value = upstream_response
    rate_limiter = MagicMock()
    rate_limiter.check_limit.return_value = False
    rotator = ProxyWhirl(
        proxies=[
            Proxy(
                url="http://proxy.example.com:8080",
                health_status=HealthStatus.HEALTHY,
            )
        ],
        config=ProxyConfiguration(queue_enabled=True, queue_size=2),
        rate_limiter=rate_limiter,
        bootstrap=False,
    )
    monkeypatch.setattr(rotator, "_get_or_create_client", lambda *_args: fake_client)

    response = rotator._make_request(
        "GET",
        "https://example.com",
        _response_body_limit_bytes=5,
    )

    assert response.content == b"abcde"
    assert response.extensions["proxywhirl_response_truncated"] is True
    fake_client.send.assert_called_once_with(upstream_request, stream=True)
    fake_client.request.assert_not_called()


@pytest.mark.asyncio
async def test_proxy_health_check_streams_without_buffering(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class StreamContext:
        async def __aenter__(self):
            return httpx.Response(200)

        async def __aexit__(self, *_args: object) -> None:
            return None

    class FakeAsyncClient:
        def __init__(self, **_kwargs: object) -> None:
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *_args: object) -> None:
            return None

        def stream(self, method: str, url: str) -> StreamContext:
            assert method == "GET"
            assert url == "https://example.com"
            return StreamContext()

        async def get(self, _url: str) -> httpx.Response:
            raise AssertionError("buffering health-check path must not be used")

    monkeypatch.setattr(proxy_routes.httpx, "AsyncClient", FakeAsyncClient)
    proxy = Proxy(url="http://proxy.example.com:8080")

    result = await proxy_routes._check_proxy_health(proxy, "https://example.com")

    assert result.status == "working"
    assert result.error is None


@pytest.mark.asyncio
async def test_proxy_health_check_error_is_generic(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeAsyncClient:
        def __init__(self, **_kwargs: object) -> None:
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *_args: object) -> None:
            return None

        def stream(self, _method: str, _url: str):
            raise RuntimeError("raw-validation-secret-value")

    monkeypatch.setattr(proxy_routes.httpx, "AsyncClient", FakeAsyncClient)
    proxy = Proxy(url="http://proxy.example.com:8080")

    result = await proxy_routes._check_proxy_health(proxy, "https://example.com")

    assert result.status == "failed"
    assert result.error == "Proxy validation failed"


def test_proxied_request_truncates_large_body(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    class FakeResponse:
        status_code = 200
        headers = {}
        text = "x" * 5000

    class FakeRotator:
        last_used_proxy = Proxy(url="http://proxy.example.com:8080")

        def _make_request(self, *_args, **kwargs):
            captured.update(kwargs)
            return FakeResponse()

    rotator = FakeRotator()
    app.dependency_overrides[proxy_routes.get_rotator] = lambda: rotator
    monkeypatch.setenv("PROXYWHIRL_MAX_PROXIED_RESPONSE_BYTES", "2048")
    monkeypatch.setenv("PROXYWHIRL_API_KEY", "test-key")
    monkeypatch.setattr(proxy_routes, "revalidate_proxied_target_url", lambda _url: None)
    monkeypatch.setattr(
        proxy_routes,
        "validate_proxied_request_url",
        lambda data: data,
    )
    try:
        client = TestClient(app)
        response = client.post(
            "/api/request",
            headers={"X-API-Key": "test-key"},
            json={
                "url": "https://example.com",
                "method": "GET",
                "headers": {},
                "timeout": 5,
            },
        )
    finally:
        app.dependency_overrides.pop(proxy_routes.get_rotator, None)

    assert response.status_code == 200
    body = response.json()["data"]["body"]
    assert len(body.encode("utf-8")) <= 2048 + 64
    assert "truncated" in body
    assert captured["_response_body_limit_bytes"] == 2048


def test_proxied_request_strips_hop_by_hop_headers(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    class FakeResponse:
        status_code = 200
        headers = {}
        text = "ok"

    class FakeRotator:
        last_used_proxy = Proxy(url="http://proxy.example.com:8080")

        def _make_request(self, _method, _url, **kwargs):
            captured["headers"] = kwargs.get("headers")
            return FakeResponse()

    rotator = FakeRotator()
    app.dependency_overrides[proxy_routes.get_rotator] = lambda: rotator
    monkeypatch.setenv("PROXYWHIRL_API_KEY", "test-key")
    monkeypatch.setattr(proxy_routes, "revalidate_proxied_target_url", lambda _url: None)
    monkeypatch.setattr(
        proxy_routes,
        "validate_proxied_request_url",
        lambda data: data,
    )
    try:
        client = TestClient(app)
        response = client.post(
            "/api/request",
            headers={"X-API-Key": "test-key"},
            json={
                "url": "https://example.com",
                "method": "GET",
                "headers": {
                    "Connection": "close",
                    "X-Custom": "keep-me",
                    "Transfer-Encoding": "chunked",
                },
                "timeout": 5,
            },
        )
    finally:
        app.dependency_overrides.pop(proxy_routes.get_rotator, None)

    assert response.status_code == 200
    raw_headers = captured.get("headers")
    headers: dict[str, object] = raw_headers if isinstance(raw_headers, dict) else {}
    assert "X-Custom" in headers
    assert "Connection" not in headers
    assert "Transfer-Encoding" not in headers


def test_health_check_max_proxies_enforced() -> None:
    rotator = MagicMock()
    rotator.pool = MagicMock()
    rotator.pool.get_all_proxies.return_value = [
        Proxy(url=f"http://proxy{i}.example.com:8080") for i in range(5)
    ]
    app.dependency_overrides[proxy_routes.get_rotator] = lambda: rotator
    try:
        with patch.dict(
            os.environ,
            {"PROXYWHIRL_HEALTH_CHECK_MAX_PROXIES": "2", "PROXYWHIRL_API_KEY": "k"},
            clear=True,
        ):
            client = TestClient(app)
            response = client.post(
                "/api/proxies/health-check",
                headers={"X-API-Key": "k"},
                json={},
            )
    finally:
        app.dependency_overrides.pop(proxy_routes.get_rotator, None)

    assert response.status_code == 400
    assert "max 2" in response.json()["error"]["message"]


def test_readiness_omits_storage_connected_without_storage_path() -> None:
    rotator = ProxyWhirl(proxies=[Proxy(url="http://p.example.com:8080")], bootstrap=False)
    app.dependency_overrides[proxy_routes.get_rotator] = lambda: rotator
    try:
        with patch.dict(os.environ, {}, clear=True):
            response = TestClient(app).get("/api/ready")
    finally:
        app.dependency_overrides.pop(proxy_routes.get_rotator, None)

    assert response.status_code == 200
    checks = response.json()["data"]["checks"]
    assert "storage_connected" not in checks


def test_metrics_hours_out_of_range_is_safely_bounded(mock_rotator) -> None:
    mock_rotator.get_retry_metrics.return_value.retention_hours = 24
    with (
        patch("proxywhirl.api.runtime._rotator", mock_rotator),
        patch.dict(os.environ, {"PROXYWHIRL_API_KEY": "k"}, clear=True),
    ):
        client = TestClient(app)
        response = client.get(
            "/api/metrics/retries/timeseries?hours=10000",
            headers={"X-API-Key": "k"},
        )
        assert response.status_code == 200


def test_dns_rebinding_revalidated_before_request(monkeypatch: pytest.MonkeyPatch) -> None:
    call_count = 0

    def _validate(url: str, *, allow_private: bool = False) -> None:
        nonlocal call_count
        call_count += 1
        if call_count >= 2:
            raise ValueError("rebinding blocked")

    monkeypatch.setattr("proxywhirl.api.runtime.validate_target_url_safe", _validate)

    class FakeResponse:
        status_code = 200
        headers = {}
        text = "ok"

    rotator = MagicMock()
    rotator.last_used_proxy = Proxy(url="http://proxy.example.com:8080")
    rotator._make_request.return_value = FakeResponse()
    app.dependency_overrides[proxy_routes.get_rotator] = lambda: rotator
    monkeypatch.setenv("PROXYWHIRL_API_KEY", "test-key")
    try:
        client = TestClient(app)
        response = client.post(
            "/api/request",
            headers={"X-API-Key": "test-key"},
            json={
                "url": "https://example.com",
                "method": "GET",
                "headers": {},
                "timeout": 5,
            },
        )
    finally:
        app.dependency_overrides.pop(proxy_routes.get_rotator, None)

    assert response.status_code == 400
    assert call_count >= 2
