"""Unit tests for proxy anonymity detection."""

import httpx
import respx

from proxywhirl.fetchers import ProxyValidator
from proxywhirl.models import ValidationLevel

# Fixed test URL to avoid rotation issues with respx mocking
TEST_URL = "http://test.example.com/check"


class TestAnonymityDetection:
    """Test proxy anonymity level detection."""

    async def test_anonymity_transparent(self) -> None:
        """T016: Test detection of transparent proxy (leaks real IP)."""
        validator = ProxyValidator(level=ValidationLevel.FULL, test_url=TEST_URL)

        # Mock response that reveals real IP in headers
        with respx.mock:
            mock_response_data = {
                "origin": "1.2.3.4",  # Real IP
                "headers": {
                    "X-Forwarded-For": "1.2.3.4",  # Leaks real IP
                    "Via": "1.1 proxy.example.com",  # Reveals proxy
                },
            }
            respx.get(TEST_URL).mock(return_value=httpx.Response(200, json=mock_response_data))

            anonymity_level = await validator.check_anonymity()

            assert anonymity_level == "transparent"

    async def test_anonymity_anonymous(self) -> None:
        """T017: Test detection of anonymous proxy (hides IP but reveals proxy use)."""
        validator = ProxyValidator(level=ValidationLevel.FULL, test_url=TEST_URL)

        # Mock response that hides real IP but shows proxy headers
        with respx.mock:
            mock_response_data = {
                "origin": "5.6.7.8",  # Proxy IP, not real IP
                "headers": {
                    "Via": "1.1 proxy.example.com",  # Reveals it's a proxy
                },
            }
            respx.get(TEST_URL).mock(return_value=httpx.Response(200, json=mock_response_data))

            anonymity_level = await validator.check_anonymity()

            assert anonymity_level == "anonymous"

    async def test_anonymity_elite(self) -> None:
        """T018: Test detection of elite proxy (completely hides proxy use)."""
        validator = ProxyValidator(level=ValidationLevel.FULL, test_url=TEST_URL)

        # Mock response with no proxy-revealing headers
        with respx.mock:
            mock_response_data = {
                "origin": "5.6.7.8",  # Proxy IP
                "headers": {
                    "User-Agent": "Mozilla/5.0...",  # Normal headers only
                },
            }
            respx.get(TEST_URL).mock(return_value=httpx.Response(200, json=mock_response_data))

            anonymity_level = await validator.check_anonymity()

            assert anonymity_level == "elite"

    async def test_anonymity_check_with_x_real_ip(self) -> None:
        """Test transparent detection via X-Real-IP header."""
        validator = ProxyValidator(level=ValidationLevel.FULL, test_url=TEST_URL)

        with respx.mock:
            mock_response_data = {
                "origin": "5.6.7.8",
                "headers": {
                    "X-Real-IP": "1.2.3.4",  # Leaks real IP
                },
            }
            respx.get(TEST_URL).mock(return_value=httpx.Response(200, json=mock_response_data))

            anonymity_level = await validator.check_anonymity()

            assert anonymity_level == "transparent"

    async def test_anonymity_check_with_proxy_connection(self) -> None:
        """Test anonymous detection via Proxy-Connection header."""
        validator = ProxyValidator(level=ValidationLevel.FULL, test_url=TEST_URL)

        with respx.mock:
            mock_response_data = {
                "origin": "5.6.7.8",
                "headers": {
                    "Proxy-Connection": "keep-alive",  # Reveals proxy
                },
            }
            respx.get(TEST_URL).mock(return_value=httpx.Response(200, json=mock_response_data))

            anonymity_level = await validator.check_anonymity()

            assert anonymity_level == "anonymous"

    async def test_anonymity_check_network_error(self) -> None:
        """Test anonymity check gracefully handles network errors."""
        validator = ProxyValidator(level=ValidationLevel.FULL, test_url=TEST_URL)

        with respx.mock:
            respx.get(TEST_URL).mock(side_effect=httpx.NetworkError("Network unreachable"))

            anonymity_level = await validator.check_anonymity()

            # Network errors should return None or "unknown"
            assert anonymity_level in (None, "unknown")

    async def test_anonymity_check_timeout(self) -> None:
        """Test anonymity check handles timeout gracefully."""
        validator = ProxyValidator(level=ValidationLevel.FULL, timeout=2.0, test_url=TEST_URL)

        with respx.mock:
            respx.get(TEST_URL).mock(side_effect=httpx.TimeoutException("Request timed out"))

            anonymity_level = await validator.check_anonymity()

            assert anonymity_level in (None, "unknown")
