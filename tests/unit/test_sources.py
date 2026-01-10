"""Unit tests for proxy sources module."""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx

from proxywhirl.sources import (
    ProxySourceConfig,
    SourceValidationReport,
    SourceValidationResult,
    _get_source_name,
    validate_source,
    validate_sources,
    validate_sources_sync,
)


class TestSourceValidationResult:
    """Tests for SourceValidationResult dataclass."""

    def test_is_healthy_all_conditions_met(self):
        """Test is_healthy returns True when all conditions are met."""
        source = ProxySourceConfig(url="http://example.com/proxies.txt")
        result = SourceValidationResult(
            source=source,
            name="test",
            status_code=200,
            content_length=100,
            has_proxies=True,
            error=None,
            response_time_ms=50.0,
        )
        assert result.is_healthy is True

    def test_is_healthy_false_when_status_not_200(self):
        """Test is_healthy returns False when status code is not 200."""
        source = ProxySourceConfig(url="http://example.com/proxies.txt")
        result = SourceValidationResult(
            source=source,
            name="test",
            status_code=404,
            content_length=0,
            has_proxies=False,
            error=None,
            response_time_ms=50.0,
        )
        assert result.is_healthy is False

    def test_is_healthy_false_when_no_proxies(self):
        """Test is_healthy returns False when has_proxies is False."""
        source = ProxySourceConfig(url="http://example.com/proxies.txt")
        result = SourceValidationResult(
            source=source,
            name="test",
            status_code=200,
            content_length=100,
            has_proxies=False,
            error=None,
            response_time_ms=50.0,
        )
        assert result.is_healthy is False

    def test_is_healthy_false_when_error_present(self):
        """Test is_healthy returns False when error is present."""
        source = ProxySourceConfig(url="http://example.com/proxies.txt")
        result = SourceValidationResult(
            source=source,
            name="test",
            status_code=200,
            content_length=100,
            has_proxies=True,
            error="Connection timeout",
            response_time_ms=50.0,
        )
        assert result.is_healthy is False

    def test_is_healthy_false_when_status_none(self):
        """Test is_healthy returns False when status_code is None."""
        source = ProxySourceConfig(url="http://example.com/proxies.txt")
        result = SourceValidationResult(
            source=source,
            name="test",
            status_code=None,
            content_length=0,
            has_proxies=False,
            error="Connection failed",
            response_time_ms=50.0,
        )
        assert result.is_healthy is False


class TestSourceValidationReport:
    """Tests for SourceValidationReport dataclass."""

    def _create_result(self, healthy: bool) -> SourceValidationResult:
        """Helper to create a validation result."""
        source = ProxySourceConfig(url="http://example.com/proxies.txt")
        return SourceValidationResult(
            source=source,
            name="test",
            status_code=200 if healthy else 404,
            content_length=100 if healthy else 0,
            has_proxies=healthy,
            error=None if healthy else "Error",
            response_time_ms=50.0,
        )

    def test_healthy_property_returns_healthy_results(self):
        """Test healthy property returns only healthy results."""
        results = [
            self._create_result(healthy=True),
            self._create_result(healthy=False),
            self._create_result(healthy=True),
        ]
        report = SourceValidationReport(
            results=results,
            total_sources=3,
            healthy_sources=2,
            unhealthy_sources=1,
            total_time_ms=100.0,
        )

        healthy = report.healthy
        assert len(healthy) == 2
        for r in healthy:
            assert r.is_healthy is True

    def test_unhealthy_property_returns_unhealthy_results(self):
        """Test unhealthy property returns only unhealthy results."""
        results = [
            self._create_result(healthy=True),
            self._create_result(healthy=False),
            self._create_result(healthy=False),
        ]
        report = SourceValidationReport(
            results=results,
            total_sources=3,
            healthy_sources=1,
            unhealthy_sources=2,
            total_time_ms=100.0,
        )

        unhealthy = report.unhealthy
        assert len(unhealthy) == 2
        for r in unhealthy:
            assert r.is_healthy is False

    def test_all_healthy_true_when_no_unhealthy(self):
        """Test all_healthy returns True when all sources are healthy."""
        results = [
            self._create_result(healthy=True),
            self._create_result(healthy=True),
        ]
        report = SourceValidationReport(
            results=results,
            total_sources=2,
            healthy_sources=2,
            unhealthy_sources=0,
            total_time_ms=100.0,
        )
        assert report.all_healthy is True

    def test_all_healthy_false_when_some_unhealthy(self):
        """Test all_healthy returns False when any source is unhealthy."""
        results = [
            self._create_result(healthy=True),
            self._create_result(healthy=False),
        ]
        report = SourceValidationReport(
            results=results,
            total_sources=2,
            healthy_sources=1,
            unhealthy_sources=1,
            total_time_ms=100.0,
        )
        assert report.all_healthy is False


class TestGetSourceName:
    """Tests for _get_source_name function."""

    def test_github_url_extraction(self):
        """Test extracting name from GitHub raw URL."""
        source = ProxySourceConfig(
            url="https://raw.githubusercontent.com/owner/repo/main/proxies.txt"
        )
        name = _get_source_name(source)
        assert "owner" in name
        assert "repo" in name
        assert "PROXIES" in name

    def test_geonode_http(self):
        """Test GeoNode HTTP source naming."""
        source = ProxySourceConfig(url="https://proxylist.geonode.com/api/proxy-list?limit=500")
        name = _get_source_name(source)
        assert "GeoNode" in name
        assert "HTTP" in name

    def test_geonode_socks4(self):
        """Test GeoNode SOCKS4 source naming."""
        source = ProxySourceConfig(
            url="https://proxylist.geonode.com/api/proxy-list?protocols=socks4"
        )
        name = _get_source_name(source)
        assert "GeoNode" in name
        assert "SOCKS4" in name

    def test_geonode_socks5(self):
        """Test GeoNode SOCKS5 source naming."""
        source = ProxySourceConfig(
            url="https://proxylist.geonode.com/api/proxy-list?protocols=socks5"
        )
        name = _get_source_name(source)
        assert "GeoNode" in name
        assert "SOCKS5" in name

    def test_proxyscrape_http(self):
        """Test ProxyScrape HTTP source naming."""
        source = ProxySourceConfig(
            url="https://api.proxyscrape.com/v2/?request=getproxies&protocol=http"
        )
        name = _get_source_name(source)
        assert "ProxyScrape" in name
        assert "HTTP" in name

    def test_proxyscrape_socks4(self):
        """Test ProxyScrape SOCKS4 source naming."""
        source = ProxySourceConfig(
            url="https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks4"
        )
        name = _get_source_name(source)
        assert "ProxyScrape" in name
        assert "SOCKS4" in name

    def test_proxyscrape_socks5(self):
        """Test ProxyScrape SOCKS5 source naming."""
        source = ProxySourceConfig(
            url="https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks5"
        )
        name = _get_source_name(source)
        assert "ProxyScrape" in name
        assert "SOCKS5" in name

    def test_proxyscrape_country_specific(self):
        """Test ProxyScrape country-specific source naming."""
        for country, expected in [("US", "US"), ("DE", "DE"), ("FR", "FR"), ("GB", "GB")]:
            source = ProxySourceConfig(url=f"https://api.proxyscrape.com/v2/?country={country}")
            name = _get_source_name(source)
            assert "ProxyScrape" in name
            assert expected in name

    def test_proxyspace_source(self):
        """Test ProxySpace source naming."""
        source = ProxySourceConfig(url="https://proxyspace.pro/http.txt")
        name = _get_source_name(source)
        assert "ProxySpace" in name
        assert "HTTP" in name

    def test_openproxylist_source(self):
        """Test OpenProxyList source naming."""
        source = ProxySourceConfig(url="https://openproxylist.xyz/http.txt")
        name = _get_source_name(source)
        assert "OpenProxyList" in name

    def test_unknown_source_truncation(self):
        """Test unknown source URL truncation."""
        long_url = "https://example.com/" + "x" * 100
        source = ProxySourceConfig(url=long_url)
        name = _get_source_name(source)
        assert len(name) <= 53  # 50 chars + "..."
        assert "..." in name

    def test_short_unknown_source(self):
        """Test short unknown source URL."""
        source = ProxySourceConfig(url="https://short.com/p.txt")
        name = _get_source_name(source)
        assert name == "https://short.com/p.txt"


class TestValidateSource:
    """Tests for validate_source async function."""

    async def test_validate_source_success(self):
        """Test successful source validation."""
        source = ProxySourceConfig(url="http://example.com/proxies.txt")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "192.168.1.1:8080\n10.0.0.1:3128\n" + "x" * 100

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response

        result = await validate_source(source, client=mock_client)

        assert result.status_code == 200
        assert result.has_proxies is True
        assert result.error is None
        assert result.response_time_ms > 0

    async def test_validate_source_failure(self):
        """Test source validation with error."""
        source = ProxySourceConfig(url="http://example.com/proxies.txt")

        mock_client = AsyncMock()
        mock_client.get.side_effect = httpx.TimeoutException("Timeout")

        result = await validate_source(source, client=mock_client)

        assert result.status_code is None
        assert result.has_proxies is False
        assert result.error is not None
        assert "Timeout" in result.error

    async def test_validate_source_no_proxy_content(self):
        """Test validation with content that doesn't look like proxies."""
        source = ProxySourceConfig(url="http://example.com/empty.txt")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "Just some random text without IPs"

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response

        result = await validate_source(source, client=mock_client)

        assert result.status_code == 200
        assert result.has_proxies is False  # No IP patterns detected

    async def test_validate_source_404(self):
        """Test validation with 404 response."""
        source = ProxySourceConfig(url="http://example.com/notfound.txt")

        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response

        result = await validate_source(source, client=mock_client)

        assert result.status_code == 404
        assert result.has_proxies is False
        assert result.content_length == 0  # Empty content for non-200

    async def test_validate_source_without_client(self):
        """Test validation creates its own client when none provided."""
        source = ProxySourceConfig(url="http://example.com/proxies.txt")

        # Mock httpx.AsyncClient context manager
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "1.2.3.4:8080\n" + "x" * 100

        mock_client_instance = AsyncMock()
        mock_client_instance.get.return_value = mock_response
        mock_client_instance.__aenter__.return_value = mock_client_instance
        mock_client_instance.__aexit__.return_value = None

        with patch("httpx.AsyncClient", return_value=mock_client_instance):
            result = await validate_source(source)

        assert result.status_code == 200


class TestValidateSources:
    """Tests for validate_sources async function."""

    async def test_validate_sources_with_list(self):
        """Test validating a list of sources."""
        sources = [
            ProxySourceConfig(url="http://example1.com/p.txt"),
            ProxySourceConfig(url="http://example2.com/p.txt"),
        ]

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "1.2.3.4:8080\n" + "x" * 100

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None

        with patch("httpx.AsyncClient", return_value=mock_client):
            report = await validate_sources(sources=sources)

        assert report.total_sources == 2
        assert len(report.results) == 2
        assert report.healthy_sources == 2
        assert report.unhealthy_sources == 0

    async def test_validate_sources_mixed_results(self):
        """Test validating sources with mixed results."""
        sources = [
            ProxySourceConfig(url="http://good.com/p.txt"),
            ProxySourceConfig(url="http://bad.com/p.txt"),
        ]

        call_count = 0

        async def mock_get(url, **kwargs):
            nonlocal call_count
            call_count += 1
            response = MagicMock()
            if "good" in url:
                response.status_code = 200
                response.text = "1.2.3.4:8080\n" + "x" * 100
            else:
                response.status_code = 500
                response.text = ""
            return response

        mock_client = AsyncMock()
        mock_client.get = mock_get
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None

        with patch("httpx.AsyncClient", return_value=mock_client):
            report = await validate_sources(sources=sources)

        assert report.total_sources == 2
        assert report.healthy_sources == 1
        assert report.unhealthy_sources == 1


class TestValidateSourcesSync:
    """Tests for validate_sources_sync function."""

    def test_validate_sources_sync(self):
        """Test synchronous wrapper for validate_sources."""
        sources = [
            ProxySourceConfig(url="http://example.com/p.txt"),
        ]

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "1.2.3.4:8080\n" + "x" * 100

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None

        with patch("httpx.AsyncClient", return_value=mock_client):
            report = validate_sources_sync(sources=sources)

        assert report.total_sources == 1
        assert isinstance(report, SourceValidationReport)
