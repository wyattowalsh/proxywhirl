"""Helm chart configuration and generation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from loguru import logger


@dataclass
class ChartMaintainer:
    """Chart maintainer info."""

    name: str
    email: str | None = None
    url: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dict.

        Returns:
            Maintainer dict
        """
        data = {"name": self.name}
        if self.email:
            data["email"] = self.email
        if self.url:
            data["url"] = self.url
        return data


@dataclass
class ChartDependency:
    """Helm chart dependency."""

    name: str
    version: str
    repository: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to dict.

        Returns:
            Dependency dict
        """
        return {
            "name": self.name,
            "version": self.version,
            "repository": self.repository,
        }


@dataclass
class HelmChart:
    """Helm chart metadata."""

    name: str
    version: str
    app_version: str
    description: str
    chart_type: str = "application"
    home: str | None = None
    sources: list[str] = field(default_factory=list)
    maintainers: list[ChartMaintainer] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
    dependencies: list[ChartDependency] = field(default_factory=list)
    icon: str | None = None
    deprecated: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert to Chart.yaml dict.

        Returns:
            Chart dict
        """
        chart: dict[str, Any] = {
            "apiVersion": "v2",
            "name": self.name,
            "version": self.version,
            "appVersion": self.app_version,
            "description": self.description,
            "type": self.chart_type,
        }

        if self.home:
            chart["home"] = self.home
        if self.sources:
            chart["sources"] = self.sources
        if self.maintainers:
            chart["maintainers"] = [m.to_dict() for m in self.maintainers]
        if self.keywords:
            chart["keywords"] = self.keywords
        if self.icon:
            chart["icon"] = self.icon

        chart["deprecated"] = self.deprecated

        if self.dependencies:
            chart["dependencies"] = [d.to_dict() for d in self.dependencies]

        return chart


@dataclass
class HelmValue:
    """Single Helm value with description."""

    key: str
    value: Any
    description: str = ""
    type: str = "string"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dict.

        Returns:
            Value dict
        """
        return {
            "key": self.key,
            "value": self.value,
            "description": self.description,
            "type": self.type,
        }


@dataclass
class ValuesConfig:
    """Helm values configuration."""

    replica_count: int = 1
    image_repository: str = "proxywhirl"
    image_tag: str = "latest"
    image_pull_policy: str = "IfNotPresent"
    service_type: str = "ClusterIP"
    service_port: int = 8000
    ingress_enabled: bool = False
    ingress_hosts: list[str] = field(default_factory=list)
    resources_requests_cpu: str = "100m"
    resources_requests_memory: str = "128Mi"
    resources_limits_cpu: str = "500m"
    resources_limits_memory: str = "512Mi"
    autoscaling_enabled: bool = False
    autoscaling_min_replicas: int = 1
    autoscaling_max_replicas: int = 10
    autoscaling_target_cpu_percentage: int = 80
    custom_values: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to values dict.

        Returns:
            Values dict
        """
        values: dict[str, Any] = {
            "replicaCount": self.replica_count,
            "image": {
                "repository": self.image_repository,
                "tag": self.image_tag,
                "pullPolicy": self.image_pull_policy,
            },
            "service": {
                "type": self.service_type,
                "port": self.service_port,
            },
            "resources": {
                "requests": {
                    "cpu": self.resources_requests_cpu,
                    "memory": self.resources_requests_memory,
                },
                "limits": {
                    "cpu": self.resources_limits_cpu,
                    "memory": self.resources_limits_memory,
                },
            },
        }

        if self.ingress_enabled:
            values["ingress"] = {
                "enabled": True,
                "hosts": self.ingress_hosts,
            }

        if self.autoscaling_enabled:
            values["autoscaling"] = {
                "enabled": True,
                "minReplicas": self.autoscaling_min_replicas,
                "maxReplicas": self.autoscaling_max_replicas,
                "targetCPUUtilizationPercentage": self.autoscaling_target_cpu_percentage,
            }

        values.update(self.custom_values)

        return values


class HelmChartBuilder:
    """Builder for Helm charts."""

    def __init__(self, name: str, version: str, app_version: str):
        """Initialize builder.

        Args:
            name: Chart name
            version: Chart version
            app_version: App version
        """
        self.chart = HelmChart(
            name=name,
            version=version,
            app_version=app_version,
            description=f"Helm chart for {name}",
        )
        self.values = ValuesConfig()

    def with_description(self, description: str) -> HelmChartBuilder:
        """Set description.

        Args:
            description: Chart description

        Returns:
            Self for chaining
        """
        self.chart.description = description
        return self

    def with_home(self, home: str) -> HelmChartBuilder:
        """Set home URL.

        Args:
            home: Home URL

        Returns:
            Self for chaining
        """
        self.chart.home = home
        return self

    def add_source(self, source: str) -> HelmChartBuilder:
        """Add source URL.

        Args:
            source: Source URL

        Returns:
            Self for chaining
        """
        self.chart.sources.append(source)
        return self

    def add_maintainer(self, maintainer: ChartMaintainer) -> HelmChartBuilder:
        """Add maintainer.

        Args:
            maintainer: Maintainer

        Returns:
            Self for chaining
        """
        self.chart.maintainers.append(maintainer)
        return self

    def add_keyword(self, keyword: str) -> HelmChartBuilder:
        """Add keyword.

        Args:
            keyword: Keyword

        Returns:
            Self for chaining
        """
        self.chart.keywords.append(keyword)
        return self

    def add_dependency(self, dependency: ChartDependency) -> HelmChartBuilder:
        """Add dependency.

        Args:
            dependency: Dependency

        Returns:
            Self for chaining
        """
        self.chart.dependencies.append(dependency)
        return self

    def with_icon(self, icon: str) -> HelmChartBuilder:
        """Set icon URL.

        Args:
            icon: Icon URL

        Returns:
            Self for chaining
        """
        self.chart.icon = icon
        return self

    def with_values(self, values: ValuesConfig) -> HelmChartBuilder:
        """Set values config.

        Args:
            values: Values config

        Returns:
            Self for chaining
        """
        self.values = values
        return self

    def get_chart(self) -> HelmChart:
        """Get chart metadata.

        Returns:
            Chart metadata
        """
        return self.chart

    def get_values(self) -> ValuesConfig:
        """Get values config.

        Returns:
            Values config
        """
        return self.values


class ChartRenderer:
    """Renders Helm chart files."""

    def __init__(self, builder: HelmChartBuilder):
        """Initialize renderer.

        Args:
            builder: Chart builder
        """
        self.builder = builder

    def render_chart_yaml(self) -> str:
        """Render Chart.yaml content.

        Returns:
            YAML string
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return ""

        return yaml.dump(
            self.builder.get_chart().to_dict(),
            default_flow_style=False,
        )

    def render_values_yaml(self) -> str:
        """Render values.yaml content.

        Returns:
            YAML string
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed")
            return ""

        return yaml.dump(
            self.builder.get_values().to_dict(),
            default_flow_style=False,
        )

    def get_template_names(self) -> list[str]:
        """Get standard template names.

        Returns:
            Template names
        """
        return [
            "deployment.yaml",
            "service.yaml",
            "configmap.yaml",
            "ingress.yaml",
            "hpa.yaml",
            "pvc.yaml",
        ]
