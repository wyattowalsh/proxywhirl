"""Docker Compose development environment configuration."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from loguru import logger


class ServiceType(str, Enum):
    """Docker service types."""

    DATABASE = "database"
    CACHE = "cache"
    MESSAGE_QUEUE = "message_queue"
    API_SERVER = "api_server"
    TUI = "tui"
    MONITORING = "monitoring"


class BuildContext(str, Enum):
    """Build contexts."""

    CURRENT = "."
    CUSTOM = "custom"


@dataclass
class HealthCheck:
    """Health check configuration."""

    test: str
    interval: str = "10s"
    timeout: str = "5s"
    retries: int = 3
    start_period: str = "40s"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dict.

        Returns:
            Dict representation
        """
        return {
            "test": self.test.split(),
            "interval": self.interval,
            "timeout": self.timeout,
            "retries": self.retries,
            "start_period": self.start_period,
        }


@dataclass
class Port:
    """Port mapping."""

    container: int
    host: int | None = None
    protocol: str = "tcp"

    def to_string(self) -> str:
        """Convert to port string.

        Returns:
            Port string (host:container/protocol)
        """
        if self.host:
            return f"{self.host}:{self.container}/{self.protocol}"
        return f"{self.container}/{self.protocol}"


@dataclass
class VolumeMount:
    """Volume mount configuration."""

    name: str
    path: str
    read_only: bool = False

    def to_string(self) -> str:
        """Convert to volume string.

        Returns:
            Volume string
        """
        ro = ":ro" if self.read_only else ""
        return f"{self.name}:{self.path}{ro}"


@dataclass
class Service:
    """Docker Compose service definition."""

    name: str
    image: str | None = None
    build_context: str | None = None
    ports: list[Port] = field(default_factory=list)
    environment: dict[str, str] = field(default_factory=dict)
    volumes: list[VolumeMount] = field(default_factory=list)
    depends_on: list[str] = field(default_factory=list)
    healthcheck: HealthCheck | None = None
    service_type: ServiceType = ServiceType.DATABASE
    networks: list[str] = field(default_factory=list)
    command: str | None = None
    entrypoint: str | None = None
    restart_policy: str = "unless-stopped"
    cpu_limit: str | None = None
    memory_limit: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to compose service dict.

        Returns:
            Service dict
        """
        service_def: dict[str, Any] = {}

        if self.image:
            service_def["image"] = self.image
        if self.build_context:
            service_def["build"] = self.build_context

        if self.ports:
            service_def["ports"] = [p.to_string() for p in self.ports]
        if self.environment:
            service_def["environment"] = self.environment
        if self.volumes:
            service_def["volumes"] = [v.to_string() for v in self.volumes]
        if self.depends_on:
            service_def["depends_on"] = self.depends_on
        if self.healthcheck:
            service_def["healthcheck"] = self.healthcheck.to_dict()
        if self.networks:
            service_def["networks"] = self.networks

        if self.command:
            service_def["command"] = self.command
        if self.entrypoint:
            service_def["entrypoint"] = self.entrypoint

        service_def["restart"] = self.restart_policy

        if self.cpu_limit:
            service_def["deploy"] = {"resources": {"limits": {"cpus": self.cpu_limit}}}
        if self.memory_limit:
            if "deploy" not in service_def:
                service_def["deploy"] = {"resources": {"limits": {}}}
            service_def["deploy"]["resources"]["limits"]["memory"] = self.memory_limit

        return service_def


@dataclass
class Network:
    """Docker network configuration."""

    name: str
    driver: str = "bridge"
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to network dict.

        Returns:
            Network dict
        """
        return {
            "driver": self.driver,
        }


@dataclass
class Volume:
    """Docker volume configuration."""

    name: str
    driver: str = "local"
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to volume dict.

        Returns:
            Volume dict
        """
        return {
            "driver": self.driver,
        }


class DockerComposeConfig:
    """Docker Compose configuration builder."""

    def __init__(self, version: str = "3.9"):
        """Initialize config.

        Args:
            version: Compose file version
        """
        self.version = version
        self._services: dict[str, Service] = {}
        self._networks: dict[str, Network] = {}
        self._volumes: dict[str, Volume] = {}
        self._env_file = ".env.docker"

    def add_service(self, service: Service) -> None:
        """Add service.

        Args:
            service: Service to add
        """
        self._services[service.name] = service
        logger.info(f"Added service: {service.name}")

    def add_network(self, network: Network) -> None:
        """Add network.

        Args:
            network: Network to add
        """
        self._networks[network.name] = network
        logger.info(f"Added network: {network.name}")

    def add_volume(self, volume: Volume) -> None:
        """Add volume.

        Args:
            volume: Volume to add
        """
        self._volumes[volume.name] = volume
        logger.info(f"Added volume: {volume.name}")

    def get_service(self, name: str) -> Service | None:
        """Get service by name.

        Args:
            name: Service name

        Returns:
            Service or None
        """
        return self._services.get(name)

    def remove_service(self, name: str) -> bool:
        """Remove service.

        Args:
            name: Service name

        Returns:
            True if removed
        """
        if name in self._services:
            del self._services[name]
            logger.info(f"Removed service: {name}")
            return True
        return False

    def to_dict(self) -> dict[str, Any]:
        """Convert to docker-compose dict.

        Returns:
            Compose file dict
        """
        return {
            "version": self.version,
            "services": {name: service.to_dict() for name, service in self._services.items()},
            "networks": {name: network.to_dict() for name, network in self._networks.items()},
            "volumes": {name: volume.to_dict() for name, volume in self._volumes.items()},
        }

    def get_stats(self) -> dict[str, int]:
        """Get configuration stats.

        Returns:
            Stats dict
        """
        return {
            "services": len(self._services),
            "networks": len(self._networks),
            "volumes": len(self._volumes),
        }
