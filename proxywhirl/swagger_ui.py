"""Swagger UI integration for ProxyWhirl API.

Provides interactive API documentation with Swagger/OpenAPI.
"""

from __future__ import annotations

from typing import Any

from loguru import logger


class SwaggerUIConfig:
    """Configuration for Swagger UI."""

    def __init__(
        self,
        title: str = "ProxyWhirl API",
        version: str = "1.0.0",
        description: str = "",
        servers: list[dict[str, str]] | None = None,
    ) -> None:
        """Initialize Swagger UI configuration.

        Args:
            title: API title
            version: API version
            description: API description
            servers: List of server configurations
        """
        self.title = title
        self.version = version
        self.description = description
        self.servers = servers or []
        logger.debug(f"SwaggerUIConfig initialized: {title} v{version}")

    def to_openapi(self) -> dict[str, Any]:
        """Convert to OpenAPI specification.

        Returns:
            OpenAPI spec dictionary
        """
        return {
            "openapi": "3.0.0",
            "info": {
                "title": self.title,
                "version": self.version,
                "description": self.description,
            },
            "servers": self.servers,
            "paths": {},
            "components": {
                "schemas": {
                    "Proxy": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "protocol": {
                                "type": "string",
                                "enum": ["http", "https", "socks4", "socks5"],
                            },
                            "host": {"type": "string"},
                            "port": {"type": "integer"},
                            "status": {"type": "string"},
                        },
                    },
                    "ProxyPool": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "name": {"type": "string"},
                            "proxy_ids": {"type": "array", "items": {"type": "string"}},
                            "strategy": {"type": "string"},
                        },
                    },
                }
            },
        }


class SwaggerUIGenerator:
    """Generates Swagger UI HTML."""

    def __init__(self, config: SwaggerUIConfig) -> None:
        """Initialize Swagger UI generator.

        Args:
            config: Swagger UI configuration
        """
        self.config = config
        logger.debug("SwaggerUIGenerator initialized")

    def generate_html(self, spec_url: str = "/api/openapi.json") -> str:
        """Generate Swagger UI HTML.

        Args:
            spec_url: URL to OpenAPI spec

        Returns:
            HTML content
        """
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.config.title}</title>
    <link rel="stylesheet" type="text/css" href="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/4.15.5/swagger-ui.min.css">
    <style>
        html {{
            box-sizing: border-box;
            overflow: -moz-scrollbars-vertical;
            overflow-y: scroll;
        }}
        body {{
            margin: 0;
            padding: 0;
        }}
    </style>
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/4.15.5/swagger-ui.min.js"></script>
    <script>
        window.onload = function() {{
            SwaggerUIBundle({{
                url: "{spec_url}",
                dom_id: '#swagger-ui',
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIBundle.SwaggerUIStandalonePreset
                ],
                layout: "BaseLayout",
                supportedSubmitMethods: []
            }});
        }};
    </script>
</body>
</html>"""

    def generate_spec_html(self) -> str:
        """Generate Swagger UI with embedded spec.

        Returns:
            HTML content
        """
        import json

        spec = self.config.to_openapi()
        spec_json = json.dumps(spec)

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.config.title}</title>
    <link rel="stylesheet" type="text/css" href="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/4.15.5/swagger-ui.min.css">
    <style>
        html {{
            box-sizing: border-box;
            overflow: -moz-scrollbars-vertical;
            overflow-y: scroll;
        }}
        body {{
            margin: 0;
            padding: 0;
        }}
    </style>
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/4.15.5/swagger-ui.min.js"></script>
    <script>
        window.onload = function() {{
            SwaggerUIBundle({{
                spec: {spec_json},
                dom_id: '#swagger-ui',
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIBundle.SwaggerUIStandalonePreset
                ],
                layout: "BaseLayout",
                supportedSubmitMethods: []
            }});
        }};
    </script>
</body>
</html>"""
