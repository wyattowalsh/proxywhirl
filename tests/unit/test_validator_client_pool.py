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
        """Test that same client is reused across multiple direct (non-proxied) validations.

        Note: When proxy_url is provided, httpx creates a new client each time because
        the proxy must be set at client initialization. The shared client pool is only
        used for direct requests (proxy_url=None).
        """
        validator = ProxyValidator()

        with patch.object(httpx, "AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(
                return_value=MagicMock(status_code=200, json=lambda: {"headers": {}})
            )
            mock_client_class.return_value = mock_client

            # First direct validation - should create client
            await validator._validate_http_request(None)

            # Second direct validation - should reuse client
            await validator._validate_http_request(None)

            # Client should only be created once (shared client pool)
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
            # Create mock limits object - actual values from fetchers.py
            mock_limits = MagicMock()
            mock_limits.max_connections = 1000
            mock_limits.max_keepalive_connections = 100

            # Mock the AsyncClient to capture the limits argument
            def create_client(**kwargs):
                limits = kwargs.get("limits")
                if limits:
                    # These values match ProxyValidator._get_client() implementation
                    assert limits.max_connections == 1000
                    assert limits.max_keepalive_connections == 100
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

    async def test_validate_batch_creates_per_proxy_clients(self):
        """Test that validate_batch creates a separate client for each proxied validation.

        Note: httpx requires the proxy to be set at client initialization, so each
        proxy validation creates its own client. The shared client pool is only used
        for direct (non-proxied) requests.
        """
        validator = ProxyValidator(concurrency=10)

        proxies = [
            {"url": "http://proxy1.example.com:8080"},
            {"url": "http://proxy2.example.com:8080"},
            {"url": "http://proxy3.example.com:8080"},
        ]

        with patch.object(httpx, "AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=MagicMock(status_code=200))
            mock_client.aclose = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client_class.return_value = mock_client

            # Mock asyncio.open_connection for TCP check
            with patch("asyncio.open_connection") as mock_open_conn:
                mock_writer = AsyncMock()
                mock_writer.close = MagicMock()
                mock_writer.wait_closed = AsyncMock()
                mock_open_conn.return_value = (AsyncMock(), mock_writer)

                await validator.validate_batch(proxies)

                # Each proxy validation creates its own client (httpx proxy requirement)
                assert mock_client_class.call_count == 3

                # Each client makes one GET request
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

    async def test_validate_creates_per_proxy_client(self):
        """Test that validate() creates a per-proxy client for proxied requests.

        Note: httpx requires the proxy to be set at client initialization, so each
        proxy validation creates its own client. The shared client pool is only used
        for direct (non-proxied) requests via _validate_http_request(None).
        """
        validator = ProxyValidator()

        proxy = {"url": "http://proxy.example.com:8080"}

        with patch.object(httpx, "AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=MagicMock(status_code=200))
            mock_client.aclose = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client_class.return_value = mock_client

            with patch("asyncio.open_connection") as mock_open_conn:
                mock_writer = AsyncMock()
                mock_writer.close = MagicMock()
                mock_writer.wait_closed = AsyncMock()
                mock_open_conn.return_value = (AsyncMock(), mock_writer)

                result = await validator.validate(proxy)

                # Should have created one client for this proxy
                assert mock_client_class.call_count == 1
                assert result.is_valid is True

        await validator.close()

    async def test_check_anonymity_uses_shared_client_for_direct_requests(self):
        """Test that check_anonymity(None) uses the shared client pool for direct requests.

        Note: When proxy_url is provided, a per-proxy client is created because httpx
        requires proxy at initialization. The shared client is only used when proxy_url=None.
        """
        validator = ProxyValidator()

        with patch.object(httpx, "AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(
                return_value=MagicMock(status_code=200, json=lambda: {"headers": {}})
            )
            mock_client_class.return_value = mock_client

            # Test with None (direct request) - should use shared client
            result = await validator.check_anonymity(None)

            # Should have created shared client once
            assert mock_client_class.call_count == 1
            assert result == "elite"

            # Second call should reuse the same client
            result2 = await validator.check_anonymity(None)
            assert mock_client_class.call_count == 1  # Still only 1 client
            assert result2 == "elite"

        await validator.close()

    async def test_check_anonymity_creates_per_proxy_client(self):
        """Test that check_anonymity() with proxy_url creates a per-proxy client.

        Note: httpx requires the proxy to be set at client initialization, so each
        proxied check creates its own client.
        """
        validator = ProxyValidator()

        with patch.object(httpx, "AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(
                return_value=MagicMock(status_code=200, json=lambda: {"headers": {}})
            )
            mock_client.aclose = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client_class.return_value = mock_client

            result = await validator.check_anonymity("http://proxy.example.com:8080")

            # Should have created one per-proxy client
            assert mock_client_class.call_count == 1
            assert result == "elite"

        await validator.close()

    async def test_socks_proxy_validation_creates_per_proxy_client(self):
        """Test that SOCKS proxy validation creates a per-proxy client with transport.

        Note: SOCKS validation creates a new client for each proxy with the appropriate
        AsyncProxyTransport configured at initialization.
        """
        validator = ProxyValidator()

        proxy = {"url": "socks5://proxy.example.com:1080"}

        # Patch the imported AsyncProxyTransport in fetchers module, not httpx_socks
        with patch("proxywhirl.fetchers.AsyncProxyTransport") as mock_transport:
            mock_transport.from_url.return_value = MagicMock()

            # Ensure SOCKS_AVAILABLE is True for this test
            with patch("proxywhirl.fetchers.SOCKS_AVAILABLE", True):
                with patch.object(httpx, "AsyncClient") as mock_client_class:
                    mock_client = AsyncMock()
                    mock_client.get = AsyncMock(return_value=MagicMock(status_code=200))
                    mock_client.aclose = AsyncMock()
                    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
                    mock_client.__aexit__ = AsyncMock(return_value=None)
                    mock_client_class.return_value = mock_client

                    with patch("asyncio.open_connection") as mock_open_conn:
                        mock_writer = AsyncMock()
                        mock_writer.close = MagicMock()
                        mock_writer.wait_closed = AsyncMock()
                        mock_open_conn.return_value = (AsyncMock(), mock_writer)

                        result = await validator.validate(proxy)

                        # Should have created SOCKS transport from URL
                        assert mock_transport.from_url.called
                        mock_transport.from_url.assert_called_with(proxy["url"])

                        # Should have created client with transport
                        assert mock_client_class.call_count == 1
                        assert result.is_valid is True

        await validator.close()
