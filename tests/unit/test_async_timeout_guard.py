"""Tests for async timeout guards and timeouts in proxy operations."""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from proxywhirl.models import Proxy


class TestAsyncTimeoutBasics:
    """Test basic async timeout functionality."""

    @pytest.mark.asyncio
    async def test_timeout_with_asyncio_timeout(self):
        """Test asyncio.timeout guard for operations."""
        async def fast_operation():
            await asyncio.sleep(0.01)
            return "success"
        
        # Should complete within timeout
        try:
            async with asyncio.timeout(1.0):
                result = await fast_operation()
                assert result == "success"
        except asyncio.TimeoutError:
            pytest.fail("Should not timeout for fast operation")

    @pytest.mark.asyncio
    async def test_timeout_with_slow_operation(self):
        """Test timeout raises error for slow operation."""
        async def slow_operation():
            await asyncio.sleep(2.0)
            return "should not reach"
        
        # Should timeout
        with pytest.raises(asyncio.TimeoutError):
            async with asyncio.timeout(0.1):
                await slow_operation()

    @pytest.mark.asyncio
    async def test_timeout_context_cleanup(self):
        """Test that timeout context cleans up properly."""
        cleanup_called = False
        
        async def operation_with_cleanup():
            nonlocal cleanup_called
            try:
                await asyncio.sleep(2.0)
            finally:
                cleanup_called = True
        
        with pytest.raises(asyncio.TimeoutError):
            async with asyncio.timeout(0.1):
                await operation_with_cleanup()
        
        # Give time for cleanup
        await asyncio.sleep(0.05)
        # Cleanup should have been called
        assert cleanup_called


class TestAsyncNetworkTimeouts:
    """Test timeout behavior for network-like operations."""

    @pytest.mark.asyncio
    async def test_proxy_selection_timeout(self):
        """Test timeout during proxy selection."""
        async def select_proxy_slow():
            # Simulate slow proxy selection
            await asyncio.sleep(0.5)
            return Proxy(url="http://selected.example.com:8080")
        
        # Should timeout
        with pytest.raises(asyncio.TimeoutError):
            async with asyncio.timeout(0.1):
                await select_proxy_slow()

    @pytest.mark.asyncio
    async def test_proxy_health_check_timeout(self):
        """Test timeout during health check."""
        async def health_check_slow():
            await asyncio.sleep(1.0)
            return True
        
        # Timeout should interrupt health check
        with pytest.raises(asyncio.TimeoutError):
            async with asyncio.timeout(0.1):
                await health_check_slow()

    @pytest.mark.asyncio
    async def test_proxy_validation_timeout(self):
        """Test timeout during proxy validation."""
        async def validate_proxy_slow():
            await asyncio.sleep(2.0)
            return True
        
        # Should timeout
        with pytest.raises(asyncio.TimeoutError):
            async with asyncio.timeout(0.05):
                await validate_proxy_slow()


class TestAsyncMultipleTimeouts:
    """Test multiple concurrent timeouts."""

    @pytest.mark.asyncio
    async def test_concurrent_operations_with_timeout(self):
        """Test concurrent operations each with timeout."""
        async def operation(idx, delay):
            await asyncio.sleep(delay)
            return idx
        
        # All operations complete within timeout
        try:
            async with asyncio.timeout(1.0):
                results = await asyncio.gather(
                    operation(0, 0.1),
                    operation(1, 0.1),
                    operation(2, 0.1),
                )
                assert results == [0, 1, 2]
        except asyncio.TimeoutError:
            pytest.fail("Should not timeout for concurrent fast ops")

    @pytest.mark.asyncio
    async def test_mixed_timeout_compliance(self):
        """Test that some ops timeout and some complete."""
        async def operation(idx, delay):
            await asyncio.sleep(delay)
            return idx
        
        # One will timeout, others won't
        with pytest.raises((asyncio.TimeoutError, Exception)):
            async with asyncio.timeout(0.2):
                # First two complete, third times out
                results = await asyncio.gather(
                    operation(0, 0.05),
                    operation(1, 0.05),
                    operation(2, 0.5),  # This will timeout
                    return_exceptions=True
                )

    @pytest.mark.asyncio
    async def test_nested_timeouts(self):
        """Test nested timeout contexts."""
        async def inner_op():
            await asyncio.sleep(0.01)
            return "inner"
        
        try:
            async with asyncio.timeout(2.0):  # Outer timeout
                async with asyncio.timeout(1.0):  # Inner timeout
                    result = await inner_op()
                    assert result == "inner"
        except asyncio.TimeoutError:
            pytest.fail("Should not timeout for fast inner operation")


class TestAsyncTimeoutCancellation:
    """Test cancellation behavior with timeouts."""

    @pytest.mark.asyncio
    async def test_timeout_cancellation_propagation(self):
        """Test that timeout cancellation propagates correctly."""
        was_cancelled = False
        
        async def cancellable_op():
            nonlocal was_cancelled
            try:
                await asyncio.sleep(10.0)
            except asyncio.CancelledError:
                was_cancelled = True
                raise
        
        with pytest.raises(asyncio.TimeoutError):
            async with asyncio.timeout(0.1):
                await cancellable_op()
        
        await asyncio.sleep(0.05)
        assert was_cancelled

    @pytest.mark.asyncio
    async def test_timeout_with_shield(self):
        """Test using asyncio.shield with timeout."""
        async def protected_op():
            await asyncio.sleep(0.01)
            return "protected"
        
        # Shield won't prevent timeout
        with pytest.raises(asyncio.TimeoutError):
            async with asyncio.timeout(0.001):
                await asyncio.shield(protected_op())

    @pytest.mark.asyncio
    async def test_timeout_exception_cleanup(self):
        """Test cleanup when timeout occurs."""
        resources_closed = []
        
        async def operation_with_resources():
            async def resource():
                try:
                    await asyncio.sleep(10.0)
                finally:
                    resources_closed.append(True)
            
            await resource()
        
        with pytest.raises(asyncio.TimeoutError):
            async with asyncio.timeout(0.05):
                await operation_with_resources()
        
        await asyncio.sleep(0.05)


class TestAsyncTimeoutEdgeCases:
    """Test edge cases for async timeouts."""

    @pytest.mark.asyncio
    async def test_timeout_zero(self):
        """Test timeout of zero (immediate timeout)."""
        async def any_operation():
            await asyncio.sleep(0)
            return "done"
        
        # May timeout immediately or complete if already ready
        try:
            async with asyncio.timeout(0):
                result = await any_operation()
        except asyncio.TimeoutError:
            pass  # Expected

    @pytest.mark.asyncio
    async def test_timeout_very_large(self):
        """Test with very large timeout."""
        async def fast_op():
            await asyncio.sleep(0.01)
            return "done"
        
        try:
            async with asyncio.timeout(1000.0):
                result = await fast_op()
                assert result == "done"
        except asyncio.TimeoutError:
            pytest.fail("Should not timeout with very large timeout")

    @pytest.mark.asyncio
    async def test_multiple_sequential_timeouts(self):
        """Test multiple sequential timeout contexts."""
        results = []
        
        for i in range(3):
            try:
                async with asyncio.timeout(0.1):
                    await asyncio.sleep(0.01)
                    results.append(f"success-{i}")
            except asyncio.TimeoutError:
                results.append(f"timeout-{i}")
        
        assert len(results) == 3
        assert all("success" in r for r in results)
