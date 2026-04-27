"""Request building and serialization utilities."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class RequestBuilder:
    """Builds HTTP requests with fluent API."""

    method: str = "GET"
    url: str = ""
    headers: dict[str, str] = field(default_factory=dict)
    params: dict[str, Any] = field(default_factory=dict)
    data: Any = None
    json_body: dict[str, Any] | None = None
    timeout: float = 30.0
    verify_ssl: bool = True
    allow_redirects: bool = True
    proxy: str | None = None

    def with_method(self, method: str) -> RequestBuilder:
        """Set HTTP method.

        Args:
            method: HTTP method

        Returns:
            Self for chaining
        """
        self.method = method.upper()
        return self

    def with_url(self, url: str) -> RequestBuilder:
        """Set URL.

        Args:
            url: Request URL

        Returns:
            Self for chaining
        """
        self.url = url
        return self

    def with_header(self, name: str, value: str) -> RequestBuilder:
        """Add a header.

        Args:
            name: Header name
            value: Header value

        Returns:
            Self for chaining
        """
        self.headers[name] = value
        return self

    def with_headers(self, headers: dict[str, str]) -> RequestBuilder:
        """Set multiple headers.

        Args:
            headers: Headers dict

        Returns:
            Self for chaining
        """
        self.headers.update(headers)
        return self

    def with_param(self, name: str, value: Any) -> RequestBuilder:
        """Add a query parameter.

        Args:
            name: Parameter name
            value: Parameter value

        Returns:
            Self for chaining
        """
        self.params[name] = value
        return self

    def with_params(self, params: dict[str, Any]) -> RequestBuilder:
        """Set multiple parameters.

        Args:
            params: Parameters dict

        Returns:
            Self for chaining
        """
        self.params.update(params)
        return self

    def with_data(self, data: Any) -> RequestBuilder:
        """Set request body data.

        Args:
            data: Body data

        Returns:
            Self for chaining
        """
        self.data = data
        return self

    def with_json(self, json_body: dict[str, Any]) -> RequestBuilder:
        """Set JSON body.

        Args:
            json_body: JSON body dict

        Returns:
            Self for chaining
        """
        self.json_body = json_body
        self.with_header("Content-Type", "application/json")
        return self

    def with_timeout(self, timeout: float) -> RequestBuilder:
        """Set timeout in seconds.

        Args:
            timeout: Timeout in seconds

        Returns:
            Self for chaining
        """
        self.timeout = timeout
        return self

    def with_proxy(self, proxy: str) -> RequestBuilder:
        """Set proxy.

        Args:
            proxy: Proxy URL

        Returns:
            Self for chaining
        """
        self.proxy = proxy
        return self

    def with_ssl_verification(self, verify: bool) -> RequestBuilder:
        """Set SSL verification.

        Args:
            verify: Whether to verify SSL

        Returns:
            Self for chaining
        """
        self.verify_ssl = verify
        return self

    def with_redirects(self, allow: bool) -> RequestBuilder:
        """Set redirect following.

        Args:
            allow: Whether to follow redirects

        Returns:
            Self for chaining
        """
        self.allow_redirects = allow
        return self

    def build(self) -> dict[str, Any]:
        """Build request dict.

        Returns:
            Request configuration
        """
        if not self.url:
            raise ValueError("URL is required")

        return {
            "method": self.method,
            "url": self.url,
            "headers": self.headers,
            "params": self.params,
            "data": self.data,
            "json": self.json_body,
            "timeout": self.timeout,
            "verify": self.verify_ssl,
            "allow_redirects": self.allow_redirects,
            "proxy": self.proxy,
        }

    def to_curl_command(self) -> str:
        """Convert to curl command.

        Returns:
            curl command string
        """
        cmd_parts = ["curl"]

        # Method
        if self.method != "GET":
            cmd_parts.append(f"-X {self.method}")

        # Headers
        for name, value in self.headers.items():
            cmd_parts.append(f'-H "{name}: {value}"')

        # Parameters
        if self.params:
            params_str = "&".join(f"{k}={v}" for k, v in self.params.items())
            url = f"{self.url}?{params_str}"
        else:
            url = self.url

        # Data/JSON
        if self.json_body:
            import json

            cmd_parts.append(f"-d '{json.dumps(self.json_body)}'")
        elif self.data:
            cmd_parts.append(f"-d '{self.data}'")

        # SSL verification
        if not self.verify_ssl:
            cmd_parts.append("-k")

        # Proxy
        if self.proxy:
            cmd_parts.append(f"-x {self.proxy}")

        # URL (always last)
        cmd_parts.append(f'"{url}"')

        return " ".join(cmd_parts)


class ResponseSerializer:
    """Serializes responses to various formats."""

    @staticmethod
    def to_dict(response: Any) -> dict[str, Any]:
        """Convert response to dict.

        Args:
            response: Response object

        Returns:
            Response as dict
        """
        return {
            "status_code": getattr(response, "status_code", None),
            "headers": dict(getattr(response, "headers", {})),
            "content": getattr(response, "text", None),
            "url": getattr(response, "url", None),
            "elapsed": float(getattr(response, "elapsed", 0).total_seconds()),
        }

    @staticmethod
    def to_json(response: Any) -> str:
        """Convert response to JSON.

        Args:
            response: Response object

        Returns:
            Response as JSON string
        """
        import json

        return json.dumps(ResponseSerializer.to_dict(response), indent=2)

    @staticmethod
    def to_html(response: Any) -> str:
        """Convert response to HTML.

        Args:
            response: Response object

        Returns:
            Response as HTML
        """
        content = getattr(response, "text", "")
        status_code = getattr(response, "status_code", "Unknown")

        return f"""<!DOCTYPE html>
<html>
<head><title>Response {status_code}</title></head>
<body>
<h1>HTTP {status_code}</h1>
<pre>{content}</pre>
</body>
</html>"""
