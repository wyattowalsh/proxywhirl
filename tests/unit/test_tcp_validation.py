"""Unit tests for TCP connectivity validation."""

import socket
from unittest.mock import MagicMock, patch

from proxywhirl.fetchers import ProxyValidator
from proxywhirl.models import ValidationLevel


class TestTCPConnectivity:
    """Test TCP connectivity validation."""

    async def test_tcp_connect_success(self) -> None:
        """T006: Test successful TCP connection to proxy."""
        validator = ProxyValidator(level=ValidationLevel.BASIC)

        # Mock successful socket connection
        with patch("socket.create_connection") as mock_connect:
            mock_socket = MagicMock()
            mock_connect.return_value = mock_socket

            result = await validator._validate_tcp_connectivity("proxy.example.com", 8080)

            assert result is True
            mock_connect.assert_called_once_with(
                ("proxy.example.com", 8080), timeout=validator.timeout
            )
            mock_socket.close.assert_called_once()

    async def test_tcp_connect_timeout(self) -> None:
        """T007: Test TCP connection timeout."""
        validator = ProxyValidator(level=ValidationLevel.BASIC, timeout=2.0)

        # Mock timeout exception
        with patch("socket.create_connection") as mock_connect:
            mock_connect.side_effect = socket.timeout("Connection timed out")

            result = await validator._validate_tcp_connectivity("slow.proxy.com", 8080)

            assert result is False

    async def test_tcp_connect_refused(self) -> None:
        """T008: Test TCP connection refused."""
        validator = ProxyValidator(level=ValidationLevel.BASIC)

        # Mock connection refused
        with patch("socket.create_connection") as mock_connect:
            mock_connect.side_effect = ConnectionRefusedError("Connection refused")

            result = await validator._validate_tcp_connectivity("dead.proxy.com", 8080)

            assert result is False

    async def test_tcp_connect_invalid_host(self) -> None:
        """Test TCP connection with invalid hostname."""
        validator = ProxyValidator(level=ValidationLevel.BASIC)

        # Mock DNS resolution failure
        with patch("socket.create_connection") as mock_connect:
            mock_connect.side_effect = socket.gaierror("Name or service not known")

            result = await validator._validate_tcp_connectivity("invalid.proxy", 8080)

            assert result is False

    async def test_tcp_connect_network_unreachable(self) -> None:
        """Test TCP connection when network is unreachable."""
        validator = ProxyValidator(level=ValidationLevel.BASIC)

        # Mock network unreachable error
        with patch("socket.create_connection") as mock_connect:
            mock_connect.side_effect = OSError("Network is unreachable")

            result = await validator._validate_tcp_connectivity("unreachable.proxy.com", 8080)

            assert result is False
