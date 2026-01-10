"""Unit tests for premium_sources module."""

import pytest
from pydantic import ValidationError

from proxywhirl.premium_sources import (
    PREMIUM_PROVIDERS,
    PremiumProxyConfig,
    ProxySourceList,
    create_premium_proxy_source,
    list_premium_providers,
)


class TestPremiumProxyConfig:
    """Test PremiumProxyConfig model."""

    def test_valid_config(self) -> None:
        """Test creating valid proxy source config."""
        from pydantic import SecretStr

        config = PremiumProxyConfig(
            url="http://proxy.example.com:8080",
            username="user",
            password="pass",
            region="US-EAST",
            provider="TestProvider",
        )

        assert str(config.url) == "http://proxy.example.com:8080/"
        assert config.username == "user"
        # Password is now a SecretStr, so we need to access the secret value
        assert isinstance(config.password, SecretStr)
        assert config.password.get_secret_value() == "pass"
        assert config.region == "US-EAST"
        assert config.provider == "TestProvider"

    def test_invalid_url(self) -> None:
        """Test validation fails for invalid URL."""
        with pytest.raises(ValidationError):
            PremiumProxyConfig(url="not-a-url")

    def test_invalid_region(self) -> None:
        """Test validation fails for invalid region."""
        with pytest.raises(ValidationError, match="Invalid region"):
            PremiumProxyConfig(
                url="http://proxy.example.com:8080",
                region="INVALID-PLACE",
            )

    def test_valid_regions(self) -> None:
        """Test all valid regions."""
        valid_regions = [
            "US-EAST",
            "US-WEST",
            "EU-WEST",
            "EU-CENTRAL",
            "ASIA-PACIFIC",
            "GLOBAL",
        ]

        for region in valid_regions:
            config = PremiumProxyConfig(
                url="http://proxy.example.com:8080",
                region=region,
            )
            assert config.region == region

    def test_region_case_insensitive(self) -> None:
        """Test region validation is case-insensitive."""
        config = PremiumProxyConfig(
            url="http://proxy.example.com:8080",
            region="us-east",
        )
        assert config.region == "US-EAST"

    def test_invalid_protocol(self) -> None:
        """Test validation fails for invalid protocol."""
        with pytest.raises(ValidationError, match="Invalid protocol"):
            PremiumProxyConfig(
                url="http://proxy.example.com:8080",
                protocol="unknown",
            )

    def test_valid_protocols(self) -> None:
        """Test all valid protocols."""
        valid_protocols = ["http", "https", "socks4", "socks5"]

        for protocol in valid_protocols:
            config = PremiumProxyConfig(
                url="http://proxy.example.com:8080",
                protocol=protocol,
            )
            assert config.protocol == protocol


class TestProxySourceList:
    """Test ProxySourceList model."""

    def test_empty_list(self) -> None:
        """Test empty proxy source list."""
        source_list = ProxySourceList()
        assert len(source_list.sources) == 0

    def test_add_source(self) -> None:
        """Test adding source to list."""
        source_list = ProxySourceList()
        source_list.add_source("http://proxy.example.com:8080", username="user")

        assert len(source_list.sources) == 1
        assert str(source_list.sources[0].url) == "http://proxy.example.com:8080/"
        assert source_list.sources[0].username == "user"

    def test_get_by_region(self) -> None:
        """Test filtering sources by region."""
        source_list = ProxySourceList()
        source_list.add_source("http://proxy1.com:8080", region="US-EAST")
        source_list.add_source("http://proxy2.com:8080", region="EU-WEST")
        source_list.add_source("http://proxy3.com:8080", region="US-EAST")

        us_east = source_list.get_by_region("US-EAST")
        assert len(us_east) == 2

    def test_get_by_provider(self) -> None:
        """Test filtering sources by provider."""
        source_list = ProxySourceList()
        source_list.add_source("http://proxy1.com:8080", provider="Provider1")
        source_list.add_source("http://proxy2.com:8080", provider="Provider2")
        source_list.add_source("http://proxy3.com:8080", provider="Provider1")

        provider1 = source_list.get_by_provider("Provider1")
        assert len(provider1) == 2

    def test_get_by_protocol(self) -> None:
        """Test filtering sources by protocol."""
        source_list = ProxySourceList()
        source_list.add_source("http://proxy1.com:8080", protocol="http")
        source_list.add_source("http://proxy2.com:8080", protocol="socks5")
        source_list.add_source("http://proxy3.com:8080", protocol="http")

        http_sources = source_list.get_by_protocol("http")
        assert len(http_sources) == 2


class TestCreatePremiumProxySource:
    """Test create_premium_proxy_source function."""

    def test_brightdata_source(self) -> None:
        """Test creating Bright Data source."""
        source = create_premium_proxy_source(
            "brightdata",
            "myuser",
            "mypass",
            region="US-EAST",
        )

        assert "brd.superproxy.io" in str(source.url)
        assert source.provider == "Bright Data"
        assert source.region == "US-EAST"

    def test_oxylabs_source(self) -> None:
        """Test creating Oxylabs source."""
        source = create_premium_proxy_source(
            "oxylabs",
            "myuser",
            "mypass",
        )

        assert "pr.oxylabs.io" in str(source.url)
        assert source.provider == "Oxylabs"

    def test_unknown_provider(self) -> None:
        """Test error for unknown provider."""
        with pytest.raises(ValueError, match="Unknown provider"):
            create_premium_proxy_source(
                "unknown-provider",
                "user",
                "pass",
            )

    def test_all_providers(self) -> None:
        """Test all premium providers can be created."""
        for provider_key in PREMIUM_PROVIDERS.keys():
            source = create_premium_proxy_source(
                provider_key,
                "testuser",
                "testpass",
            )
            assert source.provider == PREMIUM_PROVIDERS[provider_key]["name"]


class TestListPremiumProviders:
    """Test list_premium_providers function."""

    def test_list_providers(self) -> None:
        """Test listing all premium providers."""
        providers = list_premium_providers()

        assert len(providers) == 8
        assert "brightdata" in providers
        assert "oxylabs" in providers
        assert "smartproxy" in providers

        for provider_key, info in providers.items():
            assert "name" in info
            assert "description" in info


class TestSecurityFeatures:
    """Test SEC-005: Password security with SecretStr."""

    def test_password_not_leaked_in_repr(self) -> None:
        """Test that password is not exposed in repr()."""
        from pydantic import SecretStr

        config = PremiumProxyConfig(
            url="http://user:mypassword@example.com:8080",
            password=SecretStr("supersecret123"),
            region="US-EAST",
        )

        repr_str = repr(config)

        # Password field value should not leak
        assert "supersecret123" not in repr_str, "Password field leaked in repr!"

        # URL password should not leak
        assert "mypassword" not in repr_str, "URL password leaked in repr!"

        # Should show masked credentials
        assert "***:***" in repr_str, "URL credentials not properly masked!"

        # Should still show SecretStr placeholder
        assert "**********" in repr_str, "SecretStr not showing masked value!"

    def test_password_accessible_for_use(self) -> None:
        """Test that password can still be accessed when needed."""
        from pydantic import SecretStr

        config = PremiumProxyConfig(
            url="http://user:pass@example.com:8080",
            password=SecretStr("mysecret"),
        )

        # Password should be accessible via get_secret_value()
        assert config.password is not None
        assert config.password.get_secret_value() == "mysecret"

        # URL credentials should be accessible via str()
        url_str = str(config.url)
        assert "user:pass" in url_str

    def test_create_premium_proxy_hides_credentials(self) -> None:
        """Test that create_premium_proxy_source hides credentials in repr."""
        source = create_premium_proxy_source(
            "brightdata", "myusername", "mypassword123", region="EU-WEST"
        )

        repr_str = repr(source)

        # Credentials should not leak
        assert "myusername:mypassword123" not in repr_str
        assert "mypassword123" not in repr_str

        # Should show masked credentials
        assert "***:***" in repr_str

    def test_logging_safety(self) -> None:
        """Test that logging repr is safe from credential leakage."""
        import logging
        from io import StringIO

        from pydantic import SecretStr

        # Create a string stream to capture log output
        log_stream = StringIO()
        handler = logging.StreamHandler(log_stream)
        handler.setLevel(logging.INFO)

        logger = logging.getLogger("test_premium_sources")
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)

        config = PremiumProxyConfig(
            url="http://admin:secret123@proxy.example.com:8080",
            password=SecretStr("topsecret"),
            region="US-WEST",
        )

        # Log the config
        logger.info(f"Proxy config: {repr(config)}")

        # Get log output
        log_output = log_stream.getvalue()

        # Verify credentials are not in logs
        assert "secret123" not in log_output, "URL password leaked in logs!"
        assert "topsecret" not in log_output, "Password field leaked in logs!"
        assert "***:***" in log_output, "URL credentials not masked in logs!"

        # Cleanup
        logger.removeHandler(handler)
