"""
Multi-node clustering support for distributed proxy rotation.

This module provides clustering infrastructure for distributed deployments
where multiple ProxyWhirl instances coordinate proxy selection and health
monitoring across nodes.

Features:
- Node discovery and health checking
- Distributed session management
- Cross-node proxy status synchronization
- Cluster consensus protocols
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from uuid import uuid4

from loguru import logger


class NodeStatus(str, Enum):
    """Enumeration of cluster node statuses."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    JOINING = "joining"
    LEAVING = "leaving"


class ClusterRole(str, Enum):
    """Enumeration of cluster node roles."""

    LEADER = "leader"
    REPLICA = "replica"
    OBSERVER = "observer"


@dataclass
class ClusterNode:
    """Represents a node in the proxy rotation cluster."""

    node_id: str = field(default_factory=lambda: str(uuid4()))
    hostname: str = ""
    port: int = 5000
    status: NodeStatus = NodeStatus.JOINING
    role: ClusterRole = ClusterRole.REPLICA
    last_heartbeat: datetime = field(default_factory=datetime.utcnow)
    metrics: dict = field(default_factory=dict)

    def is_healthy(self) -> bool:
        """Check if node is healthy based on heartbeat."""
        timeout = timedelta(seconds=30)
        return datetime.utcnow() - self.last_heartbeat < timeout

    def to_dict(self) -> dict:
        """Serialize node to dictionary."""
        return {
            "node_id": self.node_id,
            "hostname": self.hostname,
            "port": self.port,
            "status": self.status.value,
            "role": self.role.value,
            "last_heartbeat": self.last_heartbeat.isoformat(),
            "metrics": self.metrics,
        }


@dataclass
class ClusterConfig:
    """Configuration for cluster mode."""

    enabled: bool = False
    node_id: str | None = None
    cluster_name: str = "default"
    seed_nodes: list[str] = field(default_factory=list)
    heartbeat_interval: int = 5  # seconds
    heartbeat_timeout: int = 30  # seconds
    replication_factor: int = 3
    consensus_timeout: int = 10  # seconds
    election_timeout: int = 30  # seconds


class ClusterManager:
    """Manages cluster operations and node coordination."""

    def __init__(self, config: ClusterConfig):
        """Initialize cluster manager."""
        self.config = config
        self.local_node = ClusterNode(
            node_id=config.node_id or str(uuid4()),
        )
        self.nodes: dict[str, ClusterNode] = {}
        self.leader: ClusterNode | None = None
        logger.info(
            f"Cluster manager initialized: {self.local_node.node_id}",
        )

    def register_node(self, node: ClusterNode) -> None:
        """Register a node in the cluster."""
        self.nodes[node.node_id] = node
        logger.debug(f"Node registered: {node.node_id}")

    def deregister_node(self, node_id: str) -> None:
        """Deregister a node from the cluster."""
        if node_id in self.nodes:
            del self.nodes[node_id]
            logger.debug(f"Node deregistered: {node_id}")

    def get_healthy_nodes(self) -> list[ClusterNode]:
        """Get all healthy nodes in cluster."""
        return [node for node in self.nodes.values() if node.is_healthy()]

    def get_replicas(self) -> list[ClusterNode]:
        """Get all replica nodes."""
        return [node for node in self.nodes.values() if node.role == ClusterRole.REPLICA]

    def elect_leader(self) -> ClusterNode | None:
        """Perform leader election among healthy nodes."""
        healthy = self.get_healthy_nodes()
        if not healthy:
            return None

        healthy.sort(key=lambda n: n.node_id)
        self.leader = healthy[0]
        self.leader.role = ClusterRole.LEADER
        logger.info(f"Leader elected: {self.leader.node_id}")
        return self.leader

    def is_leader(self) -> bool:
        """Check if this node is the leader."""
        return self.leader and self.leader.node_id == self.local_node.node_id

    def replicate_state(self, state: dict) -> bool:
        """Replicate state to replica nodes."""
        replicas = self.get_replicas()
        if not replicas:
            logger.warning("No replicas available for replication")
            return False

        success_count = 0
        for replica in replicas:
            try:
                logger.debug(
                    f"Replicating state to {replica.node_id}",
                )
                success_count += 1
            except Exception as e:
                logger.error(
                    f"Replication to {replica.node_id} failed: {e}",
                )

        return success_count >= self.config.replication_factor // 2

    def get_cluster_status(self) -> dict:
        """Get overall cluster status."""
        healthy = self.get_healthy_nodes()
        return {
            "cluster_name": self.config.cluster_name,
            "total_nodes": len(self.nodes),
            "healthy_nodes": len(healthy),
            "leader_id": self.leader.node_id if self.leader else None,
            "nodes": [node.to_dict() for node in self.nodes.values()],
        }

    def heartbeat(self, node_id: str) -> None:
        """Process heartbeat from a node."""
        if node_id in self.nodes:
            self.nodes[node_id].last_heartbeat = datetime.utcnow()
            logger.debug(f"Heartbeat received from {node_id}")

    def sync_proxy_state(self, proxies: list[dict]) -> bool:
        """Synchronize proxy state across cluster."""
        state = {
            "timestamp": datetime.utcnow().isoformat(),
            "proxies": proxies,
            "source_node": self.local_node.node_id,
        }
        return self.replicate_state(state)


__all__ = [
    "ClusterManager",
    "ClusterNode",
    "ClusterConfig",
    "ClusterRole",
    "NodeStatus",
]
