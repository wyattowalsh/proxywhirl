"""ProxyWhirl data sources with comprehensive validation.

This module extends the existing built-in sources with additional premium
providers and validation using Pydantic.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, HttpUrl, SecretStr, field_validator


class PremiumProxyConfig(BaseModel):
    """Validated proxy source configuration for premium providers."""

    url: HttpUrl = Field(..., description="Proxy URL")
    username: str | None = Field(None, description="Authentication username")
    password: SecretStr | None = Field(None, description="Authentication password")
    region: str | None = Field(None, description="Geographic region")
    provider: str | None = Field(None, description="Proxy provider name")
    protocol: str | None = Field("http", description="Protocol (http, socks4, socks5)")

    def __repr__(self) -> str:
        """Custom repr that hides credentials in URL."""
        # Extract URL components and mask credentials
        url_str = str(self.url)
        # Replace credentials in URL with asterisks
        if "@" in url_str:
            scheme_and_creds, rest = url_str.split("@", 1)
            if "://" in scheme_and_creds:
                scheme, creds = scheme_and_creds.split("://", 1)
                # Mask the credentials
                masked_url = f"{scheme}://***:***@{rest}"
            else:
                masked_url = f"***:***@{rest}"
        else:
            masked_url = url_str

        password_repr = "SecretStr('**********')" if self.password else None
        return (
            f"PremiumProxyConfig("
            f"url='{masked_url}', "
            f"username={self.username!r}, "
            f"password={password_repr}, "
            f"region={self.region!r}, "
            f"provider={self.provider!r}, "
            f"protocol={self.protocol!r})"
        )

    @field_validator("region")
    @classmethod
    def validate_region(cls, v: str | None) -> str | None:
        """Validate region is a known region code."""
        if v is None:
            return v
        valid_regions = [
            "US-EAST",
            "US-WEST",
            "EU-WEST",
            "EU-CENTRAL",
            "ASIA-PACIFIC",
            "GLOBAL",
        ]
        if v.upper() not in valid_regions:
            raise ValueError(f"Invalid region. Must be one of: {valid_regions}")
        return v.upper()

    @field_validator("protocol")
    @classmethod
    def validate_protocol(cls, v: str | None) -> str | None:
        """Validate protocol type."""
        if v is None:
            return "http"
        valid_protocols = ["http", "https", "socks4", "socks5"]
        if v.lower() not in valid_protocols:
            raise ValueError(f"Invalid protocol. Must be one of: {valid_protocols}")
        return v.lower()


class ProxySourceList(BaseModel):
    """Collection of validated proxy sources."""

    sources: list[PremiumProxyConfig] = Field(default_factory=list)

    def add_source(self, url: str, **kwargs: Any) -> None:
        """Add a validated proxy source."""
        source = PremiumProxyConfig(url=url, **kwargs)
        self.sources.append(source)

    def get_by_region(self, region: str) -> list[PremiumProxyConfig]:
        """Get proxies for a specific region."""
        return [s for s in self.sources if s.region == region.upper()]

    def get_by_provider(self, provider: str) -> list[PremiumProxyConfig]:
        """Get proxies from a specific provider."""
        return [s for s in self.sources if s.provider == provider]

    def get_by_protocol(self, protocol: str) -> list[PremiumProxyConfig]:
        """Get proxies by protocol type."""
        return [s for s in self.sources if s.protocol == protocol.lower()]


# Premium proxy provider templates
PREMIUM_PROVIDERS = {
    "brightdata": {
        "name": "Bright Data",
        "url_template": "http://{username}:{password}@brd.superproxy.io:22225",
        "description": "Premium residential and datacenter proxies",
    },
    "oxylabs": {
        "name": "Oxylabs",
        "url_template": "http://{username}:{password}@pr.oxylabs.io:7777",
        "description": "High-quality residential proxies",
    },
    "smartproxy": {
        "name": "SmartProxy",
        "url_template": "http://{username}:{password}@gate.smartproxy.com:7000",
        "description": "Affordable residential proxy network",
    },
    "geonode": {
        "name": "GeoNode",
        "url_template": "http://{username}:{password}@premium-residential.geonode.com:9000",
        "description": "Geo-targeted residential proxies",
    },
    "proxyrack": {
        "name": "ProxyRack",
        "url_template": "http://{username}:{password}@premium.residential.proxyrack.net:9000",
        "description": "Rotating residential proxies",
    },
    "soax": {
        "name": "SOAX",
        "url_template": "http://{username}:{password}@proxy.soax.com:5000",
        "description": "Mobile and residential proxies",
    },
    "iproyal": {
        "name": "IPRoyal",
        "url_template": "http://{username}:{password}@geo.iproyal.com:12321",
        "description": "Residential and mobile proxies",
    },
    "webshare": {
        "name": "Webshare",
        "url_template": "http://{username}:{password}@p.webshare.io:80",
        "description": "Affordable shared proxies",
    },
}


def create_premium_proxy_source(
    provider: str, username: str, password: str, region: str | None = None
) -> PremiumProxyConfig:
    """
    Create a validated proxy source from a premium provider.

    Args:
        provider: Provider name (e.g., 'brightdata', 'oxylabs', 'smartproxy')
        username: Provider username
        password: Provider password
        region: Optional geographic region

    Returns:
        Validated PremiumProxyConfig

    Raises:
        ValueError: If provider is unknown

    Examples:
        >>> source = create_premium_proxy_source(
        ...     'brightdata',
        ...     'myuser',
        ...     'mypass',
        ...     region='US-EAST'
        ... )
    """
    provider_lower = provider.lower()
    if provider_lower not in PREMIUM_PROVIDERS:
        raise ValueError(
            f"Unknown provider: {provider}. Valid providers: {list(PREMIUM_PROVIDERS.keys())}"
        )

    provider_info = PREMIUM_PROVIDERS[provider_lower]
    # SecretStr needs to be unwrapped when used in URL formatting
    url = provider_info["url_template"].format(username=username, password=password)

    return PremiumProxyConfig(
        url=url,
        region=region,
        provider=provider_info["name"],
        password=SecretStr(password) if password else None,
    )


def list_premium_providers() -> dict[str, dict[str, str]]:
    """
    List all available premium proxy providers.

    Returns:
        Dictionary of provider information
    """
    return {
        k: {"name": v["name"], "description": v["description"]}
        for k, v in PREMIUM_PROVIDERS.items()
    }
