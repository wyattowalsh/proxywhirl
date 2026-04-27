"""Kubernetes manifests generator."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from loguru import logger


class ResourceKind(str, Enum):
    """Kubernetes resource kinds."""

    DEPLOYMENT = "Deployment"
    SERVICE = "Service"
    CONFIGMAP = "ConfigMap"
    SECRET = "Secret"
    INGRESS = "Ingress"
    STATEFULSET = "StatefulSet"
    DAEMONSET = "DaemonSet"
    PERSISTENT_VOLUME = "PersistentVolume"
    PERSISTENT_VOLUME_CLAIM = "PersistentVolumeClaim"
    NAMESPACE = "Namespace"
    RBAC_ROLE = "Role"
    RBAC_ROLEBINDING = "RoleBinding"
    HORIZONTALPODAUTOSCALER = "HorizontalPodAutoscaler"


class ServiceType(str, Enum):
    """Kubernetes service types."""

    CLUSTER_IP = "ClusterIP"
    NODE_PORT = "NodePort"
    LOAD_BALANCER = "LoadBalancer"
    EXTERNAL_NAME = "ExternalName"


class RestartPolicy(str, Enum):
    """Pod restart policies."""

    ALWAYS = "Always"
    ON_FAILURE = "OnFailure"
    NEVER = "Never"


@dataclass
class ObjectMeta:
    """Kubernetes object metadata."""

    name: str
    namespace: str = "default"
    labels: dict[str, str] = field(default_factory=dict)
    annotations: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dict.

        Returns:
            Meta dict
        """
        meta: dict[str, Any] = {
            "name": self.name,
            "namespace": self.namespace,
        }
        if self.labels:
            meta["labels"] = self.labels
        if self.annotations:
            meta["annotations"] = self.annotations
        return meta


@dataclass
class ResourceRequirements:
    """Container resource requirements."""

    cpu_request: str = "100m"
    memory_request: str = "128Mi"
    cpu_limit: str = "500m"
    memory_limit: str = "512Mi"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dict.

        Returns:
            Requirements dict
        """
        return {
            "requests": {
                "cpu": self.cpu_request,
                "memory": self.memory_request,
            },
            "limits": {
                "cpu": self.cpu_limit,
                "memory": self.memory_limit,
            },
        }


@dataclass
class Container:
    """Kubernetes container spec."""

    name: str
    image: str
    ports: list[int] = field(default_factory=list)
    env: dict[str, str] = field(default_factory=dict)
    resources: ResourceRequirements = field(default_factory=ResourceRequirements)
    volume_mounts: list[dict[str, str]] = field(default_factory=list)
    liveness_probe: dict[str, Any] | None = None
    readiness_probe: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dict.

        Returns:
            Container dict
        """
        cont: dict[str, Any] = {
            "name": self.name,
            "image": self.image,
        }

        if self.ports:
            cont["ports"] = [{"containerPort": p} for p in self.ports]
        if self.env:
            cont["env"] = [{"name": k, "value": v} for k, v in self.env.items()]

        cont["resources"] = self.resources.to_dict()

        if self.volume_mounts:
            cont["volumeMounts"] = self.volume_mounts
        if self.liveness_probe:
            cont["livenessProbe"] = self.liveness_probe
        if self.readiness_probe:
            cont["readinessProbe"] = self.readiness_probe

        return cont


@dataclass
class KubernetesResource:
    """Base Kubernetes resource."""

    kind: ResourceKind
    api_version: str
    metadata: ObjectMeta
    spec: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dict.

        Returns:
            Resource dict
        """
        return {
            "apiVersion": self.api_version,
            "kind": self.kind.value,
            "metadata": self.metadata.to_dict(),
            "spec": self.spec,
        }


class DeploymentBuilder:
    """Builder for Deployments."""

    def __init__(self, name: str, namespace: str = "default"):
        """Initialize builder.

        Args:
            name: Deployment name
            namespace: Namespace
        """
        self.name = name
        self.namespace = namespace
        self.replicas = 1
        self.containers: list[Container] = []
        self.labels: dict[str, str] = {"app": name}
        self.selector_labels: dict[str, str] = {"app": name}
        self.restart_policy = RestartPolicy.ALWAYS

    def with_replicas(self, replicas: int) -> DeploymentBuilder:
        """Set replicas.

        Args:
            replicas: Number of replicas

        Returns:
            Self for chaining
        """
        self.replicas = replicas
        return self

    def add_container(self, container: Container) -> DeploymentBuilder:
        """Add container.

        Args:
            container: Container spec

        Returns:
            Self for chaining
        """
        self.containers.append(container)
        return self

    def with_labels(self, labels: dict[str, str]) -> DeploymentBuilder:
        """Set labels.

        Args:
            labels: Labels dict

        Returns:
            Self for chaining
        """
        self.labels.update(labels)
        return self

    def build(self) -> KubernetesResource:
        """Build deployment.

        Returns:
            Deployment resource
        """
        metadata = ObjectMeta(
            name=self.name,
            namespace=self.namespace,
            labels=self.labels,
        )

        spec = {
            "replicas": self.replicas,
            "selector": {"matchLabels": self.selector_labels},
            "template": {
                "metadata": {"labels": self.selector_labels},
                "spec": {
                    "containers": [c.to_dict() for c in self.containers],
                    "restartPolicy": self.restart_policy.value,
                },
            },
        }

        return KubernetesResource(
            kind=ResourceKind.DEPLOYMENT,
            api_version="apps/v1",
            metadata=metadata,
            spec=spec,
        )


class ServiceBuilder:
    """Builder for Services."""

    def __init__(self, name: str, namespace: str = "default"):
        """Initialize builder.

        Args:
            name: Service name
            namespace: Namespace
        """
        self.name = name
        self.namespace = namespace
        self.service_type = ServiceType.CLUSTER_IP
        self.selector: dict[str, str] = {}
        self.ports: list[dict[str, Any]] = []

    def with_type(self, service_type: ServiceType) -> ServiceBuilder:
        """Set service type.

        Args:
            service_type: Service type

        Returns:
            Self for chaining
        """
        self.service_type = service_type
        return self

    def with_selector(self, labels: dict[str, str]) -> ServiceBuilder:
        """Set selector labels.

        Args:
            labels: Selector labels

        Returns:
            Self for chaining
        """
        self.selector = labels
        return self

    def add_port(
        self, port: int, target_port: int | None = None, protocol: str = "TCP"
    ) -> ServiceBuilder:
        """Add port mapping.

        Args:
            port: Service port
            target_port: Target container port
            protocol: Protocol

        Returns:
            Self for chaining
        """
        self.ports.append(
            {
                "port": port,
                "targetPort": target_port or port,
                "protocol": protocol,
            }
        )
        return self

    def build(self) -> KubernetesResource:
        """Build service.

        Returns:
            Service resource
        """
        metadata = ObjectMeta(
            name=self.name,
            namespace=self.namespace,
        )

        spec = {
            "type": self.service_type.value,
            "selector": self.selector,
            "ports": self.ports,
        }

        return KubernetesResource(
            kind=ResourceKind.SERVICE,
            api_version="v1",
            metadata=metadata,
            spec=spec,
        )


class ConfigMapBuilder:
    """Builder for ConfigMaps."""

    def __init__(self, name: str, namespace: str = "default"):
        """Initialize builder.

        Args:
            name: ConfigMap name
            namespace: Namespace
        """
        self.name = name
        self.namespace = namespace
        self.data: dict[str, str] = {}

    def add_data(self, key: str, value: str) -> ConfigMapBuilder:
        """Add data entry.

        Args:
            key: Data key
            value: Data value

        Returns:
            Self for chaining
        """
        self.data[key] = value
        return self

    def build(self) -> KubernetesResource:
        """Build config map.

        Returns:
            ConfigMap resource
        """
        metadata = ObjectMeta(
            name=self.name,
            namespace=self.namespace,
        )

        spec = {"data": self.data}

        return KubernetesResource(
            kind=ResourceKind.CONFIGMAP,
            api_version="v1",
            metadata=metadata,
            spec=spec,
        )


class ManifestGenerator:
    """Generates Kubernetes manifests."""

    def __init__(self):
        """Initialize generator."""
        self._resources: list[KubernetesResource] = []

    def add_resource(self, resource: KubernetesResource) -> None:
        """Add resource.

        Args:
            resource: Kubernetes resource
        """
        self._resources.append(resource)
        logger.info(f"Added {resource.kind.value}: {resource.metadata.name}")

    def to_yaml(self) -> str:
        """Convert to YAML.

        Returns:
            YAML string
        """
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML not installed, returning JSON")
            return self.to_json()

        return yaml.dump_all(
            [r.to_dict() for r in self._resources],
            default_flow_style=False,
        )

    def to_json(self) -> str:
        """Convert to JSON.

        Returns:
            JSON string
        """
        import json

        return json.dumps(
            [r.to_dict() for r in self._resources],
            indent=2,
        )

    def get_stats(self) -> dict[str, int]:
        """Get generation stats.

        Returns:
            Stats dict
        """
        by_kind: dict[str, int] = {}
        for resource in self._resources:
            kind = resource.kind.value
            by_kind[kind] = by_kind.get(kind, 0) + 1

        return {
            "total_resources": len(self._resources),
            **by_kind,
        }
