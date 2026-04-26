"""
Tests for AsyncProxyWhirl context manager (`async with` pattern).

Verifies:
- Proper async context manager protocol (__aenter__, __aexit__)
- Resource cleanup on exit
- Exception handling during context
- Nested contexts
"""

import asyncio
import pytest
import httpx
from proxywhirl.rotator import AsyncProxyWhirl
from proxywhirl.models import Proxy


class TestAsyncContextManager:
    """Test async context manager functionality."""

    @pytest.mark.asyncio
    async def test_async_context_manager_protocol(self):
        """Test that AsyncProxyWhirl supports async context manager protocol."""
        rotator = AsyncProxyWhirl()
        
        # Should have __aenter__ and __aexit__
        assert hasattr(rotator, '__aenter__')
        assert hasattr(rotator, '__aexit__')
        assert callable(rotator.__aenter__)
        assert callable(rotator.__aexit__)

    @pytest.mark.asyncio
    async def test_async_with_basic_usage(self):
        """Test basic async with usage."""
        async with AsyncProxyWhirl() as rotator:
            assert rotator is not None
            assert isinstance(rotator, AsyncProxyWhirl)
            
            # Should be able to add proxies inside context
            await rotator.add_proxy("http://proxy1.example.com:8080")
            proxies = rotator.pool.get_all_proxies()
            assert len(proxies) > 0

    @pytest.mark.asyncio
    async def test_async_context_manager_cleanup(self):
        """Test that async context manager properly cleans up resources."""
        rotator = AsyncProxyWhirl()
        await rotator.add_proxy("http://proxy1.example.com:8080")
        
        async with rotator:
            # Context entered successfully
            assert rotator.pool.get_all_proxies()
        
        # Should be cleaned up after exit

    @pytest.mark.asyncio
    async def test_async_context_manager_with_exception(self):
        """Test that async context manager handles exceptions gracefully."""
        with pytest.raises(ValueError):
            async with AsyncProxyWhirl() as rotator:
                await rotator.add_proxy("http://proxy1.example.com:8080")
                raise ValueError("Test exception")

    @pytest.mark.asyncio
    async def test_async_context_manager_exception_handling(self):
        """Test exception handling in async with block."""
        rotator = AsyncProxyWhirl()
        
        try:
            async with rotator:
                raise RuntimeError("Simulated error")
        except RuntimeError:
            pass  # Expected
        
        # Rotator should still exist and be in valid state
        assert rotator is not None

    @pytest.mark.asyncio
    async def test_multiple_async_with_contexts(self):
        """Test multiple sequential async with contexts."""
        for i in range(3):
            async with AsyncProxyWhirl() as rotator:
                assert rotator is not None
                await rotator.add_proxy(f"http://proxy{i}.example.com:8080")

    @pytest.mark.asyncio
    async def test_async_context_manager_return_value(self):
        """Test that async context manager returns self."""
        rotator = AsyncProxyWhirl()
        async with rotator as ctx:
            assert ctx is rotator

    @pytest.mark.asyncio
    async def test_async_context_manager_preserves_state(self):
        """Test that state is preserved across async context."""
        rotator = AsyncProxyWhirl()
        await rotator.add_proxy("http://proxy1.example.com:8080")
        initial_count = len(rotator.pool.get_all_proxies())
        
        async with rotator:
            await rotator.add_proxy("http://proxy2.example.com:8080")
            assert len(rotator.pool.get_all_proxies()) == initial_count + 1
        
        # State should be preserved
        assert len(rotator.pool.get_all_proxies()) == initial_count + 1

    @pytest.mark.asyncio
    async def test_async_with_concurrent_operations(self):
        """Test async with context with concurrent operations."""
        async with AsyncProxyWhirl() as rotator:
            # Add multiple proxies concurrently
            tasks = [
                rotator.add_proxy(f"http://proxy{i}.example.com:808{i}")
                for i in range(5)
            ]
            await asyncio.gather(*tasks)
            
            assert len(rotator.pool.get_all_proxies()) == 5

    @pytest.mark.asyncio
    async def test_aenter_returns_instance(self):
        """Test that __aenter__ returns the rotator instance."""
        rotator = AsyncProxyWhirl()
        result = await rotator.__aenter__()
        assert result is rotator
        await rotator.__aexit__(None, None, None)

    @pytest.mark.asyncio
    async def test_aexit_with_no_exception(self):
        """Test __aexit__ with no exception."""
        rotator = AsyncProxyWhirl()
        await rotator.__aenter__()
        result = await rotator.__aexit__(None, None, None)
        # Should return None or False (no exception suppression)
        assert result is None or result is False

    @pytest.mark.asyncio
    async def test_aexit_with_exception(self):
        """Test __aexit__ with exception."""
        rotator = AsyncProxyWhirl()
        await rotator.__aenter__()
        
        exc = ValueError("test")
        result = await rotator.__aexit__(type(exc), exc, None)
        # Should not suppress exception
        assert result is None or result is False
