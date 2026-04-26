"""Unit tests for offline proxy enrichment module."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from proxywhirl.enrichment import (
    PORT_SIGNATURES,
    OfflineEnricher,
    get_default_geoip_path,
    is_geoip_available,
)


class TestPortSignatures:
    """Tests for PORT_SIGNATURES constant."""

    def test_http_ports_defined(self):
        """Test that standard HTTP ports are defined."""
        assert PORT_SIGNATURES[80] == "http"
        assert PORT_SIGNATURES[8080] == "http-alt"
        assert PORT_SIGNATURES[8000] == "http-alt"

    def test_https_ports_defined(self):
        """Test that HTTPS ports are defined."""
        assert PORT_SIGNATURES[443] == "https"
        assert PORT_SIGNATURES[8443] == "https-alt"

    def test_socks_ports_defined(self):
        """Test that SOCKS ports are defined."""
        assert PORT_SIGNATURES[1080] == "socks"
        assert PORT_SIGNATURES[9050] == "tor"

    def test_squid_ports_defined(self):
        """Test that Squid proxy ports are defined."""
        assert PORT_SIGNATURES[3128] == "squid"
        assert PORT_SIGNATURES[3129] == "squid-alt"


class TestOfflineEnricherInit:
    """Tests for OfflineEnricher initialization."""

    def test_init_without_geoip(self):
        """Test initialization when GeoIP is not available."""
        enricher = OfflineEnricher()
        # Without GeoIP database, reader should be None
        # (unless installed on system)
        enricher.close()

    def test_init_with_nonexistent_path_only(self):
        """Test initialization with nonexistent path when no defaults exist."""
        # Mock Path.exists to return False for all paths
        with patch.object(Path, "exists", return_value=False):
            enricher = OfflineEnricher(geoip_path=Path("/nonexistent/path.mmdb"))
            assert enricher.geoip_reader is None
            enricher.close()

    def test_init_with_existing_path_but_load_fails(self):
        """Test initialization when path exists but loading fails."""
        with patch.object(Path, "exists", return_value=True):
            with patch("geoip2.database.Reader", side_effect=Exception("Load error")):
                enricher = OfflineEnricher(geoip_path=Path("/fake/path.mmdb"))
                # May still find a database in default paths if they exist
                enricher.close()


class TestOfflineEnricherClose:
    """Tests for OfflineEnricher close method."""

    def test_close_without_reader(self):
        """Test closing when no reader is open."""
        enricher = OfflineEnricher()
        enricher.geoip_reader = None
        enricher.close()  # Should not raise
        assert enricher.geoip_reader is None

    def test_close_with_reader(self):
        """Test closing when reader is open."""
        enricher = OfflineEnricher()
        mock_reader = MagicMock()
        enricher.geoip_reader = mock_reader
        enricher.close()
        mock_reader.close.assert_called_once()
        assert enricher.geoip_reader is None


class TestOfflineEnricherIpAnalysis:
    """Tests for IP analysis functionality."""

    def test_ip_analysis_public_ipv4(self):
        """Test IP analysis for public IPv4."""
        enricher = OfflineEnricher()
        result = enricher._ip_analysis("8.8.8.8")
        assert result["is_private"] is False
        assert result["is_global"] is True
        assert result["is_loopback"] is False
        assert result["is_reserved"] is False
        assert result["ip_version"] == 4
        enricher.close()

    def test_ip_analysis_private_ipv4(self):
        """Test IP analysis for private IPv4."""
        enricher = OfflineEnricher()
        result = enricher._ip_analysis("192.168.1.1")
        assert result["is_private"] is True
        assert result["is_global"] is False
        assert result["is_loopback"] is False
        assert result["ip_version"] == 4
        enricher.close()

    def test_ip_analysis_loopback(self):
        """Test IP analysis for loopback address."""
        enricher = OfflineEnricher()
        result = enricher._ip_analysis("127.0.0.1")
        assert result["is_loopback"] is True
        assert result["is_private"] is True
        assert result["ip_version"] == 4
        enricher.close()

    def test_ip_analysis_ipv6(self):
        """Test IP analysis for IPv6 address."""
        enricher = OfflineEnricher()
        result = enricher._ip_analysis("2001:4860:4860::8888")
        assert result["ip_version"] == 6
        assert result["is_global"] is True
        enricher.close()

    def test_ip_analysis_invalid_ip(self):
        """Test IP analysis with invalid IP returns empty dict."""
        enricher = OfflineEnricher()
        result = enricher._ip_analysis("not-an-ip")
        assert result == {}
        enricher.close()


class TestOfflineEnricherPortAnalysis:
    """Tests for port analysis functionality."""

    def test_port_analysis_known_port(self):
        """Test port analysis for known ports."""
        enricher = OfflineEnricher()
        assert enricher._port_analysis(80) == "http"
        assert enricher._port_analysis(443) == "https"
        assert enricher._port_analysis(1080) == "socks"
        assert enricher._port_analysis(3128) == "squid"
        enricher.close()

    def test_port_analysis_unknown_port(self):
        """Test port analysis for unknown ports returns 'other'."""
        enricher = OfflineEnricher()
        assert enricher._port_analysis(12345) == "other"
        assert enricher._port_analysis(54321) == "other"
        enricher.close()


class TestOfflineEnricherEnrich:
    """Tests for the main enrich method."""

    def test_enrich_returns_all_fields(self):
        """Test that enrich returns all expected fields."""
        enricher = OfflineEnricher()
        result = enricher.enrich("8.8.8.8", 8080)

        # Check all expected keys are present
        expected_keys = [
            "country",
            "country_code",
            "city",
            "region",
            "latitude",
            "longitude",
            "timezone",
            "continent",
            "continent_code",
            "is_private",
            "is_global",
            "is_loopback",
            "is_reserved",
            "ip_version",
            "port_type",
        ]
        for key in expected_keys:
            assert key in result

        enricher.close()

    def test_enrich_with_public_ip_and_known_port(self):
        """Test enrichment with public IP and known port."""
        enricher = OfflineEnricher()
        result = enricher.enrich("8.8.8.8", 8080)

        # IP analysis should work
        assert result["is_private"] is False
        assert result["is_global"] is True
        assert result["ip_version"] == 4

        # Port analysis should work
        assert result["port_type"] == "http-alt"

        enricher.close()

    def test_enrich_with_private_ip(self):
        """Test enrichment with private IP."""
        enricher = OfflineEnricher()
        result = enricher.enrich("10.0.0.1", 3128)

        assert result["is_private"] is True
        assert result["is_global"] is False
        assert result["port_type"] == "squid"

        enricher.close()


class TestOfflineEnricherGeoIPLookup:
    """Tests for GeoIP lookup functionality."""

    def test_geoip_lookup_without_reader(self):
        """Test GeoIP lookup returns empty dict when no reader."""
        enricher = OfflineEnricher()
        enricher.geoip_reader = None
        result = enricher._geoip_lookup("8.8.8.8")
        assert result == {}
        enricher.close()

    def test_geoip_lookup_with_mock_reader(self):
        """Test GeoIP lookup with mocked reader."""
        enricher = OfflineEnricher()

        # Create mock response
        mock_response = MagicMock()
        mock_response.country.name = "United States"
        mock_response.country.iso_code = "US"
        mock_response.city.name = "Mountain View"
        mock_response.continent.name = "North America"
        mock_response.continent.code = "NA"
        mock_response.subdivisions = MagicMock()
        mock_response.subdivisions.most_specific.name = "California"
        mock_response.location = MagicMock()
        mock_response.location.latitude = 37.386
        mock_response.location.longitude = -122.084
        mock_response.location.time_zone = "America/Los_Angeles"

        # Create mock reader
        mock_reader = MagicMock()
        mock_reader.city.return_value = mock_response
        enricher.geoip_reader = mock_reader

        result = enricher._geoip_lookup("8.8.8.8")

        assert result["country"] == "United States"
        assert result["country_code"] == "US"
        assert result["city"] == "Mountain View"
        assert result["region"] == "California"
        assert result["latitude"] == 37.386
        assert result["longitude"] == -122.084
        assert result["timezone"] == "America/Los_Angeles"
        assert result["continent"] == "North America"
        assert result["continent_code"] == "NA"

        enricher.close()

    def test_geoip_lookup_exception_returns_empty(self):
        """Test GeoIP lookup exception returns empty dict."""
        enricher = OfflineEnricher()

        mock_reader = MagicMock()
        mock_reader.city.side_effect = Exception("IP not found")
        enricher.geoip_reader = mock_reader

        result = enricher._geoip_lookup("invalid-ip")
        assert result == {}

        enricher.close()

    def test_geoip_lookup_without_subdivisions(self):
        """Test GeoIP lookup when subdivisions is empty."""
        enricher = OfflineEnricher()

        mock_response = MagicMock()
        mock_response.country.name = "Country"
        mock_response.country.iso_code = "XX"
        mock_response.city.name = "City"
        mock_response.continent.name = "Continent"
        mock_response.continent.code = "XX"
        mock_response.subdivisions = []  # Empty - falsy
        mock_response.location = None

        mock_reader = MagicMock()
        mock_reader.city.return_value = mock_response
        enricher.geoip_reader = mock_reader

        result = enricher._geoip_lookup("1.2.3.4")

        assert result["country"] == "Country"
        assert "region" not in result  # Not set when subdivisions empty

        enricher.close()


class TestOfflineEnricherBatch:
    """Tests for batch enrichment functionality."""

    def test_enrich_batch_basic(self):
        """Test basic batch enrichment."""
        enricher = OfflineEnricher()

        proxies = [
            {"ip": "8.8.8.8", "port": 8080},
            {"ip": "1.1.1.1", "port": 443},
        ]

        result = enricher.enrich_batch(proxies)

        # Should return same list
        assert result is proxies

        # Each proxy should have enrichment fields
        for proxy in result:
            assert "is_private" in proxy
            assert "port_type" in proxy

        enricher.close()

    def test_enrich_batch_with_custom_fields(self):
        """Test batch enrichment with custom field names."""
        enricher = OfflineEnricher()

        proxies = [
            {"host": "8.8.8.8", "proxy_port": 8080},
        ]

        result = enricher.enrich_batch(proxies, ip_field="host", port_field="proxy_port")

        assert result[0]["is_global"] is True
        assert result[0]["port_type"] == "http-alt"

        enricher.close()

    def test_enrich_batch_skips_missing_fields(self):
        """Test batch enrichment skips entries with missing fields."""
        enricher = OfflineEnricher()

        proxies = [
            {"ip": "8.8.8.8", "port": 8080},  # Valid
            {"ip": "", "port": 8080},  # Empty IP
            {"ip": "1.1.1.1"},  # Missing port
            {},  # Empty dict
        ]

        result = enricher.enrich_batch(proxies)

        # First one should be enriched
        assert result[0].get("is_global") is True

        # Others should not have enrichment fields
        assert result[1].get("is_global") is None
        assert result[2].get("port_type") is None
        assert result[3].get("is_private") is None

        enricher.close()

    def test_enrich_batch_empty_list(self):
        """Test batch enrichment with empty list."""
        enricher = OfflineEnricher()
        result = enricher.enrich_batch([])
        assert result == []
        enricher.close()


class TestHelperFunctions:
    """Tests for module-level helper functions."""

    def test_get_default_geoip_path(self):
        """Test get_default_geoip_path returns expected path."""
        path = get_default_geoip_path()
        assert isinstance(path, Path)
        assert "proxywhirl" in str(path)
        assert "GeoLite2-City.mmdb" in str(path)

    def test_is_geoip_available(self):
        """Test is_geoip_available function."""
        # Just test that it doesn't raise
        result = is_geoip_available()
        assert isinstance(result, bool)


class TestOfflineEnricherEdgeCases:
    """Edge case tests for OfflineEnricher."""

    def test_enrich_with_ipv6_loopback(self):
        """Test enrichment with IPv6 loopback."""
        enricher = OfflineEnricher()
        result = enricher.enrich("::1", 8080)
        assert result["is_loopback"] is True
        assert result["ip_version"] == 6
        enricher.close()

    def test_enrich_with_reserved_ip(self):
        """Test enrichment with reserved IP range."""
        enricher = OfflineEnricher()
        # 0.0.0.0 is reserved
        result = enricher.enrich("0.0.0.0", 80)
        # Note: 0.0.0.0 is considered unspecified, not strictly reserved
        assert result["ip_version"] == 4
        enricher.close()

    def test_enrich_multiple_times_same_enricher(self):
        """Test calling enrich multiple times on same enricher."""
        enricher = OfflineEnricher()

        result1 = enricher.enrich("8.8.8.8", 80)
        result2 = enricher.enrich("1.1.1.1", 443)
        result3 = enricher.enrich("192.168.1.1", 3128)

        assert result1["port_type"] == "http"
        assert result2["port_type"] == "https"
        assert result3["is_private"] is True

        enricher.close()

    def test_context_manager_pattern(self):
        """Test using enricher in a manual context-like pattern."""
        enricher = OfflineEnricher()
        try:
            result = enricher.enrich("8.8.8.8", 8080)
            assert "is_global" in result
        finally:
            enricher.close()
