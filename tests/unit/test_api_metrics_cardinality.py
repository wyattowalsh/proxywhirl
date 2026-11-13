"""Prometheus cardinality guards for REST API request and proxy-id labels."""

from __future__ import annotations

import uuid
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from proxywhirl.api import app
from proxywhirl.api.runtime import (
    OTHER_METHOD_LABEL,
    UNMATCHED_ENDPOINT_LABEL,
    _tracked_proxy_ids,
    clear_proxy_metrics,
    metric_endpoint_label,
    metric_method_label,
    proxywhirl_circuit_breaker_state,
    proxywhirl_requests_total,
)
from proxywhirl.models import Proxy

_UNIT_API_KEY = "unit-test-api-key"
_AUTH_HEADERS = {"X-API-Key": _UNIT_API_KEY}


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch):
    """Create a test client with a configured API key for force-auth routes."""
    monkeypatch.setenv("PROXYWHIRL_API_KEY", _UNIT_API_KEY)
    test_client = TestClient(app)
    test_client.headers.update(_AUTH_HEADERS)
    return test_client


def _request_endpoint_labels() -> set[str]:
    """Unique endpoint labels on the process-global request counter."""
    endpoints: set[str] = set()
    for label_values in proxywhirl_requests_total._metrics:
        endpoints.add(label_values[0])
    for metric in proxywhirl_requests_total.collect():
        for sample in metric.samples:
            endpoint = sample.labels.get("endpoint")
            if endpoint is not None:
                endpoints.add(endpoint)
    return endpoints


def _circuit_breaker_proxy_ids() -> set[str]:
    """proxy_id labels currently present on the API runtime circuit-breaker gauge."""
    proxy_ids: set[str] = set()
    for metric in proxywhirl_circuit_breaker_state.collect():
        for sample in metric.samples:
            proxy_id = sample.labels.get("proxy_id")
            if proxy_id is not None:
                proxy_ids.add(proxy_id)
    return proxy_ids


def test_metric_endpoint_label_uses_route_template() -> None:
    request = MagicMock()
    request.scope = {"route": SimpleNamespace(path="/api/proxies/{proxy_id}")}
    request.url.path = "/api/proxies/abc123"
    assert metric_endpoint_label(request) == "/api/proxies/{proxy_id}"


def test_metric_endpoint_label_unmatched_api_path() -> None:
    request = MagicMock()
    request.scope = {}
    request.url.path = f"/api/{uuid.uuid4()}"
    assert metric_endpoint_label(request) == UNMATCHED_ENDPOINT_LABEL


def test_metric_endpoint_label_empty_template_is_unmatched() -> None:
    request = MagicMock()
    request.scope = {"route": SimpleNamespace(path="")}
    request.url.path = "/not-a-registered-route"
    assert metric_endpoint_label(request) == UNMATCHED_ENDPOINT_LABEL


def test_unmatched_api_paths_collapse_to_single_endpoint_label(client: TestClient) -> None:
    """Authenticated 404s on unique /api/* paths must not mint unique endpoint labels."""
    raw_paths = [f"/api/{uuid.uuid4()}" for _ in range(5)]
    for path in raw_paths:
        response = client.get(path)
        assert response.status_code == 404, path

    endpoints = _request_endpoint_labels()
    assert UNMATCHED_ENDPOINT_LABEL in endpoints
    for path in raw_paths:
        assert path not in endpoints


def test_clear_proxy_metrics_removes_circuit_breaker_series() -> None:
    proxy_id = f"cardinality-proxy-{uuid.uuid4()}"
    proxywhirl_circuit_breaker_state.labels(proxy_id=proxy_id).set(1)
    _tracked_proxy_ids.add(proxy_id)
    assert proxy_id in _circuit_breaker_proxy_ids()

    clear_proxy_metrics(proxy_id)

    assert proxy_id not in _circuit_breaker_proxy_ids()
    assert proxy_id not in _tracked_proxy_ids


def test_metric_method_label_collapses_unknown_methods() -> None:
    assert metric_method_label("get") == "GET"
    assert metric_method_label("POST") == "POST"
    assert metric_method_label("NOPE") == OTHER_METHOD_LABEL
    assert metric_method_label("GET2") == OTHER_METHOD_LABEL


def test_delete_proxy_clears_circuit_breaker_series(client: TestClient) -> None:
    proxy = Proxy(url="http://cardinality-delete.example.com:8080")
    proxy_id = str(proxy.id)
    proxywhirl_circuit_breaker_state.labels(proxy_id=proxy_id).set(2)
    _tracked_proxy_ids.add(proxy_id)
    assert proxy_id in _circuit_breaker_proxy_ids()

    rotator = MagicMock()
    rotator.pool.get_all_proxies.return_value = [proxy]
    rotator.pool.aget_all_proxies = None
    rotator.get_circuit_breaker_states.return_value = {}
    rotator.remove_proxy = MagicMock()

    with (
        patch("proxywhirl.api.runtime._rotator", rotator),
        patch("proxywhirl.api.runtime._storage", None),
    ):
        response = client.delete(f"/api/proxies/{proxy_id}")

    assert response.status_code == 204
    rotator.remove_proxy.assert_called_once_with(proxy_id)
    assert proxy_id not in _circuit_breaker_proxy_ids()
    assert proxy_id not in _tracked_proxy_ids
