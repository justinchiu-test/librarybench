"""Tests for CLI functionality."""

import json
from unittest.mock import MagicMock, patch

import pytest

from k8s_resource_monitor.models import (
    ContainerStats,
    NamespaceResources,
    NodePressure,
    PodResources,
    ResourceBreach,
    ResourceQuota,
    ResourceType,
)


class TestCLIFunctionality:
    """Test CLI-related functionality."""

    def test_json_output_namespace_resources(self) -> None:
        """Test JSON serialization of namespace resources."""
        namespace = NamespaceResources(
            namespace="production",
            pods=[
                PodResources(
                    name="api-server",
                    namespace="production",
                    uid="uid-api",
                    node_name="node-1",
                    phase="Running",
                    containers=[
                        ContainerStats(
                            name="api",
                            container_id="docker://api123",
                            runtime="docker",
                            cpu_usage=500.0,
                            memory_usage=1024 * 1024 * 1024,
                        )
                    ],
                    total_cpu_usage=500.0,
                    total_memory_usage=1024 * 1024 * 1024,
                )
            ],
            quotas=[
                ResourceQuota(
                    namespace="production",
                    quota_name="compute-quota",
                    hard_limits={"cpu": "10", "memory": "20Gi"},
                    used={"cpu": "5", "memory": "10Gi"},
                )
            ],
        )

        namespace.calculate_totals()

        # Should be JSON serializable
        json_str = namespace.model_dump_json(indent=2)
        data = json.loads(json_str)

        assert data["namespace"] == "production"
        assert data["pod_count"] == 1
        assert len(data["pods"]) == 1
        assert len(data["quotas"]) == 1

    def test_json_output_breaches(self) -> None:
        """Test JSON serialization of resource breaches."""
        breaches = [
            ResourceBreach(
                pod_name="api-server",
                namespace="production",
                container_name="api",
                resource_type=ResourceType.CPU,
                current_usage=950.0,
                limit=1000.0,
                threshold_percent=90.0,
            ),
            ResourceBreach(
                pod_name="database",
                namespace="production",
                container_name="postgres",
                resource_type=ResourceType.MEMORY,
                current_usage=7.5 * 1024 * 1024 * 1024,
                limit=8 * 1024 * 1024 * 1024,
                threshold_percent=90.0,
            ),
        ]

        # Serialize list of breaches
        breach_dicts = [b.model_dump() for b in breaches]
        json_str = json.dumps(breach_dicts, indent=2, default=str)

        data = json.loads(json_str)
        assert len(data) == 2
        assert data[0]["severity"] == "critical"
        assert data[1]["severity"] == "warning"

    def test_json_output_node_pressure(self) -> None:
        """Test JSON serialization of node pressure."""
        nodes = [
            NodePressure(
                node_name="node-1",
                cpu_capacity=4000.0,
                cpu_allocatable=3800.0,
                cpu_allocated=3000.0,
                cpu_usage=2500.0,
                memory_capacity=8 * 1024 * 1024 * 1024,
                memory_allocatable=7 * 1024 * 1024 * 1024,
                memory_allocated=6 * 1024 * 1024 * 1024,
                memory_usage=5 * 1024 * 1024 * 1024,
                ephemeral_storage_capacity=100 * 1024 * 1024 * 1024,
                ephemeral_storage_allocatable=90 * 1024 * 1024 * 1024,
                ephemeral_storage_usage=50 * 1024 * 1024 * 1024,
                pod_capacity=110,
                pod_count=80,
            ),
            NodePressure(
                node_name="node-2",
                cpu_capacity=8000.0,
                cpu_allocatable=7800.0,
                cpu_allocated=1000.0,
                cpu_usage=800.0,
                memory_capacity=16 * 1024 * 1024 * 1024,
                memory_allocatable=15 * 1024 * 1024 * 1024,
                memory_allocated=2 * 1024 * 1024 * 1024,
                memory_usage=1 * 1024 * 1024 * 1024,
                ephemeral_storage_capacity=200 * 1024 * 1024 * 1024,
                ephemeral_storage_allocatable=190 * 1024 * 1024 * 1024,
                ephemeral_storage_usage=20 * 1024 * 1024 * 1024,
                pod_capacity=220,
                pod_count=20,
            ),
        ]

        for node in nodes:
            node.calculate_pressure_metrics()

        # Serialize list
        node_dicts = [n.model_dump() for n in nodes]
        json_str = json.dumps(node_dicts, indent=2, default=str)

        data = json.loads(json_str)
        assert len(data) == 2
        assert data[0]["node_name"] == "node-1"
        assert data[1]["node_name"] == "node-2"
        assert "scheduling_pressure" in data[0]
        assert "eviction_risk" in data[0]


class TestCLICommands:
    """Test CLI command scenarios."""

    @patch("k8s_resource_monitor.monitor.K8sResourceMonitor")
    def test_cli_get_namespace_resources(self, mock_monitor_class: MagicMock) -> None:
        """Test CLI command to get namespace resources."""
        mock_monitor = MagicMock()
        mock_monitor_class.return_value = mock_monitor

        # Mock return value
        mock_monitor.get_namespace_resources.return_value = NamespaceResources(
            namespace="production",
            pods=[],
            quotas=[],
        )

        # Simulate CLI command
        monitor = mock_monitor_class()
        monitor.connect()
        result = monitor.get_namespace_resources(
            "production", include_pods=True, include_quota=True
        )

        assert result.namespace == "production"
        mock_monitor.connect.assert_called_once()
        mock_monitor.get_namespace_resources.assert_called_once_with(
            "production", include_pods=True, include_quota=True
        )

    @patch("k8s_resource_monitor.monitor.K8sResourceMonitor")
    def test_cli_detect_breaches(self, mock_monitor_class: MagicMock) -> None:
        """Test CLI command to detect breaches."""
        mock_monitor = MagicMock()
        mock_monitor_class.return_value = mock_monitor

        # Mock return value
        mock_monitor.detect_limit_breaches.return_value = [
            ResourceBreach(
                pod_name="test-pod",
                namespace="default",
                container_name="app",
                resource_type=ResourceType.CPU,
                current_usage=950.0,
                limit=1000.0,
                threshold_percent=90.0,
            )
        ]

        # Simulate CLI command
        monitor = mock_monitor_class()
        monitor.connect()
        breaches = monitor.detect_limit_breaches(
            threshold_percent=90, namespace="default"
        )

        assert len(breaches) == 1
        assert breaches[0].pod_name == "test-pod"

    @patch("k8s_resource_monitor.monitor.K8sResourceMonitor")
    def test_cli_analyze_nodes(self, mock_monitor_class: MagicMock) -> None:
        """Test CLI command to analyze nodes."""
        mock_monitor = MagicMock()
        mock_monitor_class.return_value = mock_monitor

        # Mock return value
        mock_node = NodePressure(
            node_name="node-1",
            cpu_capacity=4000.0,
            cpu_allocatable=3800.0,
            cpu_allocated=2000.0,
            cpu_usage=1500.0,
            memory_capacity=8 * 1024 * 1024 * 1024,
            memory_allocatable=7 * 1024 * 1024 * 1024,
            memory_allocated=4 * 1024 * 1024 * 1024,
            memory_usage=3 * 1024 * 1024 * 1024,
            ephemeral_storage_capacity=100 * 1024 * 1024 * 1024,
            ephemeral_storage_allocatable=90 * 1024 * 1024 * 1024,
            ephemeral_storage_usage=50 * 1024 * 1024 * 1024,
            pod_capacity=110,
            pod_count=50,
        )
        mock_node.calculate_pressure_metrics()

        mock_monitor.analyze_node_pressure.return_value = [mock_node]

        # Simulate CLI command
        monitor = mock_monitor_class()
        monitor.connect()
        nodes = monitor.analyze_node_pressure(
            include_scheduling_hints=True, predict_evictions=True
        )

        assert len(nodes) == 1
        assert nodes[0].node_name == "node-1"
