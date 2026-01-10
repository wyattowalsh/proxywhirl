"""Tests for ProxyValidator client pool implementation."""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx

from proxywhirl.fetchers import ProxyValidator


class TestProxyValidatorClientPool:
    """Test ProxyValidator shared client pool functionality."""

    async def test_client_pool_created_lazily(self):
        """Test that client is created lazily on first use."""
        validator = ProxyValidator()

        # Client should be None initially
        assert validator._client is None
        assert validator._socks_client is None

        # Get client - should create it
        client = await validator._get_client()
        assert client is not None
        assert isinstance(client, httpx.AsyncClient)
        assert validator._client is not None

        # Second call should return same client
        client2 = await validator._get_client()
        assert client2 is client

        await validator.close()

    async def test_client_pool_reused_across_validations(self):
        """Test that same client is reused across multiple validations."""
        validator = ProxyValidator()

        with patch.object(httpx, "AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(
                return_value=MagicMock(status_code=200, json=lambda: {"headers": {}})
            )
            mock_client_class.return_value = mock_client

            # First validation - should create client
            await validator._validate_http_request("http://proxy1.example.com:8080")

            # Second validation - should reuse client
            await validator._validate_http_request("http://proxy2.example.com:8080")

            # Client should only be created once
            assert mock_client_class.call_count == 1

            # But get() should be called twice
            assert mock_client.get.call_count == 2

        await validator.close()

    async def test_context_manager_cleanup(self):
        """Test that context manager properly cleans up clients."""
        async with ProxyValidator() as validator:
            # Get client to create it
            client = await validator._get_client()
            assert client is not None
            assert validator._client is not None

        # After exiting context, client should be closed and None
        assert validator._client is None

    async def test_close_method(self):
        """Test that close() method properly cleans up all clients."""
        validator = ProxyValidator()

        # Create both HTTP and SOCKS clients
        await validator._get_client()

        # Mock SOCKS client creation
        with patch("httpx_socks.AsyncProxyTransport") as mock_transport:
            mock_transport.from_url.return_value = MagicMock()
            with patch.object(httpx, "AsyncClient") as mock_socks_client_class:
                mock_socks_client = AsyncMock()
                mock_socks_client_class.return_value = mock_socks_client

                socks_client = await validator._get_socks_client("socks5://proxy.example.com:1080")
                assert socks_client is not None
                assert validator._socks_client is not None

        # Both clients should exist
        assert validator._client is not None
        assert validator._socks_client is not None

        # Close should clean up both
        await validator.close()

        assert validator._client is None
        assert validator._socks_client is None

    async def test_client_pool_limits(self):
        """Test that client is created with proper connection limits."""
        with patch.object(httpx, "AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            # Create mock limits object
            mock_limits = MagicMock()
            mock_limits.max_connections = 100
            mock_limits.max_keepalive_connections = 20

            # Mock the AsyncClient to capture the limits argument
            def create_client(**kwargs):
                limits = kwargs.get("limits")
                if limits:
                    assert limits.max_connections == 100
                    assert limits.max_keepalive_connections == 20
                return mock_client

            mock_client_class.side_effect = create_client

            validator = ProxyValidator()
            await validator._get_client()

            # Verify client was created with correct parameters
            assert mock_client_class.called

            await validator.close()

    async def test_socks_client_separate_from_http(self):
        """Test that SOCKS client is separate from HTTP client."""
        validator = ProxyValidator()

        # Create HTTP client
        http_client = await validator._get_client()

        # Mock SOCKS transport with proper async support
        with patch("httpx_socks.AsyncProxyTransport") as mock_transport_class:
            # Create mock transport that supports async close
            mock_transport = AsyncMock()
            mock_transport.aclose = AsyncMock()
            mock_transport_class.from_url.return_value = mock_transport

            # Create SOCKS client
            socks_client = await validator._get_socks_client("socks5://proxy.example.com:1080")

            # Should be different clients
            assert socks_client is not http_client
            assert validator._client is not None
            assert validator._socks_client is not None
            assert validator._client is not validator._socks_client

        await validator.close()

    async def test_validate_batch_uses_shared_client(self):
        """Test that validate_batch uses the shared client for all validations."""
        validator = ProxyValidator(concurrency=10)

        proxies = [
            {"url": "http://proxy1.example.com:8080"},
            {"url": "http://proxy2.example.com:8080"},
            {"url": "http://proxy3.example.com:8080"},
        ]

        with patch.object(httpx, "AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=MagicMock(status_code=200))
            mock_client_class.return_value = mock_client

            # Mock asyncio.open_connection for TCP check
            with patch("asyncio.open_connection") as mock_open_conn:
                mock_writer = AsyncMock()
                mock_open_conn.return_value = (AsyncMock(), mock_writer)

                await validator.validate_batch(proxies)

                # Client should only be created once despite 3 validations
                assert mock_client_class.call_count == 1

                # But get() should be called 3 times (once per proxy)
                assert mock_client.get.call_count == 3

        await validator.close()

    async def test_multiple_close_calls_safe(self):
        """Test that calling close() multiple times is safe."""
        validator = ProxyValidator()

        # Create client
        await validator._get_client()
        assert validator._client is not None

        # First close
        await validator.close()
        assert validator._client is None

        # Second close should not raise error
        await validator.close()
        assert validator._client is None

    async def test_client_recreation_after_close(self):
        """Test that client can be recreated after being closed."""
        validator = ProxyValidator()

        # Create and close first client
        await validator._get_client()
        await validator.close()

        # Create new client - should be a fresh instance
        client2 = await validator._get_client()
        assert client2 is not None

        # Note: Can't compare identity since close() sets to None
        # But we can verify it's a new client by checking it exists
        assert validator._client is not None

        await validator.close()


class TestProxyValidatorIntegrationWithClientPool:
    """Integration tests for ProxyValidator using client pool."""

    async def test_validate_uses_client_pool(self):
        """Test that validate() method uses the shared client pool."""
        validator = ProxyValidator()

        proxy = {"url": "http://proxy.example.com:8080"}

        with patch.object(httpx, "AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=MagicMock(status_code=200))
            mock_client_class.return_value = mock_client

            with patch("asyncio.open_connection") as mock_open_conn:
                mock_writer = AsyncMock()
                mock_open_conn.return_value = (AsyncMock(), mock_writer)

                result = await validator.validate(proxy)

                # Should have created client once
                assert mock_client_class.call_count == 1
                assert result is True

        await validator.close()

    async def test_check_anonymity_uses_client_pool(self):
        """Test that check_anonymity() method uses the shared client pool."""
        validator = ProxyValidator()

        with patch.object(httpx, "AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(
                return_value=MagicMock(status_code=200, json=lambda: {"headers": {}})
            )
            mock_client_class.return_value = mock_client

            result = await validator.check_anonymity("http://proxy.example.com:8080")

            # Should have created client once
            assert mock_client_class.call_count == 1
            assert result == "elite"

        await validator.close()

    async def test_socks_proxy_validation_uses_separate_client(self):
        """Test that SOCKS proxy validation uses separate client pool."""
        validator = ProxyValidator()

        proxy = {"url": "socks5://proxy.example.com:1080"}

        with patch("httpx_socks.AsyncProxyTransport") as mock_transport:
            mock_transport.from_url.return_value = MagicMock()

            with patch.object(httpx, "AsyncClient") as mock_client_class:
                mock_client = AsyncMock()
                mock_client.get = AsyncMock(return_value=MagicMock(status_code=200))
                mock_client_class.return_value = mock_client

                with patch("asyncio.open_connection") as mock_open_conn:
                    mock_writer = AsyncMock()
                    mock_open_conn.return_value = (AsyncMock(), mock_writer)

                    result = await validator.validate(proxy)

                    # Should have created SOCKS client
                    assert mock_transport.from_url.called
                    assert result is True

        await validator.close()
