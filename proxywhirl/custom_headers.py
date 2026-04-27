"""Custom request headers support for proxy requests.

Allows per-source and per-request custom headers.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from loguru import logger


@dataclass
class HeaderTemplate:
    """Template for custom headers with variable substitution."""

    template: str
    variables: dict[str, str] = field(default_factory=dict)

    def render(self, context: dict[str, Any]) -> str:
        """Render template with context variables.

        Args:
            context: Variables for substitution

        Returns:
            Rendered template string
        """
        result = self.template
        all_vars = {**self.variables, **context}

        for key, value in all_vars.items():
            result = result.replace(f"{{{key}}}", str(value))

        return result


class HeaderPolicy:
    """Base class for header policies."""

    def apply(self, headers: dict[str, str]) -> dict[str, str]:
        """Apply policy to headers.

        Args:
            headers: Current headers dict

        Returns:
            Modified headers
        """
        return headers


class RateLimitHeaderPolicy(HeaderPolicy):
    """Add rate limit metadata headers."""

    def __init__(self, prefix: str = "X-RateLimit", include_reset: bool = True):
        """Initialize policy.

        Args:
            prefix: Header name prefix
            include_reset: Whether to include reset time
        """
        self.prefix = prefix
        self.include_reset = include_reset

    def apply(self, headers: dict[str, str]) -> dict[str, str]:
        """Add rate limit headers."""
        import time

        headers[f"{self.prefix}-Limit"] = "1000"
        headers[f"{self.prefix}-Remaining"] = "999"

        if self.include_reset:
            reset_time = int(time.time()) + 3600
            headers[f"{self.prefix}-Reset"] = str(reset_time)

        return headers


class UserAgentPolicy(HeaderPolicy):
    """Rotate or customize User-Agent headers."""

    def __init__(self, user_agents: list[str] | None = None):
        """Initialize policy.

        Args:
            user_agents: List of User-Agent strings
        """
        self.user_agents = user_agents or [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
        ]
        self._index = 0

    def apply(self, headers: dict[str, str]) -> dict[str, str]:
        """Set User-Agent header."""
        headers["User-Agent"] = self.user_agents[self._index % len(self.user_agents)]
        self._index += 1
        return headers


class SecurityHeaderPolicy(HeaderPolicy):
    """Add security headers."""

    def apply(self, headers: dict[str, str]) -> dict[str, str]:
        """Add standard security headers."""
        headers.setdefault("X-Requested-With", "XMLHttpRequest")
        headers.setdefault("DNT", "1")
        headers.setdefault("Upgrade-Insecure-Requests", "1")
        return headers


@dataclass
class HeaderConfig:
    """Configuration for custom headers."""

    static_headers: dict[str, str] = field(default_factory=dict)
    policies: list[HeaderPolicy] = field(default_factory=list)
    templates: dict[str, HeaderTemplate] = field(default_factory=dict)
    blacklisted: set[str] = field(default_factory=set)


@dataclass
class ProxyHeaders:
    """Headers configuration for a proxy or pool."""

    headers: dict[str, str] = field(default_factory=dict)
    auth_headers: dict[str, str] = field(default_factory=dict)
    user_agent: str | None = None

    def to_dict(self) -> dict[str, str]:
        """Convert to flat headers dictionary.

        Returns:
            Merged headers dictionary
        """
        result = dict(self.headers)
        result.update(self.auth_headers)
        if self.user_agent:
            result["User-Agent"] = self.user_agent
        return result

    def merge(self, other: ProxyHeaders) -> ProxyHeaders:
        """Merge with another ProxyHeaders instance.

        Other values take precedence.

        Args:
            other: ProxyHeaders to merge

        Returns:
            New merged ProxyHeaders instance
        """
        return ProxyHeaders(
            headers={**self.headers, **other.headers},
            auth_headers={**self.auth_headers, **other.auth_headers},
            user_agent=other.user_agent or self.user_agent,
        )


class CustomHeadersManager:
    """Manages custom headers with precedence: proxy > pool > default."""

    def __init__(self):
        """Initialize custom headers manager."""
        self._default: ProxyHeaders | None = None
        self._pool_headers: dict[str, ProxyHeaders] = {}
        self._proxy_headers: dict[str, ProxyHeaders] = {}

    def set_default_headers(self, headers: ProxyHeaders) -> None:
        """Set default headers."""
        self._default = headers

    def set_pool_headers(self, pool_id: str, headers: ProxyHeaders) -> None:
        """Set pool-specific headers."""
        self._pool_headers[pool_id] = headers

    def set_proxy_headers(self, proxy_url: str, headers: ProxyHeaders) -> None:
        """Set proxy-specific headers."""
        self._proxy_headers[proxy_url] = headers

    def get_headers(
        self,
        pool_id: str | None = None,
        proxy_url: str | None = None,
    ) -> dict[str, str]:
        """Get headers with precedence: proxy > pool > default."""
        result: dict[str, str] = {}

        if self._default:
            result.update(self._default.to_dict())

        if pool_id and pool_id in self._pool_headers:
            result.update(self._pool_headers[pool_id].to_dict())

        if proxy_url and proxy_url in self._proxy_headers:
            result.update(self._proxy_headers[proxy_url].to_dict())

        return result

    def remove_pool_headers(self, pool_id: str) -> bool:
        """Remove pool-specific headers.

        Returns:
            True if headers were removed
        """
        if pool_id in self._pool_headers:
            del self._pool_headers[pool_id]
            return True
        return False

    def remove_proxy_headers(self, proxy_url: str) -> bool:
        """Remove proxy-specific headers.

        Returns:
            True if headers were removed
        """
        if proxy_url in self._proxy_headers:
            del self._proxy_headers[proxy_url]
            return True
        return False


class HeaderManager:
    """Manages custom request headers."""

    def __init__(self, config: HeaderConfig | None = None):
        """Initialize header manager.

        Args:
            config: Header configuration
        """
        self.config = config or HeaderConfig()
        self._custom_filters: list[Callable[[dict[str, str]], dict[str, str]]] = []

    def add_static_header(self, key: str, value: str) -> None:
        """Add a static header.

        Args:
            key: Header name
            value: Header value
        """
        self.config.static_headers[key] = value
        logger.debug(f"Added static header: {key}")

    def add_policy(self, policy: HeaderPolicy) -> None:
        """Add a header policy.

        Args:
            policy: Header policy instance
        """
        self.config.policies.append(policy)
        logger.debug(f"Added header policy: {policy.__class__.__name__}")

    def add_template(self, name: str, template: HeaderTemplate) -> None:
        """Add a header template.

        Args:
            name: Template identifier
            template: Header template
        """
        self.config.templates[name] = template
        logger.debug(f"Added header template: {name}")

    def blacklist_header(self, header_name: str) -> None:
        """Blacklist a header name.

        Blacklisted headers will be removed from all requests.

        Args:
            header_name: Header to blacklist
        """
        self.config.blacklisted.add(header_name)
        logger.debug(f"Blacklisted header: {header_name}")

    def add_filter(self, filter_fn: Callable[[dict[str, str]], dict[str, str]]) -> None:
        """Add a custom header filter function.

        Args:
            filter_fn: Function that takes headers dict and returns modified dict
        """
        self._custom_filters.append(filter_fn)

    def build_headers(self, context: dict[str, Any] | None = None) -> dict[str, str]:
        """Build final headers dict.

        Args:
            context: Context variables for template rendering

        Returns:
            Final headers dictionary
        """
        context = context or {}
        headers = dict(self.config.static_headers)

        # Apply policies
        for policy in self.config.policies:
            headers = policy.apply(headers)

        # Apply templates
        for template_name, template in self.config.templates.items():
            try:
                rendered = template.render(context)
                headers[template_name] = rendered
            except Exception as e:
                logger.warning(f"Failed to render template {template_name}: {e}")

        # Apply custom filters
        for filter_fn in self._custom_filters:
            try:
                headers = filter_fn(headers)
            except Exception as e:
                logger.warning(f"Error in custom header filter: {e}")

        # Remove blacklisted headers
        for header in self.config.blacklisted:
            headers.pop(header, None)

        return headers

    def merge_headers(
        self,
        base_headers: dict[str, str],
        custom_headers: dict[str, str] | None = None,
    ) -> dict[str, str]:
        """Merge built headers with custom headers.

        Custom headers take precedence.

        Args:
            base_headers: Base headers from build_headers()
            custom_headers: Override headers

        Returns:
            Merged headers dictionary
        """
        result = dict(base_headers)

        if custom_headers:
            for key, value in custom_headers.items():
                if key not in self.config.blacklisted:
                    result[key] = value

        return result

    def get_config(self) -> HeaderConfig:
        """Get current configuration.

        Returns:
            Header configuration
        """
        return self.config

    def validate_header_name(self, name: str) -> bool:
        """Validate header name.

        Args:
            name: Header name to validate

        Returns:
            True if valid
        """
        if not name:
            return False

        # Check for valid characters (letters, numbers, hyphen)
        return all(c.isalnum() or c in "-_" for c in name)
