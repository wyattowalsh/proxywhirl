"""API versioning and compatibility management."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from loguru import logger


class APIVersion(str, Enum):
    """API versions."""

    V1_0 = "1.0"
    V1_1 = "1.1"
    V2_0 = "2.0"
    V2_1 = "2.1"
    V3_0 = "3.0"


@dataclass
class VersionedEndpoint:
    """Versioned API endpoint."""

    path: str
    version: APIVersion
    deprecated: bool = False
    deprecation_version: APIVersion | None = None
    replacement_endpoint: str | None = None
    description: str = ""


class VersionRouter:
    """Routes requests to appropriate API versions."""

    def __init__(self, current_version: APIVersion = APIVersion.V2_0):
        """Initialize router.

        Args:
            current_version: Current API version
        """
        self.current_version = current_version
        self._endpoints: dict[str, dict[APIVersion, VersionedEndpoint]] = {}
        self._version_compatibility: dict[APIVersion, list[APIVersion]] = {
            APIVersion.V1_0: [APIVersion.V1_0],
            APIVersion.V1_1: [APIVersion.V1_0, APIVersion.V1_1],
            APIVersion.V2_0: [APIVersion.V2_0],
            APIVersion.V2_1: [APIVersion.V2_0, APIVersion.V2_1],
            APIVersion.V3_0: [APIVersion.V3_0],
        }

    def register_endpoint(
        self,
        path: str,
        endpoint: VersionedEndpoint,
    ) -> None:
        """Register endpoint.

        Args:
            path: Endpoint path
            endpoint: Endpoint definition
        """
        if path not in self._endpoints:
            self._endpoints[path] = {}

        self._endpoints[path][endpoint.version] = endpoint
        logger.info(f"Registered endpoint {path} for version {endpoint.version}")

    def get_endpoint(self, path: str, version: APIVersion) -> VersionedEndpoint | None:
        """Get endpoint for version.

        Args:
            path: Endpoint path
            version: API version

        Returns:
            Endpoint or None
        """
        endpoints = self._endpoints.get(path, {})
        return endpoints.get(version)

    def list_versions_for_endpoint(self, path: str) -> list[APIVersion]:
        """List available versions for endpoint.

        Args:
            path: Endpoint path

        Returns:
            List of available versions
        """
        return list(self._endpoints.get(path, {}).keys())

    def is_deprecated(self, path: str, version: APIVersion) -> bool:
        """Check if endpoint is deprecated.

        Args:
            path: Endpoint path
            version: API version

        Returns:
            True if deprecated
        """
        endpoint = self.get_endpoint(path, version)
        return endpoint.deprecated if endpoint else False

    def get_replacement(self, path: str, version: APIVersion) -> str | None:
        """Get replacement endpoint for deprecated version.

        Args:
            path: Endpoint path
            version: API version

        Returns:
            Replacement endpoint or None
        """
        endpoint = self.get_endpoint(path, version)
        return endpoint.replacement_endpoint if endpoint else None


class APICompatibility:
    """Manages API compatibility across versions."""

    def __init__(self):
        """Initialize compatibility."""
        self._breaking_changes: dict[APIVersion, list[str]] = {
            APIVersion.V2_0: [
                "Removed legacy authentication",
                "Changed response structure",
            ],
            APIVersion.V3_0: [
                "Removed v1 endpoints",
                "Simplified request format",
            ],
        }

    def get_breaking_changes(self, from_version: APIVersion, to_version: APIVersion) -> list[str]:
        """Get breaking changes between versions.

        Args:
            from_version: Source version
            to_version: Target version

        Returns:
            List of breaking changes
        """
        changes = []

        # Simplified - in reality would traverse version path
        if to_version in self._breaking_changes:
            changes.extend(self._breaking_changes[to_version])

        return changes

    def is_compatible(self, client_version: APIVersion, server_version: APIVersion) -> bool:
        """Check if versions are compatible.

        Args:
            client_version: Client API version
            server_version: Server API version

        Returns:
            True if compatible
        """
        # Major versions must match (e.g., 2.x with 2.x)
        client_major = client_version.value.split(".")[0]
        server_major = server_version.value.split(".")[0]

        return client_major == server_major


class VersionedResponse:
    """Response with version information."""

    def __init__(
        self,
        data: Any,
        version: APIVersion,
        deprecated: bool = False,
        deprecation_message: str | None = None,
    ):
        """Initialize response.

        Args:
            data: Response data
            version: API version
            deprecated: Whether endpoint is deprecated
            deprecation_message: Deprecation message
        """
        self.data = data
        self.version = version
        self.deprecated = deprecated
        self.deprecation_message = deprecation_message

    def to_dict(self) -> dict[str, Any]:
        """Convert to dict.

        Returns:
            Dict representation
        """
        response = {
            "data": self.data,
            "version": self.version.value,
        }

        if self.deprecated:
            response["deprecated"] = True
            if self.deprecation_message:
                response["deprecation_message"] = self.deprecation_message

        return response


class MigrationGuide:
    """Provides migration guidance between versions."""

    def __init__(self):
        """Initialize guide."""
        self._guides: dict[tuple[APIVersion, APIVersion], str] = {
            (APIVersion.V1_1, APIVersion.V2_0): "Update authentication header format",
            (APIVersion.V2_0, APIVersion.V2_1): "Optional: update to new response format",
            (APIVersion.V2_1, APIVersion.V3_0): "Migrate to v3 endpoints",
        }

    def get_guide(self, from_version: APIVersion, to_version: APIVersion) -> str | None:
        """Get migration guide.

        Args:
            from_version: Source version
            to_version: Target version

        Returns:
            Migration guide or None
        """
        return self._guides.get((from_version, to_version))

    def list_all_guides(self) -> dict[str, str]:
        """List all migration guides.

        Returns:
            Dict of guides
        """
        result = {}
        for (from_v, to_v), guide in self._guides.items():
            key = f"{from_v.value} -> {to_v.value}"
            result[key] = guide

        return result
