"""Multi-node clustering support for ProxyWhirl.

Enables:
- Multiple ProxyWhirl nodes working together
- Shared proxy pool across nodes
- Health sync across cluster
- Distributed session management
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class NodeStatus(str, Enum):
    """Status of a cluster node."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    OFFLINE = "offline"


class ClusterNode(BaseModel):
    """A node in the ProxyWhirl cluster."""

    model_config = ConfigDict(extra="forbid")

    node_id: UUID = Field(default_factory=uuid4)
    hostname: str = Field(description="Node hostname/IP")
    port: int = Field(default=8000, description="Node API port")
    status: NodeStatus = Field(default=NodeStatus.HEALTHY)
    last_heartbeat: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metrics: dict[str, Any] = Field(
        default_factory=dict,
        description="Node performance metrics",
    )
    version: str = Field(description="ProxyWhirl version on node")
    capacity: int = Field(default=10000, description="Max proxies this node can handle")


class ClusterConfig(BaseModel):
    """Configuration for cluster mode."""

    model_config = ConfigDict(frozen=True)

    cluster_name: str = Field(description="Name of this cluster")
    node_timeout_seconds: int = Field(default=30, description="Timeout to consider node offline")
    heartbeat_interval_seconds: int = Field(default=5, description="How often nodes heartbeat")
    enable_replication: bool = Field(
        default=True, description="Enable pool replication across nodes"
    )
    replication_factor: int = Field(
        default=2, description="Number of nodes to replicate proxies to"
    )


class ClusterStats(BaseModel):
    """Statistics about the cluster."""

    model_config = ConfigDict(frozen=True)

    total_nodes: int
    healthy_nodes: int
    degraded_nodes: int
    offline_nodes: int
    total_proxies: int
    avg_response_time_ms: float
    cluster_uptime_seconds: int

    @property
    def health_percentage(self) -> float:
        """Calculate cluster health percentage."""
        if self.total_nodes == 0:
            return 100.0
        return (self.healthy_nodes / self.total_nodes) * 100


class ClusterMessage(BaseModel):
    """Message between cluster nodes."""

    model_config = ConfigDict(extra="forbid")

    message_id: UUID = Field(default_factory=uuid4)
    source_node: UUID
    message_type: str = Field(description="Type of message (heartbeat, sync, etc)")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    payload: dict[str, Any] = Field(default_factory=dict)


class PoolReplicationEvent(BaseModel):
    """Event for pool replication across cluster."""

    model_config = ConfigDict(extra="forbid")

    event_id: UUID = Field(default_factory=uuid4)
    operation: str = Field(description="Operation: add, remove, update")
    proxy_ids: list[str] = Field(description="Affected proxy IDs")
    source_node: UUID = Field(description="Node that initiated change")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = Field(default_factory=dict)


class NodeSelector:
    """Strategy for selecting nodes in the cluster."""

    def __init__(self, nodes: list[ClusterNode]):
        """Initialize with cluster nodes.

        Args:
            nodes: List of cluster nodes
        """
        self.nodes = nodes

    def healthy_nodes(self) -> list[ClusterNode]:
        """Get all healthy nodes."""
        return [n for n in self.nodes if n.status == NodeStatus.HEALTHY]

    def select_for_replication(self, replication_factor: int) -> list[ClusterNode]:
        """Select nodes for replication.

        Uses round-robin on healthy nodes.

        Args:
            replication_factor: Number of nodes to select

        Returns:
            List of selected nodes
        """
        healthy = self.healthy_nodes()
        if not healthy:
            return []

        # Round-robin selection
        selected = []
        for i in range(min(replication_factor, len(healthy))):
            selected.append(healthy[i % len(healthy)])

        return selected

    def select_random(self) -> Optional[ClusterNode]:
        """Select a random healthy node."""
        import random

        healthy = self.healthy_nodes()
        if not healthy:
            return None
        return random.choice(healthy)

    def select_best_performing(self) -> Optional[ClusterNode]:
        """Select node with best performance."""
        healthy = self.healthy_nodes()
        if not healthy:
            return None

        # Sort by response time
        def get_response_time(node: ClusterNode) -> float:
            return float(node.metrics.get("avg_response_time_ms", float("inf")))

        return min(healthy, key=get_response_time)

    def select_least_loaded(self) -> Optional[ClusterNode]:
        """Select node with least load."""
        healthy = self.healthy_nodes()
        if not healthy:
            return None

        # Sort by active connections
        def get_load(node: ClusterNode) -> int:
            return int(node.metrics.get("active_connections", 0))

        return min(healthy, key=get_load)


class ConsistentHash:
    """Consistent hashing for proxy distribution across nodes."""

    def __init__(self, nodes: list[ClusterNode], virtual_nodes: int = 160):
        """Initialize consistent hash ring.

        Args:
            nodes: List of cluster nodes
            virtual_nodes: Virtual nodes per physical node (for distribution)
        """
        self.nodes = nodes
        self.virtual_nodes = virtual_nodes
        self._ring = {}
        self._rebuild_ring()

    def _rebuild_ring(self) -> None:
        """Rebuild the hash ring."""
        import hashlib

        self._ring = {}
        for node in self.nodes:
            for i in range(self.virtual_nodes):
                key = f"{node.node_id}:{i}"
                hash_value = int(hashlib.md5(key.encode()).hexdigest(), 16)
                self._ring[hash_value] = node

    def get_node(self, key: str) -> Optional[ClusterNode]:
        """Get node responsible for key.

        Args:
            key: Key to hash

        Returns:
            Node responsible for key
        """
        if not self._ring:
            return None

        import hashlib

        hash_value = int(hashlib.md5(key.encode()).hexdigest(), 16)

        # Find next node in ring
        for ring_hash in sorted(self._ring.keys()):
            if hash_value <= ring_hash:
                return self._ring[ring_hash]

        # Wrap around
        return self._ring[min(self._ring.keys())]

    def add_node(self, node: ClusterNode) -> None:
        """Add a node to the ring."""
        self.nodes.append(node)
        self._rebuild_ring()

    def remove_node(self, node_id: UUID) -> None:
        """Remove a node from the ring."""
        self.nodes = [n for n in self.nodes if n.node_id != node_id]
        self._rebuild_ring()
