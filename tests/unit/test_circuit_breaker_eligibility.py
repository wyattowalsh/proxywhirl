"""Tests for is_eligible vs try_acquire_probe circuit breaker API (Wave 1)."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from proxywhirl.circuit_breaker import (
    AsyncCircuitBreaker,
    CircuitBreaker,
    CircuitBreakerBase,
    CircuitBreakerState,
)


class TestIsEligiblePure:
    """is_eligible must not mutate state (P-B-01)."""

    def test_closed_is_eligible(self) -> None:
        cb = CircuitBreaker(proxy_id="p1")
        assert cb.is_eligible() is True
        assert cb.state == CircuitBreakerState.CLOSED

    def test_open_before_timeout_not_eligible(self) -> None:
        cb = CircuitBreaker(proxy_id="p1", failure_threshold=1, timeout_duration=30.0)
        with patch("time.time", return_value=100.0):
            cb.record_failure()
        assert cb.state == CircuitBreakerState.OPEN
        with patch("time.time", return_value=110.0):
            assert cb.is_eligible() is False
        assert cb.state == CircuitBreakerState.OPEN

    def test_open_after_timeout_eligible_without_transition(self) -> None:
        cb = CircuitBreaker(proxy_id="p1", failure_threshold=1, timeout_duration=10.0)
        with patch("time.time", return_value=100.0):
            cb.record_failure()
        with patch("time.time", return_value=111.0):
            assert cb.is_eligible() is True
        assert cb.state == CircuitBreakerState.OPEN

    def test_half_open_pending_not_eligible(self) -> None:
        cb = CircuitBreakerBase(
            proxy_id="p1",
            failure_threshold=1,
            timeout_duration=5.0,
        )
        with patch("time.time", return_value=100.0):
            cb._do_record_failure()
        with patch("time.time", return_value=106.0):
            assert cb._do_try_acquire_probe(106.0) is True
        assert cb.state == CircuitBreakerState.HALF_OPEN
        with patch("time.time", return_value=106.0):
            assert cb._do_is_eligible(106.0) is False


class TestTryAcquireProbeMutates:
    """try_acquire_probe reserves half-open probe slots (P-B-01)."""

    def test_acquire_transitions_open_to_half_open(self) -> None:
        cb = CircuitBreaker(proxy_id="p1", failure_threshold=1, timeout_duration=10.0)
        with patch("time.time", return_value=100.0):
            cb.record_failure()
        with patch("time.time", return_value=111.0):
            assert cb.try_acquire_probe() is True
        assert cb.state == CircuitBreakerState.HALF_OPEN

    def test_second_acquire_blocked_while_pending(self) -> None:
        cb = CircuitBreaker(proxy_id="p1", failure_threshold=1, timeout_duration=10.0)
        with patch("time.time", return_value=100.0):
            cb.record_failure()
        with patch("time.time", return_value=111.0):
            assert cb.try_acquire_probe() is True
            assert cb.try_acquire_probe() is False

    def test_should_attempt_request_is_acquire_when_eligible(self) -> None:
        cb = CircuitBreaker(proxy_id="p1", failure_threshold=1, timeout_duration=10.0)
        with patch("time.time", return_value=100.0):
            cb.record_failure()
        with patch("time.time", return_value=111.0):
            assert cb.should_attempt_request() is True
            assert cb.should_attempt_request() is False


class TestHalfOpenProbeTimeout:
    """Abandoned half-open probes clear after deadline (P-B-02)."""

    def test_stale_probe_becomes_eligible_again(self) -> None:
        cb = CircuitBreaker(
            proxy_id="p1",
            failure_threshold=1,
            timeout_duration=5.0,
            half_open_probe_timeout=2.0,
        )
        with patch("time.time", return_value=100.0):
            cb.record_failure()
        with patch("time.time", return_value=106.0):
            assert cb.try_acquire_probe() is True
        with patch("time.time", return_value=106.0):
            assert cb.is_eligible() is False
        with patch("time.time", return_value=109.0):
            assert cb.is_eligible() is True
        with patch("time.time", return_value=109.0):
            assert cb.try_acquire_probe() is True


@pytest.mark.asyncio
async def test_async_is_eligible_and_try_acquire_probe() -> None:
    """Async circuit breaker exposes the same eligibility API."""
    cb = AsyncCircuitBreaker(proxy_id="p1", failure_threshold=1, timeout_duration=10.0)
    with patch("time.time", return_value=100.0):
        await cb.record_failure()
    # Before timeout: not eligible
    with patch("time.time", return_value=105.0):
        assert await cb.is_eligible() is False
    # After timeout: eligible for probe; acquire then blocks further eligibility
    with patch("time.time", return_value=111.0):
        assert await cb.is_eligible() is True
        assert await cb.try_acquire_probe() is True
        assert cb.state == CircuitBreakerState.HALF_OPEN
        assert await cb.is_eligible() is False
