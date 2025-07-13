"""Tests for K8s resource monitor."""

from datetime import datetime
from typing import Any, Dict
from unittest.mock import MagicMock, Mock, patch

import pytest
from kubernetes.client import (
    ApiException,
    V1Container,
    V1ContainerStatus,
    V1Namespace,
    V1NamespaceList,
    V1Node,
    V1NodeCondition,
    V1NodeList,
    V1NodeStatus,
    V1ObjectMeta,
    V1Pod,
    V1PodList,
    V1PodSpec,
    V1PodStatus,
    V1ResourceQuota,
    V1ResourceQuotaList,
    V1ResourceQuotaSpec,
    V1ResourceQuotaStatus,
    V1ResourceRequirements,
)

from k8s_resource_monitor.models import (
    AggregationType,
    MetricType,
    OptimizationTarget,
    ResourceType,
)
from k8s_resource_monitor.monitor import K8sResourceMonitor


@pytest.fixture
def monitor() -> K8sResourceMonitor:
    """Create a monitor instance."""
    return K8sResourceMonitor()


@pytest.fixture
def connected_monitor(monitor: K8sResourceMonitor) -> K8sResourceMonitor:
    """Create a connected monitor instance."""
    with patch("k8s_resource_monitor.monitor.config"):
        monitor.core_v1 = MagicMock()
        monitor.apps_v1 = MagicMock()
        monitor.metrics_client = MagicMock()
        monitor.is_connected = True
    return monitor


def create_mock_pod(
    name: str = "test-pod",
    namespace: str = "default",
    cpu_request: str = "100m",
    cpu_limit: str = "500m",
    memory_request: str = "128Mi",
    memory_limit: str = "512Mi",
    phase: str = "Running",
    node_name: str = "node-1",
) -> V1Pod:
    """Create a mock pod object."""
    container = V1Container(
        name="app",
        resources=V1ResourceRequirements(
            requests={"cpu": cpu_request, "memory": memory_request},
            limits={"cpu": cpu_limit, "memory": memory_limit},
        ),
    )

    container_status = V1ContainerStatus(
        name="app",
        container_id="docker://abc123",
        restart_count=0,
        ready=True,
        started=True,
        last_state=None,
        image="nginx:latest",
        image_id="docker://sha256:abc123",
    )

    pod = V1Pod(
        metadata=V1ObjectMeta(
            name=name,
            namespace=namespace,
            uid="uid-123",
            creation_timestamp=datetime.now(),
            labels={"app": "test"},
            annotations={"version": "1.0"},
        ),
        spec=V1PodSpec(
            node_name=node_name,
            containers=[container],
        ),
        status=V1PodStatus(
            phase=phase,
            container_statuses=[container_status],
        ),
    )

    return pod


def create_mock_node(
    name: str = "node-1",
    cpu_capacity: str = "4",
    memory_capacity: str = "8Gi",
    cpu_allocatable: str = "3800m",
    memory_allocatable: str = "7Gi",
) -> V1Node:
    """Create a mock node object."""
    node = V1Node(
        metadata=V1ObjectMeta(name=name),
        status=V1NodeStatus(
            capacity={
                "cpu": cpu_capacity,
                "memory": memory_capacity,
                "ephemeral-storage": "100Gi",
                "pods": "110",
            },
            allocatable={
                "cpu": cpu_allocatable,
                "memory": memory_allocatable,
                "ephemeral-storage": "90Gi",
                "pods": "110",
            },
            conditions=[
                V1NodeCondition(
                    type="Ready",
                    status="True",
                    last_heartbeat_time=datetime.now(),
                    last_transition_time=datetime.now(),
                    message="kubelet is ready",
                    reason="KubeletReady",
                ),
                V1NodeCondition(
                    type="MemoryPressure",
                    status="False",
                    last_heartbeat_time=datetime.now(),
                    last_transition_time=datetime.now(),
                    message="kubelet has sufficient memory available",
                    reason="KubeletHasSufficientMemory",
                ),
            ],
        ),
    )

    return node


def create_mock_resource_quota(
    name: str = "compute-quota",
    namespace: str = "default",
) -> V1ResourceQuota:
    """Create a mock resource quota object."""
    quota = V1ResourceQuota(
        metadata=V1ObjectMeta(name=name, namespace=namespace),
        spec=V1ResourceQuotaSpec(
            hard={
                "cpu": "100",
                "memory": "200Gi",
                "persistentvolumeclaims": "10",
            }
        ),
        status=V1ResourceQuotaStatus(
            hard={
                "cpu": "100",
                "memory": "200Gi",
                "persistentvolumeclaims": "10",
            },
            used={
                "cpu": "80",
                "memory": "150Gi",
                "persistentvolumeclaims": "8",
            },
        ),
    )

    return quota


class TestK8sResourceMonitor:
    """Test K8sResourceMonitor class."""

    def test_initialization(self, monitor: K8sResourceMonitor) -> None:
        """Test monitor initialization."""
        assert monitor.api_client is None
        assert monitor.core_v1 is None
        assert monitor.apps_v1 is None
        assert monitor.metrics_client is None
        assert monitor.is_connected is False

    @patch("k8s_resource_monitor.monitor.config.load_kube_config")
    @patch("k8s_resource_monitor.monitor.client")
    def test_connect_with_kubeconfig(
        self, mock_client: Mock, mock_config: Mock, monitor: K8sResourceMonitor
    ) -> None:
        """Test connecting with kubeconfig."""
        mock_core_v1 = MagicMock()
        mock_core_v1.list_namespace.return_value = V1NamespaceList(items=[])

        mock_client.CoreV1Api.return_value = mock_core_v1
        mock_client.AppsV1Api.return_value = MagicMock()
        mock_client.CustomObjectsApi.return_value = MagicMock()

        monitor.connect(kubeconfig="/path/to/kubeconfig", context="test-context")

        mock_config.assert_called_once_with(
            config_file="/path/to/kubeconfig", context="test-context"
        )
        assert monitor.is_connected is True

    def test_ensure_connected_not_connected(self, monitor: K8sResourceMonitor) -> None:
        """Test ensure_connected when not connected."""
        with pytest.raises(RuntimeError, match="Not connected to Kubernetes cluster"):
            monitor._ensure_connected()

    def test_parse_cpu_value(self, monitor: K8sResourceMonitor) -> None:
        """Test CPU value parsing."""
        assert monitor._parse_cpu_value("100m") == 100
        assert monitor._parse_cpu_value("1") == 1000
        assert monitor._parse_cpu_value("1000n") == 0.001
        assert monitor._parse_cpu_value(0.5) == 500

    def test_parse_memory_value(self, monitor: K8sResourceMonitor) -> None:
        """Test memory value parsing."""
        assert monitor._parse_memory_value("1Ki") == 1024
        assert monitor._parse_memory_value("1Mi") == 1024 * 1024
        assert monitor._parse_memory_value("1Gi") == 1024 * 1024 * 1024
        assert monitor._parse_memory_value("1K") == 1000
        assert monitor._parse_memory_value("100") == 100
        assert monitor._parse_memory_value(1024) == 1024

    def test_detect_container_runtime(self, monitor: K8sResourceMonitor) -> None:
        """Test container runtime detection."""
        assert monitor._detect_container_runtime("docker://abc123") == "docker"
        assert monitor._detect_container_runtime("containerd://xyz789") == "containerd"
        assert monitor._detect_container_runtime("cri-o://def456") == "cri-o"
        assert monitor._detect_container_runtime("unknown://123") == "unknown"
        assert monitor._detect_container_runtime("") == "unknown"


class TestNamespaceResources:
    """Test namespace resource monitoring."""

    def test_get_namespace_resources(
        self, connected_monitor: K8sResourceMonitor
    ) -> None:
        """Test getting namespace resources."""
        mock_pods = [create_mock_pod()]
        mock_quotas = [create_mock_resource_quota()]

        connected_monitor.core_v1.list_namespaced_pod.return_value = V1PodList(
            items=mock_pods
        )
        connected_monitor.core_v1.list_namespaced_resource_quota.return_value = (
            V1ResourceQuotaList(items=mock_quotas)
        )
        connected_monitor.metrics_client.get_namespaced_custom_object.side_effect = (
            ApiException("Not found")
        )

        namespace_resources = connected_monitor.get_namespace_resources(
            namespace="default",
            include_pods=True,
            include_quota=True,
        )

        assert namespace_resources.namespace == "default"
        assert len(namespace_resources.pods) == 1
        assert len(namespace_resources.quotas) == 1
        assert namespace_resources.pod_count == 1

    def test_get_pods_in_namespace(self, connected_monitor: K8sResourceMonitor) -> None:
        """Test getting pods in namespace."""
        mock_pods = [
            create_mock_pod(name="pod-1"),
            create_mock_pod(name="pod-2", phase="Pending"),
            create_mock_pod(name="pod-3", phase="Failed"),  # Should be excluded
        ]

        connected_monitor.core_v1.list_namespaced_pod.return_value = V1PodList(
            items=mock_pods
        )
        connected_monitor.metrics_client.get_namespaced_custom_object.side_effect = (
            ApiException("Not found")
        )

        pods = connected_monitor._get_pods_in_namespace("default")

        assert len(pods) == 2  # Only Running and Pending pods
        assert pods[0].name == "pod-1"
        assert pods[1].name == "pod-2"

    def test_extract_pod_resources(self, connected_monitor: K8sResourceMonitor) -> None:
        """Test extracting pod resources."""
        mock_pod = create_mock_pod()
        mock_metrics = {
            "containers": [
                {
                    "name": "app",
                    "usage": {"cpu": "80m", "memory": "100Mi"},
                }
            ]
        }

        connected_monitor.metrics_client.get_namespaced_custom_object.return_value = (
            mock_metrics
        )

        pod_resources = connected_monitor._extract_pod_resources(mock_pod)

        assert pod_resources.name == "test-pod"
        assert pod_resources.namespace == "default"
        assert len(pod_resources.containers) == 1
        assert pod_resources.containers[0].cpu_request == 100
        assert pod_resources.containers[0].cpu_limit == 500
        assert pod_resources.containers[0].cpu_usage == 80
        assert pod_resources.has_resource_limits is True

    def test_extract_pod_resources_no_limits(
        self, connected_monitor: K8sResourceMonitor
    ) -> None:
        """Test extracting pod resources without limits."""
        container = V1Container(
            name="app",
            resources=V1ResourceRequirements(
                requests={"cpu": "100m", "memory": "128Mi"},
            ),
        )

        mock_pod = V1Pod(
            metadata=V1ObjectMeta(
                name="test-pod",
                namespace="default",
                uid="uid-123",
                creation_timestamp=datetime.now(),
            ),
            spec=V1PodSpec(node_name="node-1", containers=[container]),
            status=V1PodStatus(
                phase="Running",
                container_statuses=[
                    V1ContainerStatus(
                        name="app",
                        container_id="docker://abc123",
                        restart_count=0,
                        ready=True,
                        started=True,
                        image="nginx:latest",
                        image_id="docker://sha256:abc123",
                    )
                ],
            ),
        )

        connected_monitor.metrics_client.get_namespaced_custom_object.side_effect = (
            ApiException("Not found")
        )

        pod_resources = connected_monitor._extract_pod_resources(mock_pod)

        assert pod_resources.has_resource_limits is False
        assert pod_resources.containers[0].cpu_limit is None
        assert pod_resources.containers[0].memory_limit is None

    def test_get_resource_quotas(self, connected_monitor: K8sResourceMonitor) -> None:
        """Test getting resource quotas."""
        mock_quotas = [create_mock_resource_quota()]

        connected_monitor.core_v1.list_namespaced_resource_quota.return_value = (
            V1ResourceQuotaList(items=mock_quotas)
        )

        quotas = connected_monitor._get_resource_quotas("default")

        assert len(quotas) == 1
        assert quotas[0].namespace == "default"
        assert quotas[0].utilization["cpu"] == 80.0  # 80/100
        assert quotas[0].utilization["memory"] == 75.0  # 150/200


class TestLimitBreachDetection:
    """Test resource limit breach detection."""

    def test_detect_limit_breaches(self, connected_monitor: K8sResourceMonitor) -> None:
        """Test detecting limit breaches."""
        # Create pods with different usage levels
        mock_pods = [create_mock_pod(name=f"pod-{i}") for i in range(3)]

        # Mock metrics with varying usage
        def mock_metrics(
            group: str, version: str, namespace: str, plural: str, name: str
        ) -> Dict[str, Any]:
            if name == "pod-0":
                # Under threshold
                return {
                    "containers": [
                        {
                            "name": "app",
                            "usage": {"cpu": "400m", "memory": "400Mi"},  # 80% of limit
                        }
                    ]
                }
            elif name == "pod-1":
                # CPU breach
                return {
                    "containers": [
                        {
                            "name": "app",
                            "usage": {"cpu": "460m", "memory": "200Mi"},  # 92% CPU
                        }
                    ]
                }
            else:
                # Memory breach
                return {
                    "containers": [
                        {
                            "name": "app",
                            "usage": {"cpu": "200m", "memory": "490Mi"},  # 95.7% memory
                        }
                    ]
                }

        connected_monitor.core_v1.list_namespace.return_value = V1NamespaceList(
            items=[V1Namespace(metadata=V1ObjectMeta(name="default"))]
        )
        connected_monitor.core_v1.list_namespaced_pod.return_value = V1PodList(
            items=mock_pods
        )
        connected_monitor.metrics_client.get_namespaced_custom_object.side_effect = (
            mock_metrics
        )

        breaches = connected_monitor.detect_limit_breaches(threshold_percent=90)

        assert len(breaches) == 2  # pod-1 CPU and pod-2 memory

        cpu_breach = next(b for b in breaches if b.resource_type == ResourceType.CPU)
        assert cpu_breach.pod_name == "pod-1"
        assert cpu_breach.breach_percent == 92.0
        assert cpu_breach.severity == "warning"

        memory_breach = next(
            b for b in breaches if b.resource_type == ResourceType.MEMORY
        )
        assert memory_breach.pod_name == "pod-2"
        assert memory_breach.breach_percent > 95
        assert memory_breach.severity == "critical"

    def test_detect_limit_breaches_specific_namespace(
        self, connected_monitor: K8sResourceMonitor
    ) -> None:
        """Test detecting breaches in specific namespace."""
        mock_pod = create_mock_pod()

        connected_monitor.core_v1.list_namespaced_pod.return_value = V1PodList(
            items=[mock_pod]
        )
        connected_monitor.metrics_client.get_namespaced_custom_object.return_value = {
            "containers": [
                {
                    "name": "app",
                    "usage": {
                        "cpu": "480m",
                        "memory": "500Mi",
                    },  # 96% CPU, 97.6% memory
                }
            ]
        }

        breaches = connected_monitor.detect_limit_breaches(
            threshold_percent=95,
            namespace="default",
        )

        assert len(breaches) == 2  # Both CPU and memory breach
        assert all(b.threshold_percent == 95 for b in breaches)


class TestNodePressureAnalysis:
    """Test node pressure analysis."""

    def test_analyze_node_pressure(self, connected_monitor: K8sResourceMonitor) -> None:
        """Test analyzing node pressure."""
        mock_nodes = [create_mock_node()]
        mock_pods = [
            create_mock_pod(name="pod-1", cpu_request="1000m", memory_request="2Gi"),
            create_mock_pod(name="pod-2", cpu_request="500m", memory_request="1Gi"),
        ]

        connected_monitor.core_v1.list_node.return_value = V1NodeList(items=mock_nodes)
        connected_monitor.core_v1.list_pod_for_all_namespaces.return_value = V1PodList(
            items=mock_pods
        )
        connected_monitor.metrics_client.get_cluster_custom_object.return_value = {
            "usage": {"cpu": "2500m", "memory": "5Gi"}
        }

        node_pressures = connected_monitor.analyze_node_pressure()

        assert len(node_pressures) == 1

        node = node_pressures[0]
        assert node.node_name == "node-1"
        assert node.cpu_capacity == 4000  # 4 cores
        assert node.cpu_allocatable == 3800  # 3800m
        assert node.cpu_allocated == 1500  # 1000m + 500m
        assert node.cpu_usage == 2500
        assert node.pod_count == 2

        # Check pressure calculations
        assert node.scheduling_pressure > 0  # Should have some pressure
        assert node.eviction_risk > 0  # Should have eviction risk

    def test_analyze_single_node(self, connected_monitor: K8sResourceMonitor) -> None:
        """Test analyzing a single node."""
        mock_node = create_mock_node()
        mock_pods = [create_mock_pod()]

        connected_monitor.core_v1.list_pod_for_all_namespaces.return_value = V1PodList(
            items=mock_pods
        )
        connected_monitor.metrics_client.get_cluster_custom_object.side_effect = (
            ApiException("Not found")
        )

        node_pressure = connected_monitor._analyze_single_node(
            mock_node,
            include_scheduling_hints=True,
            predict_evictions=True,
        )

        assert node_pressure.node_name == "node-1"
        assert node_pressure.cpu_allocated == 100  # From mock pod
        assert node_pressure.memory_allocated == 128 * 1024 * 1024  # 128Mi
        assert node_pressure.pod_count == 1
        assert "Ready" in node_pressure.conditions
        assert "MemoryPressure" in node_pressure.conditions


class TestHPAMetrics:
    """Test HPA metric generation."""

    def test_generate_hpa_metrics(self, connected_monitor: K8sResourceMonitor) -> None:
        """Test generating HPA metrics."""
        mock_deployment = MagicMock()
        mock_deployment.status.replicas = 3
        mock_deployment.spec.selector.match_labels = {"app": "test"}

        mock_pods = [create_mock_pod(name=f"pod-{i}") for i in range(3)]

        connected_monitor.apps_v1.read_namespaced_deployment.return_value = (
            mock_deployment
        )
        connected_monitor.core_v1.list_namespaced_pod.return_value = V1PodList(
            items=mock_pods
        )

        # Mock pod metrics
        connected_monitor.metrics_client.get_namespaced_custom_object.return_value = {
            "containers": [
                {
                    "name": "app",
                    "usage": {"cpu": "300m", "memory": "300Mi"},
                }
            ]
        }

        hpa_metric = connected_monitor.generate_hpa_metrics(
            deployment="api-server",
            namespace="production",
            metric_type="resource",
            aggregation="avg",
        )

        assert hpa_metric.deployment == "api-server"
        assert hpa_metric.namespace == "production"
        assert hpa_metric.metric_type == MetricType.RESOURCE
        assert hpa_metric.aggregation == AggregationType.AVG
        assert hpa_metric.current_replicas == 3
        assert hpa_metric.value > 0

    def test_calculate_metric_value(
        self, connected_monitor: K8sResourceMonitor
    ) -> None:
        """Test metric value calculation."""
        mock_pods = [create_mock_pod(name=f"pod-{i}") for i in range(5)]

        # Mock varying CPU usage
        def mock_metrics(
            group: str, version: str, namespace: str, plural: str, name: str
        ) -> Dict[str, Any]:
            pod_num = int(name.split("-")[1])
            cpu_usage = 100 + pod_num * 50  # 100m, 150m, 200m, 250m, 300m

            return {
                "containers": [
                    {
                        "name": "app",
                        "usage": {"cpu": f"{cpu_usage}m", "memory": "100Mi"},
                    }
                ]
            }

        connected_monitor.metrics_client.get_namespaced_custom_object.side_effect = (
            mock_metrics
        )

        # Test average
        avg_value = connected_monitor._calculate_metric_value(
            mock_pods,
            MetricType.RESOURCE,
            AggregationType.AVG,
        )
        assert avg_value == 200  # (100+150+200+250+300)/5

        # Test max
        max_value = connected_monitor._calculate_metric_value(
            mock_pods,
            MetricType.RESOURCE,
            AggregationType.MAX,
        )
        assert max_value == 300

        # Test min
        min_value = connected_monitor._calculate_metric_value(
            mock_pods,
            MetricType.RESOURCE,
            AggregationType.MIN,
        )
        assert min_value == 100


class TestResourceRecommendations:
    """Test resource recommendations."""

    def test_get_resource_recommendations(
        self, connected_monitor: K8sResourceMonitor
    ) -> None:
        """Test getting resource recommendations."""
        mock_pods = [create_mock_pod()]

        connected_monitor.core_v1.list_namespaced_pod.return_value = V1PodList(
            items=mock_pods
        )
        connected_monitor.core_v1.list_namespaced_resource_quota.return_value = (
            V1ResourceQuotaList(items=[])
        )
        connected_monitor.metrics_client.get_namespaced_custom_object.side_effect = (
            ApiException("Not found")
        )

        recommendations = connected_monitor.get_resource_recommendations(
            namespace="default",
            optimization_target="balanced",
        )

        # Should have CPU and memory recommendations
        assert len(recommendations) >= 2

        cpu_recs = [r for r in recommendations if r.resource_type == ResourceType.CPU]
        memory_recs = [
            r for r in recommendations if r.resource_type == ResourceType.MEMORY
        ]

        assert len(cpu_recs) > 0
        assert len(memory_recs) > 0

        for rec in recommendations:
            assert rec.optimization_target == OptimizationTarget.BALANCED
            assert rec.reason is not None

    def test_generate_cpu_recommendation(
        self, connected_monitor: K8sResourceMonitor
    ) -> None:
        """Test CPU recommendation generation."""
        from k8s_resource_monitor.models import ContainerStats, PodResources

        pod = PodResources(
            name="test-pod",
            namespace="default",
            uid="uid-123",
            node_name="node-1",
            phase="Running",
            containers=[],
        )

        container = ContainerStats(
            name="app",
            container_id="docker://abc123",
            runtime="docker",
            cpu_usage=80.0,
            cpu_request=100.0,
            cpu_limit=500.0,
            memory_usage=100 * 1024 * 1024,
        )

        rec = connected_monitor._generate_cpu_recommendation(
            pod,
            container,
            OptimizationTarget.BALANCED,
        )

        if rec:
            assert rec.resource_type == ResourceType.CPU
            assert rec.pod_name == "test-pod"
            assert rec.container_name == "app"
            assert rec.optimization_target == OptimizationTarget.BALANCED
            assert rec.recommended_request > 0
            assert rec.recommended_limit > 0
