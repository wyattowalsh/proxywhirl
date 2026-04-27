"""Unit tests for clustering module."""

from datetime import datetime, timedelta

from proxywhirl.clustering import (
    ClusterConfig,
    ClusterManager,
    ClusterNode,
    ClusterRole,
    NodeStatus,
)


class TestClusterNode:
    """Tests for ClusterNode."""

    def test_node_creation(self):
        """Test node creation."""
        node = ClusterNode(hostname="localhost", port=5000)
        assert node.hostname == "localhost"
        assert node.port == 5000
        assert node.status == NodeStatus.JOINING

    def test_node_healthy_status(self):
        """Test node health check."""
        node = ClusterNode()
        assert node.is_healthy()

        node.last_heartbeat = datetime.utcnow() - timedelta(seconds=60)
        assert not node.is_healthy()

    def test_node_serialization(self):
        """Test node to_dict serialization."""
        node = ClusterNode(hostname="localhost", port=5000)
        data = node.to_dict()
        assert data["hostname"] == "localhost"
        assert data["port"] == 5000
        assert "node_id" in data


class TestClusterManager:
    """Tests for ClusterManager."""

    def test_manager_initialization(self):
        """Test cluster manager initialization."""
        config = ClusterConfig(enabled=True, cluster_name="test")
        manager = ClusterManager(config)
        assert manager.config.cluster_name == "test"
        assert manager.local_node is not None

    def test_register_node(self):
        """Test node registration."""
        config = ClusterConfig(enabled=True)
        manager = ClusterManager(config)
        node = ClusterNode(hostname="localhost")
        manager.register_node(node)
        assert node.node_id in manager.nodes

    def test_get_healthy_nodes(self):
        """Test retrieving healthy nodes."""
        config = ClusterConfig(enabled=True)
        manager = ClusterManager(config)

        healthy_node = ClusterNode(hostname="node1")
        unhealthy_node = ClusterNode(hostname="node2")
        unhealthy_node.last_heartbeat = datetime.utcnow() - timedelta(seconds=60)

        manager.register_node(healthy_node)
        manager.register_node(unhealthy_node)

        healthy = manager.get_healthy_nodes()
        assert len(healthy) == 1
        assert healthy[0].hostname == "node1"

    def test_leader_election(self):
        """Test leader election."""
        config = ClusterConfig(enabled=True)
        manager = ClusterManager(config)

        node1 = ClusterNode(node_id="node1", hostname="localhost")
        node2 = ClusterNode(node_id="node2", hostname="localhost")
        manager.register_node(node1)
        manager.register_node(node2)

        leader = manager.elect_leader()
        assert leader is not None
        assert leader.role == ClusterRole.LEADER

    def test_get_cluster_status(self):
        """Test cluster status."""
        config = ClusterConfig(enabled=True, cluster_name="test")
        manager = ClusterManager(config)

        node = ClusterNode(hostname="localhost")
        manager.register_node(node)

        status = manager.get_cluster_status()
        assert status["cluster_name"] == "test"
        assert status["total_nodes"] == 1

    def test_heartbeat_processing(self):
        """Test heartbeat processing."""
        config = ClusterConfig(enabled=True)
        manager = ClusterManager(config)

        node = ClusterNode(node_id="node1")
        manager.register_node(node)

        old_time = node.last_heartbeat
        manager.heartbeat("node1")
        assert node.last_heartbeat > old_time
