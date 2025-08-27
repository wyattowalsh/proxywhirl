"""Tests for proxywhirl.models module.

Comprehensive unit tests for Proxy model, enums, field validation,
model validation, serialization, and edge cases with full coverage.
"""

from datetime import datetime, timedelta, timezone
from ipaddress import IPv4Address, IPv6Address, ip_address
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from proxywhirl.models import AnonymityLevel, CacheType, Proxy, RotationStrategy, Scheme


class TestProxyModel:
    """Comprehensive tests for Proxy model with all validation scenarios."""

    def test_basic_proxy_creation(self):
        """Test basic proxy creation with required fields."""
        proxy = Proxy(
            host="192.168.1.1", ip=ip_address("192.168.1.1"), port=8080, schemes=[Scheme.HTTP]
        )

        assert proxy.host == "192.168.1.1"
        assert str(proxy.ip) == "192.168.1.1"
        assert proxy.port == 8080
        assert proxy.schemes == [Scheme.HTTP]
        assert proxy.country_code is None
        assert proxy.country is None
        assert proxy.city is None
        assert proxy.anonymity == AnonymityLevel.UNKNOWN
        assert proxy.response_time is None
        assert proxy.source is None
        assert proxy.metadata == {}

    def test_proxy_creation_with_all_fields(self):
        """Test proxy creation with all fields populated."""
        now = datetime.now(timezone.utc)
        proxy = Proxy(
            host="proxy.example.com",
            ip=ip_address("203.0.113.1"),
            port=3128,
            schemes=[Scheme.HTTP, Scheme.HTTPS],
            country_code="US",
            country="United States",
            city="New York",
            anonymity=AnonymityLevel.ELITE,
            last_checked=now,
            response_time=0.234,
            source="test-provider",
            metadata={"checks_up": 100, "checks_down": 5},
        )

        assert proxy.host == "proxy.example.com"
        assert str(proxy.ip) == "203.0.113.1"
        assert proxy.port == 3128
        assert set(proxy.schemes) == {Scheme.HTTP, Scheme.HTTPS}
        assert proxy.country_code == "US"
        assert proxy.country == "United States"
        assert proxy.city == "New York"
        assert proxy.anonymity == AnonymityLevel.ELITE
        assert proxy.last_checked == now
        assert proxy.response_time == 0.234
        assert proxy.source == "test-provider"
        assert proxy.metadata == {"checks_up": 100, "checks_down": 5}

    def test_ip_resolution_from_host_ipv4(self):
        """Test automatic IP resolution from IPv4 host."""
        proxy = Proxy(host="8.8.8.8", port=80, schemes=[Scheme.HTTP])
        assert str(proxy.ip) == "8.8.8.8"
        assert isinstance(proxy.ip, IPv4Address)

    def test_ip_resolution_from_host_ipv6(self):
        """Test automatic IP resolution from IPv6 host."""
        proxy = Proxy(host="2001:db8::1", port=80, schemes=[Scheme.HTTP])
        assert str(proxy.ip) == "2001:db8::1"
        assert isinstance(proxy.ip, IPv6Address)

    def test_ip_resolution_with_hostname(self):
        """Test IP resolution allows non-IP hostname as fallback."""
        proxy = Proxy(
            host="example.com",  # Not an IP, should be allowed as hostname
            port=80,
            schemes=[Scheme.HTTP],
        )
        assert proxy.host == "example.com"
        assert str(proxy.ip) == "example.com"  # hostname becomes IP value

    def test_explicit_ip_overrides_host(self):
        """Test that explicit IP field overrides host-based resolution."""
        proxy = Proxy(host="example.com", ip=ip_address("1.2.3.4"), port=80, schemes=[Scheme.HTTP])
        assert str(proxy.ip) == "1.2.3.4"

    def test_schemes_normalization_case_insensitive(self):
        """Test schemes normalization from various case formats."""
        proxy = Proxy(
            host="1.2.3.4", ip=ip_address("1.2.3.4"), port=8080, schemes="HTTP,https,SOCKS4,socks5"
        )
        expected_schemes = {Scheme.HTTP, Scheme.HTTPS, Scheme.SOCKS4, Scheme.SOCKS5}
        assert set(proxy.schemes) == expected_schemes

    def test_schemes_normalization_from_string(self):
        """Test schemes normalization from comma-separated string."""
        proxy = Proxy(
            host="1.2.3.4", ip=ip_address("1.2.3.4"), port=8080, schemes="http,https,socks5"
        )
        expected_schemes = {Scheme.HTTP, Scheme.HTTPS, Scheme.SOCKS5}
        assert set(proxy.schemes) == expected_schemes

    def test_schemes_normalization_empty_list(self):
        """Test schemes normalization with empty input should raise validation error."""
        with pytest.raises(ValidationError):
            Proxy(host="1.2.3.4", ip=ip_address("1.2.3.4"), port=8080, schemes=[])

    def test_schemes_normalization_invalid_schemes(self):
        """Test schemes normalization filters out invalid schemes."""
        proxy = Proxy(
            host="1.2.3.4",
            ip=ip_address("1.2.3.4"),
            port=8080,
            schemes="http,invalid,https,unknown",
        )
        expected_schemes = {Scheme.HTTP, Scheme.HTTPS}
        assert set(proxy.schemes) == expected_schemes

    def test_anonymity_normalization_from_digits(self):
        """Test anonymity level normalization from digit strings."""
        test_cases = [
            ("0", AnonymityLevel.TRANSPARENT),
            ("1", AnonymityLevel.ANONYMOUS),
            ("2", AnonymityLevel.ELITE),
            ("3", AnonymityLevel.UNKNOWN),  # Invalid digit
        ]

        for digit, expected in test_cases:
            proxy = Proxy(
                host="1.2.3.4",
                ip=ip_address("1.2.3.4"),
                port=8080,
                schemes=[Scheme.HTTP],
                anonymity=digit,
            )
            assert proxy.anonymity == expected

    def test_anonymity_normalization_from_strings(self):
        """Test anonymity level normalization from string values."""
        test_cases = [
            ("transparent", AnonymityLevel.TRANSPARENT),
            ("TRANSPARENT", AnonymityLevel.TRANSPARENT),
            ("anonymous", AnonymityLevel.ANONYMOUS),
            ("ANONYMOUS", AnonymityLevel.ANONYMOUS),
            ("elite", AnonymityLevel.ELITE),
            ("ELITE", AnonymityLevel.ELITE),
            ("unknown", AnonymityLevel.UNKNOWN),
            ("invalid", AnonymityLevel.UNKNOWN),
        ]

        for value, expected in test_cases:
            proxy = Proxy(
                host="1.2.3.4",
                ip=ip_address("1.2.3.4"),
                port=8080,
                schemes=[Scheme.HTTP],
                anonymity=value,
            )
            assert proxy.anonymity == expected

    def test_anonymity_normalization_from_enum(self):
        """Test anonymity level normalization from enum values."""
        proxy = Proxy(
            host="1.2.3.4",
            ip=ip_address("1.2.3.4"),
            port=8080,
            schemes=[Scheme.HTTP],
            anonymity=AnonymityLevel.ELITE,
        )
        assert proxy.anonymity == AnonymityLevel.ELITE

    def test_city_empty_to_none_whitespace(self):
        """Test city field converts whitespace-only strings to None."""
        test_cases = ["", "  ", "\t", "\n", "   \t\n  "]

        for empty_city in test_cases:
            proxy = Proxy(
                host="1.2.3.4",
                ip=ip_address("1.2.3.4"),
                port=8080,
                schemes=[Scheme.HTTP],
                city=empty_city,
            )
            assert proxy.city is None

    def test_city_preserves_valid_strings(self):
        """Test city field preserves valid non-empty strings."""
        proxy = Proxy(
            host="1.2.3.4",
            ip=ip_address("1.2.3.4"),
            port=8080,
            schemes=[Scheme.HTTP],
            city="New York",
        )
        assert proxy.city == "New York"

    def test_city_strips_whitespace(self):
        """Test city field strips surrounding whitespace."""
        proxy = Proxy(
            host="1.2.3.4",
            ip=ip_address("1.2.3.4"),
            port=8080,
            schemes=[Scheme.HTTP],
            city="  New York  ",
        )
        assert proxy.city == "New York"

    def test_response_time_coercion_valid_values(self):
        """Test response_time coercion from various valid formats."""
        test_cases = [
            ("1.5", 1.5),
            (2, 2.0),
            ("0.001", 0.001),  # 0 is invalid (must be >= 0.001), removed
            ("0.5", 0.5),  # Added valid test case
            (None, None),
        ]

        for value, expected in test_cases:
            proxy = Proxy(
                host="1.2.3.4",
                ip=ip_address("1.2.3.4"),
                port=8080,
                schemes=[Scheme.HTTP],
                response_time=value,
            )
            assert proxy.response_time == expected

    def test_response_time_coercion_invalid_values(self):
        """Test response_time coercion handles invalid values."""
        test_cases = ["invalid", "abc", {}, []]

        for invalid_value in test_cases:
            proxy = Proxy(
                host="1.2.3.4",
                ip=ip_address("1.2.3.4"),
                port=8080,
                schemes=[Scheme.HTTP],
                response_time=invalid_value,
            )
            assert proxy.response_time is None

    def test_response_time_negative_validation(self):
        """Test response_time rejects negative values."""
        with pytest.raises(ValidationError):
            Proxy(
                host="1.2.3.4",
                ip=ip_address("1.2.3.4"),
                port=8080,
                schemes=[Scheme.HTTP],
                response_time=-1.0,
            )

    def test_country_code_validation_valid(self):
        """Test country_code validation accepts valid ISO codes."""
        valid_codes = ["US", "GB", "DE", "FR", "JP", "CN"]

        for code in valid_codes:
            proxy = Proxy(
                host="1.2.3.4",
                ip=ip_address("1.2.3.4"),
                port=8080,
                schemes=[Scheme.HTTP],
                country_code=code,
            )
            assert proxy.country_code == code

    def test_country_code_validation_lowercase_conversion(self):
        """Test country_code converts lowercase to uppercase."""
        proxy = Proxy(
            host="1.2.3.4",
            ip=ip_address("1.2.3.4"),
            port=8080,
            schemes=[Scheme.HTTP],
            country_code="us",
        )
        assert proxy.country_code == "US"

    def test_country_code_validation_invalid_length(self):
        """Test country_code validation rejects invalid lengths."""
        invalid_codes = ["U", "USA", "TOOLONG"]

        for code in invalid_codes:
            with pytest.raises(ValidationError):
                Proxy(
                    host="1.2.3.4",
                    ip=ip_address("1.2.3.4"),
                    port=8080,
                    schemes=[Scheme.HTTP],
                    country_code=code,
                )

    def test_country_code_validation_invalid_characters(self):
        """Test country_code validation rejects non-alphabetic characters."""
        invalid_codes = ["U1", "1S", "U-", "U "]

        for code in invalid_codes:
            with pytest.raises(ValidationError):
                Proxy(
                    host="1.2.3.4",
                    ip=ip_address("1.2.3.4"),
                    port=8080,
                    schemes=[Scheme.HTTP],
                    country_code=code,
                )

    def test_port_validation_valid_range(self):
        """Test port validation accepts valid port numbers."""
        valid_ports = [1, 80, 443, 8080, 3128, 65535]

        for port in valid_ports:
            proxy = Proxy(
                host="1.2.3.4", ip=ip_address("1.2.3.4"), port=port, schemes=[Scheme.HTTP]
            )
            assert proxy.port == port

    def test_port_validation_invalid_range(self):
        """Test port validation rejects invalid port numbers."""
        invalid_ports = [0, -1, 65536, 100000]

        for port in invalid_ports:
            with pytest.raises(ValidationError):
                Proxy(host="1.2.3.4", ip=ip_address("1.2.3.4"), port=port, schemes=[Scheme.HTTP])

    def test_last_checked_default_value(self):
        """Test last_checked gets default UTC timestamp."""
        with patch("proxywhirl.models.datetime") as mock_datetime:
            mock_now = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
            mock_datetime.now.return_value = mock_now

            proxy = Proxy(
                host="1.2.3.4", ip=ip_address("1.2.3.4"), port=8080, schemes=[Scheme.HTTP]
            )
            assert proxy.last_checked == mock_now

    def test_last_checked_serialization(self):
        """Test last_checked serialization to ISO format with Z suffix."""
        now = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        proxy = Proxy(
            host="1.2.3.4",
            ip=ip_address("1.2.3.4"),
            port=8080,
            schemes=[Scheme.HTTP],
            last_checked=now,
        )

        data = proxy.model_dump(mode="json")
        assert data["last_checked"] == "2023-01-01T12:00:00Z"

    def test_uris_property_single_scheme(self):
        """Test uris property with single scheme."""
        proxy = Proxy(
            host="proxy.example.com", ip=ip_address("1.2.3.4"), port=8080, schemes=[Scheme.HTTP]
        )

        uris = proxy.uris
        assert uris == {"http": "http://proxy.example.com:8080"}

    def test_uris_property_multiple_schemes(self):
        """Test uris property with multiple schemes."""
        proxy = Proxy(
            host="proxy.example.com",
            ip=ip_address("1.2.3.4"),
            port=8080,
            schemes=[Scheme.HTTP, Scheme.HTTPS, Scheme.SOCKS5],
        )

        uris = proxy.uris
        expected = {
            "http": "http://proxy.example.com:8080",
            "https": "https://proxy.example.com:8080",
            "socks5": "socks5://proxy.example.com:8080",
        }
        assert uris == expected

    def test_metadata_default_empty_dict(self):
        """Test metadata field defaults to empty dictionary."""
        proxy = Proxy(host="1.2.3.4", ip=ip_address("1.2.3.4"), port=8080, schemes=[Scheme.HTTP])
        assert proxy.metadata == {}

    def test_metadata_custom_values(self):
        """Test metadata field accepts custom values."""
        metadata = {
            "provider_id": "test123",
            "checks_up": 150,
            "checks_down": 10,
            "uptime": 0.95,
            "tags": ["fast", "reliable"],
        }

        proxy = Proxy(
            host="1.2.3.4",
            ip=ip_address("1.2.3.4"),
            port=8080,
            schemes=[Scheme.HTTP],
            metadata=metadata,
        )
        assert proxy.metadata == metadata

    def test_proxy_serialization_deserialization(self):
        """Test full proxy serialization and deserialization roundtrip."""
        original_proxy = Proxy(
            host="proxy.example.com",
            ip=ip_address("203.0.113.1"),
            port=3128,
            schemes=[Scheme.HTTP, Scheme.HTTPS],
            country_code="US",
            country="United States",
            city="New York",
            anonymity=AnonymityLevel.ELITE,
            response_time=0.234,
            source="test-provider",
            metadata={"checks_up": 100},
        )

        # Serialize to dict
        proxy_dict = original_proxy.model_dump()

        # Deserialize back to Proxy
        restored_proxy = Proxy(**proxy_dict)

        # Compare all fields
        assert restored_proxy.host == original_proxy.host
        assert restored_proxy.ip == original_proxy.ip
        assert restored_proxy.port == original_proxy.port
        assert restored_proxy.schemes == original_proxy.schemes
        assert restored_proxy.country_code == original_proxy.country_code
        assert restored_proxy.country == original_proxy.country
        assert restored_proxy.city == original_proxy.city
        assert restored_proxy.anonymity == original_proxy.anonymity
        assert restored_proxy.response_time == original_proxy.response_time
        assert restored_proxy.source == original_proxy.source
        assert restored_proxy.metadata == original_proxy.metadata

    def test_proxy_json_schema_extra(self):
        """Test proxy model includes JSON schema examples."""
        schema = Proxy.model_json_schema()
        assert "examples" in schema
        assert len(schema["examples"]) > 0

        example = schema["examples"][0]
        assert "host" in example
        assert "port" in example
        assert "schemes" in example

    def test_proxy_extra_fields_ignored(self):
        """Test proxy model ignores extra fields in input."""
        proxy = Proxy(
            host="1.2.3.4",
            ip=ip_address("1.2.3.4"),
            port=8080,
            schemes=[Scheme.HTTP],
            extra_field="ignored",  # This should be ignored
            unknown_field=123,  # This should also be ignored
        )

        # Extra fields should not be included
        assert not hasattr(proxy, "extra_field")
        assert not hasattr(proxy, "unknown_field")

    def test_acceptance_criteria_uris_lowercase_schemes(self):
        """Test REC-001 acceptance criteria: Proxy.uris returns lowercase scheme keys."""
        proxy = Proxy(
            host="example.com", ip=ip_address("1.2.3.4"), port=8080, schemes=[Scheme.HTTP]
        )
        uris = proxy.uris
        expected = {"http": "http://example.com:8080"}
        assert uris == expected, f"Expected lowercase scheme keys, got {uris}"

    def test_acceptance_criteria_multiple_schemes_uris(self):
        """Test REC-001 acceptance criteria: Multiple schemes all use lowercase keys."""
        proxy = Proxy(
            host="proxy.test",
            ip=ip_address("10.0.0.1"),
            port=3128,
            schemes=[Scheme.HTTP, Scheme.HTTPS, Scheme.SOCKS5],
        )
        uris = proxy.uris
        expected = {
            "http": "http://proxy.test:3128",
            "https": "https://proxy.test:3128",
            "socks5": "socks5://proxy.test:3128",
        }
        # Check all keys are lowercase
        for key in uris.keys():
            assert key.islower(), f"Scheme key '{key}' is not lowercase"
        assert uris == expected, f"Expected {expected}, got {uris}"


class TestProxyPerformanceMetrics:
    """Tests for ProxyPerformanceMetrics model - REC-001 acceptance criteria."""

    def test_success_rate_returns_fraction(self):
        """Test REC-001 acceptance criteria: success_rate returns fraction (0-1), not percentage."""
        from proxywhirl.models import ProxyPerformanceMetrics

        # Test case from acceptance criteria
        metrics = ProxyPerformanceMetrics(success_count=9, total_requests=10)
        success_rate = metrics.success_rate

        assert success_rate == 0.9, f"Expected 0.9 (fraction), got {success_rate}"
        assert (
            0.0 <= success_rate <= 1.0
        ), f"Success rate must be fraction in [0,1], got {success_rate}"

    def test_failure_rate_returns_fraction(self):
        """Test failure_rate also returns fraction (0-1)."""
        from proxywhirl.models import ProxyPerformanceMetrics

        metrics = ProxyPerformanceMetrics(success_count=7, failure_count=3, total_requests=10)
        failure_rate = metrics.failure_rate

        assert failure_rate == 0.3, f"Expected 0.3 (fraction), got {failure_rate}"
        assert (
            0.0 <= failure_rate <= 1.0
        ), f"Failure rate must be fraction in [0,1], got {failure_rate}"

    def test_reliability_score_uses_fractional_success_rate(self):
        """Test reliability_score calculation works with fractional success_rate."""
        from proxywhirl.models import ProxyPerformanceMetrics

        metrics = ProxyPerformanceMetrics(
            success_count=8, total_requests=10, avg_response_time=1.5, uptime_percentage=98.0
        )
        reliability_score = metrics.reliability_score

        # Should be a valid score using fractional success_rate
        assert (
            0.0 <= reliability_score <= 1.0
        ), f"Reliability score must be in [0,1], got {reliability_score}"

        # With 80% success rate, good response time, and high uptime, should be decent
        assert (
            reliability_score > 0.5
        ), f"Expected decent reliability score, got {reliability_score}"

    def test_zero_requests_edge_case(self):
        """Test success_rate with zero requests returns 0.0."""
        from proxywhirl.models import ProxyPerformanceMetrics

        metrics = ProxyPerformanceMetrics(success_count=0, total_requests=0)
        assert metrics.success_rate == 0.0
        assert metrics.failure_rate == 0.0


class TestAnonymityLevel:
    """Tests for AnonymityLevel enum."""

    def test_anonymity_level_values(self):
        """Test AnonymityLevel enum has correct values."""
        assert AnonymityLevel.TRANSPARENT == "transparent"
        assert AnonymityLevel.ANONYMOUS == "anonymous"
        assert AnonymityLevel.ELITE == "elite"
        assert AnonymityLevel.UNKNOWN == "unknown"

    def test_anonymity_level_iteration(self):
        """Test AnonymityLevel enum iteration."""
        values = list(AnonymityLevel)
        expected = [
            AnonymityLevel.TRANSPARENT,
            AnonymityLevel.ANONYMOUS,
            AnonymityLevel.ELITE,
            AnonymityLevel.UNKNOWN,
        ]
        assert values == expected

    def test_anonymity_level_membership(self):
        """Test AnonymityLevel enum membership."""
        assert "transparent" in AnonymityLevel
        assert "elite" in AnonymityLevel
        assert "invalid" not in AnonymityLevel


class TestScheme:
    """Tests for Scheme enum."""

    def test_scheme_values(self):
        """Test Scheme enum has correct values."""
        assert Scheme.HTTP == "http"
        assert Scheme.HTTPS == "https"
        assert Scheme.SOCKS4 == "socks4"
        assert Scheme.SOCKS5 == "socks5"

    def test_scheme_iteration(self):
        """Test Scheme enum iteration."""
        values = list(Scheme)
        expected = [Scheme.HTTP, Scheme.HTTPS, Scheme.SOCKS4, Scheme.SOCKS5]
        assert values == expected

    def test_scheme_membership(self):
        """Test Scheme enum membership."""
        assert "http" in Scheme
        assert "socks5" in Scheme
        assert "invalid" not in Scheme


class TestCacheType:
    """Tests for CacheType enum."""

    def test_cache_type_values(self):
        """Test CacheType enum has correct values."""
        assert CacheType.MEMORY == "memory"
        assert CacheType.JSON == "json"
        assert CacheType.SQLITE == "sqlite"

    def test_cache_type_iteration(self):
        """Test CacheType enum iteration."""
        values = list(CacheType)
        expected = [CacheType.MEMORY, CacheType.JSON, CacheType.SQLITE]
        assert values == expected

    def test_cache_type_membership(self):
        """Test CacheType enum membership."""
        assert "memory" in CacheType
        assert "sqlite" in CacheType
        assert "invalid" not in CacheType


class TestRotationStrategy:
    """Tests for RotationStrategy enum."""

    def test_rotation_strategy_values(self):
        """Test RotationStrategy enum has correct values."""
        assert RotationStrategy.ROUND_ROBIN == "round_robin"
        assert RotationStrategy.RANDOM == "random"
        assert RotationStrategy.WEIGHTED == "weighted"
        assert RotationStrategy.HEALTH_BASED == "health_based"
        assert RotationStrategy.LEAST_USED == "least_used"

    def test_rotation_strategy_iteration(self):
        """Test RotationStrategy enum iteration."""
        values = list(RotationStrategy)
        expected = [
            RotationStrategy.ROUND_ROBIN,
            RotationStrategy.RANDOM,
            RotationStrategy.WEIGHTED,
            RotationStrategy.HEALTH_BASED,
            RotationStrategy.LEAST_USED,
        ]
        assert values == expected

    def test_rotation_strategy_membership(self):
        """Test RotationStrategy enum membership."""
        assert "round_robin" in RotationStrategy
        assert "health_based" in RotationStrategy
        assert "invalid" not in RotationStrategy


class TestCountryCodeValidator:
    """Tests for country code validation functionality."""

    def test_country_code_annotation(self):
        """Test CountryCode type annotation behavior."""
        # This tests the AfterValidator annotation
        proxy = Proxy(
            host="1.2.3.4",
            ip=ip_address("1.2.3.4"),
            port=8080,
            schemes=[Scheme.HTTP],
            country_code="us",  # lowercase
        )
        assert proxy.country_code == "US"  # Should be uppercase


class TestProxyEdgeCases:
    """Tests for proxy model edge cases and error scenarios."""

    def test_proxy_missing_required_fields(self):
        """Test proxy creation fails with missing required fields."""
        with pytest.raises(ValidationError):
            Proxy()  # Missing all required fields

    def test_proxy_invalid_ip_address(self):
        """Test proxy creation fails with invalid IP address."""
        with pytest.raises(ValidationError):
            Proxy(
                host="example.com", ip="not..a..valid..hostname", port=8080, schemes=[Scheme.HTTP]
            )

    def test_proxy_invalid_ip_type(self):
        """Test proxy creation fails with invalid IP type."""
        with pytest.raises(ValidationError):
            Proxy(host="example.com", ip=12345, port=8080, schemes=[Scheme.HTTP])  # Invalid type

    def test_proxy_boundary_port_values(self):
        """Test proxy creation with boundary port values."""
        # Valid boundary values
        proxy1 = Proxy(host="1.2.3.4", ip=ip_address("1.2.3.4"), port=1, schemes=[Scheme.HTTP])
        assert proxy1.port == 1

        proxy2 = Proxy(host="1.2.3.4", ip=ip_address("1.2.3.4"), port=65535, schemes=[Scheme.HTTP])
        assert proxy2.port == 65535

    def test_proxy_with_ipv6_host_and_ip(self):
        """Test proxy creation with IPv6 addresses."""
        proxy = Proxy(
            host="2001:db8::1", ip=ip_address("2001:db8::1"), port=8080, schemes=[Scheme.HTTP]
        )
        assert str(proxy.ip) == "2001:db8::1"
        assert isinstance(proxy.ip, IPv6Address)

    def test_proxy_with_complex_metadata(self):
        """Test proxy with complex nested metadata."""
        complex_metadata = {
            "provider": {"name": "TestProvider", "version": "1.0", "endpoints": ["api1", "api2"]},
            "stats": {"uptime": 0.99, "latency": {"avg": 120, "p95": 200}},
            "tags": ["premium", "fast", "reliable"],
        }

        proxy = Proxy(
            host="1.2.3.4",
            ip=ip_address("1.2.3.4"),
            port=8080,
            schemes=[Scheme.HTTP],
            metadata=complex_metadata,
        )
        assert proxy.metadata == complex_metadata

    def test_proxy_datetime_timezone_handling(self):
        """Test proxy datetime field timezone handling."""
        # UTC timezone
        utc_time = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        proxy_utc = Proxy(
            host="1.2.3.4",
            ip=ip_address("1.2.3.4"),
            port=8080,
            schemes=[Scheme.HTTP],
            last_checked=utc_time,
        )
        assert proxy_utc.last_checked.tzinfo == timezone.utc

        # Different timezone
        offset_tz = timezone(timedelta(hours=5))
        offset_time = datetime(2023, 1, 1, 12, 0, 0, tzinfo=offset_tz)
        proxy_offset = Proxy(
            host="1.2.3.4",
            ip=ip_address("1.2.3.4"),
            port=8080,
            schemes=[Scheme.HTTP],
            last_checked=offset_time,
        )
        assert proxy_offset.last_checked.tzinfo == offset_tz

    def test_proxy_response_time_precision(self):
        """Test proxy response_time field precision handling."""
        # Response time is rounded to 3 decimal places (per AfterValidator)
        test_times = [
            (0.001, 0.001),
            (0.123456789, 0.123),  # Should be rounded to 3 decimal places
            (299.999, 299.999),
            # Note: 0.0 is invalid (must be >= 0.001), so not testing
        ]

        for input_time, expected_time in test_times:
            proxy = Proxy(
                host="1.2.3.4",
                ip=ip_address("1.2.3.4"),
                port=8080,
                schemes=[Scheme.HTTP],
                response_time=input_time,
            )
            assert proxy.response_time == expected_time

    def test_proxy_model_config(self):
        """Test proxy model configuration settings."""
        # Test populate_by_name
        proxy_data = {
            "host": "1.2.3.4",
            "ip": ip_address("1.2.3.4"),
            "port": 8080,
            "schemes": [Scheme.HTTP],
            "extra_field": "should_be_ignored",  # Should be ignored due to extra='ignore'
        }

        proxy = Proxy(**proxy_data)
        assert proxy.host == "1.2.3.4"
        assert not hasattr(proxy, "extra_field")

    def test_large_metadata_handling(self):
        """Test proxy with large metadata payload."""
        large_metadata = {f"key_{i}": f"value_{i}" for i in range(1000)}

        proxy = Proxy(
            host="1.2.3.4",
            ip=ip_address("1.2.3.4"),
            port=8080,
            schemes=[Scheme.HTTP],
            metadata=large_metadata,
        )
        assert len(proxy.metadata) == 1000
        assert proxy.metadata["key_0"] == "value_0"
        assert proxy.metadata["key_999"] == "value_999"

    def test_schemes_list_validation_with_mixed_types(self):
        """Test schemes validation with mixed input types."""
        proxy = Proxy(
            host="1.2.3.4",
            ip=ip_address("1.2.3.4"),
            port=8080,
            schemes=["http", "HTTPS", "socks5", "invalid", 123, None],
        )
        # Should filter out invalid entries and normalize valid ones
        expected_schemes = {Scheme.HTTP, Scheme.HTTPS, Scheme.SOCKS5}
        assert set(proxy.schemes) == expected_schemes

    def test_model_validation_with_nested_dicts(self):
        """Test model validation when input comes from nested dictionaries."""
        proxy_dict = {
            "host": "proxy.test.com",
            "port": 8080,
            "schemes": "http,https",
            "country_code": "us",
            "anonymity": "2",
            "response_time": "0.5",
            "city": "  San Francisco  ",
            "metadata": {"nested": {"value": 42, "list": [1, 2, 3]}},
        }

        proxy = Proxy(**proxy_dict)
        assert proxy.host == "proxy.test.com"
        assert str(proxy.ip) == "proxy.test.com"  # Should be resolved from host
        assert set(proxy.schemes) == {Scheme.HTTP, Scheme.HTTPS}
        assert proxy.country_code == "US"
        assert proxy.anonymity == AnonymityLevel.ELITE
        assert proxy.response_time == 0.5
        assert proxy.city == "San Francisco"
        assert proxy.metadata["nested"]["value"] == 42
