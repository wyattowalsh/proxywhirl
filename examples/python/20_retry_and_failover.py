"""
Retry and failover scenarios for ProxyWhirl.

All snippets are network-free and use short delays so they finish quickly.
Run with:

    uv run python examples/python/20_retry_and_failover.py
"""

from __future__ import annotations

from typing import Iterable, List
from unittest.mock import patch

import httpx

from proxywhirl import Proxy, ProxyRotator
from proxywhirl.circuit_breaker import CircuitBreakerState
from proxywhirl.models import HealthStatus
from proxywhirl.retry import BackoffStrategy, RetryExecutor, RetryPolicy


def _request_sequence(events: Iterable[int | Exception], url: str) -> callable:
    """
    Build a deterministic request function for RetryExecutor.

    Each element in `events` is either:
    - int: treated as an HTTP status code to return
    - Exception: raised to simulate transport failure
    """
    events_list: List[int | Exception] = list(events)
    request = httpx.Request("GET", url)

    def request_fn() -> httpx.Response:
        if not events_list:
            raise RuntimeError("No more events in request sequence")
        event = events_list.pop(0)
        if isinstance(event, Exception):
            raise event
        return httpx.Response(event, request=request)

    return request_fn


def show_default_policy() -> None:
    print("\n" + "=" * 70)
    print("Default retry policy")
    print("=" * 70)

    rotator = ProxyRotator(proxies=[Proxy(url="http://proxy-default.local:8080")])
    policy = rotator.retry_policy

    print(f"Max attempts: {policy.max_attempts}")
    print(f"Backoff: {policy.backoff_strategy.value} (base_delay={policy.base_delay}s)")
    delays = [policy.calculate_delay(i) for i in range(3)]
    print(f"First three delays: {delays}")
    print(f"Retry status codes: {policy.retry_status_codes}")


def custom_policy_example() -> None:
    print("\n" + "=" * 70)
    print("Custom policy (linear backoff + jitter)")
    print("=" * 70)

    policy = RetryPolicy(
        max_attempts=4,
        backoff_strategy=BackoffStrategy.LINEAR,
        base_delay=0.2,
        max_backoff_delay=1.0,
        jitter=True,
        retry_status_codes=[502, 503, 504],
    )

    print(policy.model_dump())
    print("Use this when upstreams rate-limit or spike during peak load.")


def simulate_retry_with_metrics() -> None:
    print("\n" + "=" * 70)
    print("Simulated retry flow with metrics")
    print("=" * 70)

    proxy = Proxy(url="http://resilient.proxy.local:8080", health_status=HealthStatus.HEALTHY)
    rotator = ProxyRotator(
        proxies=[proxy],
        retry_policy=RetryPolicy(
            max_attempts=3,
            backoff_strategy=BackoffStrategy.FIXED,
            base_delay=0.05,
            max_backoff_delay=0.05,
        ),
    )

    # Fail once with a connect error, once with 503, then succeed
    events = [
        httpx.ConnectError("dial tcp failed", request=httpx.Request("GET", "https://api.example.com")),
        503,
        200,
    ]
    request_fn = _request_sequence(events, "https://api.example.com/data")

    # Skip actual sleeping to keep the example fast
    with patch("proxywhirl.retry.executor.time.sleep", lambda *_: None):
        response = rotator.retry_executor.execute_with_retry(
            request_fn,
            proxy,
            method="GET",
            url="https://api.example.com/data",
        )

    print(f"Final status: {response.status_code}")
    summary = rotator.get_retry_metrics().get_summary()
    print("Retry summary:", summary)


def per_request_override() -> None:
    print("\n" + "=" * 70)
    print("Per-request policy override")
    print("=" * 70)

    base_rotator = ProxyRotator(
        proxies=[Proxy(url="http://override.proxy.local:8080")],
        retry_policy=RetryPolicy(max_attempts=5, base_delay=0.5),
    )

    light_policy = RetryPolicy(
        max_attempts=2,
        backoff_strategy=BackoffStrategy.LINEAR,
        base_delay=0.05,
        max_backoff_delay=0.1,
    )
    executor = RetryExecutor(light_policy, base_rotator.circuit_breakers, base_rotator.retry_metrics)
    proxy = base_rotator.pool.proxies[0]
    request_fn = _request_sequence([httpx.TimeoutException("socket hangup"), 200], "https://example.org/foo")

    with patch("proxywhirl.retry.executor.time.sleep", lambda *_: None):
        response = executor.execute_with_retry(request_fn, proxy, method="GET", url="https://example.org/foo")

    print(f"Overridden policy finished with status {response.status_code} after at most 2 attempts.")


def circuit_breaker_walkthrough() -> None:
    print("\n" + "=" * 70)
    print("Circuit breaker state transitions")
    print("=" * 70)

    rotator = ProxyRotator(proxies=[Proxy(url="http://cb.proxy.local:8080")])
    proxy = rotator.pool.proxies[0]
    circuit_breaker = rotator.circuit_breakers[str(proxy.id)]

    for idx in range(circuit_breaker.failure_threshold):
        circuit_breaker.record_failure()
        print(f"Failure {idx + 1}/{circuit_breaker.failure_threshold} -> state={circuit_breaker.state.value}")

    print("Opening the circuit prevents new traffic until timeout elapses.")
    rotator.reset_circuit_breaker(str(proxy.id))
    print(f"Reset called -> state={circuit_breaker.state.value}")


def main() -> None:
    show_default_policy()
    custom_policy_example()
    simulate_retry_with_metrics()
    per_request_override()
    circuit_breaker_walkthrough()
    print("\nAll retry examples complete.")


if __name__ == "__main__":
    main()
