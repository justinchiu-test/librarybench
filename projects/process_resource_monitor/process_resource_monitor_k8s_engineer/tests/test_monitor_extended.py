"""Extended tests for monitor with edge cases and error handling."""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from kubernetes.client import (
    ApiException,
    V1Container,
    V1ContainerStatus,
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
    V1ResourceRequirements,
)

from k8s_resource_monitor.monitor import K8sResourceMonitor


class TestK8sResourceMonitorEdgeCases:
    """Test edge cases for K8sResourceMonitor."""

    @pytest.fixture
    def monitor(self) -> K8sResourceMonitor:
        """Create a monitor instance."""
        return K8sResourceMonitor()

    @pytest.fixture
    def connected_monitor(self, monitor: K8sResourceMonitor) -> K8sResourceMonitor:
        """Create a connected monitor instance."""
        with patch("k8s_resource_monitor.monitor.config"):
            monitor.core_v1 = MagicMock()
            monitor.apps_v1 = MagicMock()
            monitor.metrics_client = MagicMock()
            monitor.is_connected = True
        return monitor

    def test_parse_cpu_edge_cases(self, monitor: K8sResourceMonitor) -> None:
        """Test CPU parsing edge cases."""
        # Test empty string
        assert monitor._parse_cpu_value("") == 0.0

        # Test whitespace
        assert monitor._parse_cpu_value("  100m  ") == 100.0

        # Test very small values
        assert monitor._parse_cpu_value("1n") == 1e-06
        assert monitor._parse_cpu_value("1000n") == 0.001

        # Test decimal cores
        assert monitor._parse_cpu_value("0.5") == 500.0
        assert monitor._parse_cpu_value("2.5") == 2500.0

        # Test large values
        assert monitor._parse_cpu_value("1000") == 1000000.0  # 1000 cores

    def test_parse_memory_edge_cases(self, monitor: K8sResourceMonitor) -> None:
        """Test memory parsing edge cases."""
        # Test empty string
        assert monitor._parse_memory_value("") == 0

        # Test whitespace
        assert monitor._parse_memory_value("  1Gi  ") == 1024 * 1024 * 1024

        # Test all units
        assert monitor._parse_memory_value("1Ti") == 1024 * 1024 * 1024 * 1024
        assert monitor._parse_memory_value("1T") == 1000 * 1000 * 1000 * 1000

        # Test decimal values
        assert monitor._parse_memory_value("1.5Gi") == int(1.5 * 1024 * 1024 * 1024)

    def test_detect_runtime_edge_cases(self, monitor: K8sResourceMonitor) -> None:
        """Test container runtime detection edge cases."""
        # Test None
        assert monitor._detect_container_runtime(None) == "unknown"

        # Test partial matches
        assert monitor._detect_container_runtime("docker") == "unknown"
        assert monitor._detect_container_runtime("://abc123") == "unknown"

        # Test case sensitivity
        assert monitor._detect_container_runtime("Docker://abc123") == "unknown"
        assert monitor._detect_container_runtime("DOCKER://abc123") == "unknown"


class TestK8sResourceMonitorErrorHandling:
    """Test error handling in K8sResourceMonitor."""

    @pytest.fixture
    def connected_monitor(self) -> K8sResourceMonitor:
        """Create a connected monitor instance."""
        monitor = K8sResourceMonitor()
        with patch("k8s_resource_monitor.monitor.config"):
            monitor.core_v1 = MagicMock()
            monitor.apps_v1 = MagicMock()
            monitor.metrics_client = MagicMock()
            monitor.is_connected = True
        return monitor

    def test_connection_error_handling(self) -> None:
        """Test connection error handling."""
        monitor = K8sResourceMonitor()

        with patch(
            "k8s_resource_monitor.monitor.config.load_kube_config"
        ) as mock_config:
            mock_config.side_effect = Exception("Config not found")

            with pytest.raises(
                RuntimeError, match="Failed to connect to Kubernetes cluster"
            ):
                monitor.connect(kubeconfig="/invalid/path")

    def test_namespace_not_found(self, connected_monitor: K8sResourceMonitor) -> None:
        """Test handling when namespace doesn't exist."""
        connected_monitor.core_v1.list_namespaced_pod.side_effect = ApiException(
            status=404, reason="Not Found"
        )

        with pytest.raises(RuntimeError, match="Failed to list pods"):
            connected_monitor.get_namespace_resources("non-existent-namespace")

    def test_metrics_server_unavailable(
        self, connected_monitor: K8sResourceMonitor
    ) -> None:
        """Test handling when metrics server is unavailable."""
        connected_monitor.core_v1.list_namespaced_pod.return_value = V1PodList(
            items=[self._create_mock_pod()]
        )
        connected_monitor.metrics_client.get_namespaced_custom_object.side_effect = (
            ApiException(status=404, reason="metrics.k8s.io not found")
        )

        # Should still work without metrics
        resources = connected_monitor.get_namespace_resources("default")
        assert len(resources.pods) == 1
        assert resources.pods[0].total_cpu_usage == 0  # No metrics available

    def test_invalid_resource_values(
        self, connected_monitor: K8sResourceMonitor
    ) -> None:
        """Test handling of invalid resource values."""
        pod = V1Pod(
            metadata=V1ObjectMeta(
                name="invalid-pod",
                namespace="default",
                uid="uid-invalid",
                creation_timestamp=datetime.now(),
            ),
            spec=V1PodSpec(
                node_name="node-1",
                containers=[
                    V1Container(
                        name="app",
                        resources=V1ResourceRequirements(
                            limits={"cpu": "invalid", "memory": "not-a-number"},
                            requests={"cpu": "@@@@", "memory": "%%%%"},
                        ),
                    )
                ],
            ),
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

        connected_monitor.core_v1.list_namespaced_pod.return_value = V1PodList(
            items=[pod]
        )
        connected_monitor.metrics_client.get_namespaced_custom_object.side_effect = (
            ApiException("Not found")
        )

        # Should handle gracefully
        with pytest.raises(ValueError):
            connected_monitor.get_namespace_resources("default")

    def test_node_not_found(self, connected_monitor: K8sResourceMonitor) -> None:
        """Test handling when node doesn't exist."""
        connected_monitor.core_v1.list_node.return_value = V1NodeList(items=[])

        node_pressures = connected_monitor.analyze_node_pressure()
        assert len(node_pressures) == 0

    def test_deployment_not_found(self, connected_monitor: K8sResourceMonitor) -> None:
        """Test HPA metrics when deployment doesn't exist."""
        connected_monitor.apps_v1.read_namespaced_deployment.side_effect = ApiException(
            status=404, reason="Not Found"
        )

        with pytest.raises(RuntimeError, match="Failed to get deployment"):
            connected_monitor.generate_hpa_metrics(
                deployment="non-existent",
                namespace="default",
            )

    def _create_mock_pod(self) -> V1Pod:
        """Create a basic mock pod."""
        return V1Pod(
            metadata=V1ObjectMeta(
                name="test-pod",
                namespace="default",
                uid="uid-123",
                creation_timestamp=datetime.now(),
            ),
            spec=V1PodSpec(
                node_name="node-1",
                containers=[
                    V1Container(
                        name="app",
                        resources=V1ResourceRequirements(
                            limits={"cpu": "500m", "memory": "512Mi"},
                            requests={"cpu": "100m", "memory": "128Mi"},
                        ),
                    )
                ],
            ),
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


class TestK8sResourceMonitorPerformance:
    """Test performance aspects of K8sResourceMonitor."""

    @pytest.fixture
    def connected_monitor(self) -> K8sResourceMonitor:
        """Create a connected monitor instance."""
        monitor = K8sResourceMonitor()
        with patch("k8s_resource_monitor.monitor.config"):
            monitor.core_v1 = MagicMock()
            monitor.apps_v1 = MagicMock()
            monitor.metrics_client = MagicMock()
            monitor.is_connected = True
        return monitor

    def test_large_namespace_performance(
        self, connected_monitor: K8sResourceMonitor
    ) -> None:
        """Test performance with large namespace (1000 pods)."""
        # Create 1000 mock pods
        pods = []
        for i in range(1000):
            pod = V1Pod(
                metadata=V1ObjectMeta(
                    name=f"pod-{i}",
                    namespace="large-namespace",
                    uid=f"uid-{i}",
                    creation_timestamp=datetime.now(),
                ),
                spec=V1PodSpec(
                    node_name=f"node-{i % 10}",
                    containers=[
                        V1Container(
                            name="app",
                            resources=V1ResourceRequirements(
                                limits={"cpu": "500m", "memory": "512Mi"},
                                requests={"cpu": "100m", "memory": "128Mi"},
                            ),
                        )
                    ],
                ),
                status=V1PodStatus(
                    phase="Running",
                    container_statuses=[
                        V1ContainerStatus(
                            name="app",
                            container_id=f"docker://abc{i}",
                            restart_count=0,
                            ready=True,
                            started=True,
                            image="nginx:latest",
                            image_id="docker://sha256:abc123",
                        )
                    ],
                ),
            )
            pods.append(pod)

        connected_monitor.core_v1.list_namespaced_pod.return_value = V1PodList(
            items=pods
        )
        connected_monitor.metrics_client.get_namespaced_custom_object.side_effect = (
            ApiException("Not found")
        )

        import time

        start = time.time()
        resources = connected_monitor.get_namespace_resources("large-namespace")
        duration = time.time() - start

        assert len(resources.pods) == 1000
        assert duration < 5.0  # Should process 1000 pods in under 5 seconds

    def test_many_nodes_performance(
        self, connected_monitor: K8sResourceMonitor
    ) -> None:
        """Test performance with many nodes (100 nodes)."""
        nodes = []
        for i in range(100):
            node = V1Node(
                metadata=V1ObjectMeta(name=f"node-{i}"),
                status=V1NodeStatus(
                    capacity={
                        "cpu": "16",
                        "memory": "64Gi",
                        "ephemeral-storage": "500Gi",
                        "pods": "110",
                    },
                    allocatable={
                        "cpu": "15800m",
                        "memory": "63Gi",
                        "ephemeral-storage": "490Gi",
                        "pods": "110",
                    },
                    conditions=[
                        V1NodeCondition(
                            type="Ready",
                            status="True",
                            last_heartbeat_time=None,
                            last_transition_time=None,
                            message="",
                            reason="",
                        )
                    ],
                ),
            )
            nodes.append(node)

        connected_monitor.core_v1.list_node.return_value = V1NodeList(items=nodes)
        connected_monitor.core_v1.list_pod_for_all_namespaces.return_value = V1PodList(
            items=[]
        )
        connected_monitor.metrics_client.get_cluster_custom_object.side_effect = (
            ApiException("Not found")
        )

        import time

        start = time.time()
        node_pressures = connected_monitor.analyze_node_pressure()
        duration = time.time() - start

        assert len(node_pressures) == 100
        assert duration < 5.0  # Should process 100 nodes in under 5 seconds


class TestK8sResourceMonitorBoundaries:
    """Test boundary conditions for K8sResourceMonitor."""

    @pytest.fixture
    def connected_monitor(self) -> K8sResourceMonitor:
        """Create a connected monitor instance."""
        monitor = K8sResourceMonitor()
        with patch("k8s_resource_monitor.monitor.config"):
            monitor.core_v1 = MagicMock()
            monitor.apps_v1 = MagicMock()
            monitor.metrics_client = MagicMock()
            monitor.is_connected = True
        return monitor

    def test_empty_cluster(self, connected_monitor: K8sResourceMonitor) -> None:
        """Test monitoring empty cluster."""
        connected_monitor.core_v1.list_namespace.return_value = V1NamespaceList(
            items=[]
        )
        connected_monitor.core_v1.list_node.return_value = V1NodeList(items=[])

        # Test with no namespaces
        breaches = connected_monitor.detect_limit_breaches()
        assert len(breaches) == 0

        # Test with no nodes
        node_pressures = connected_monitor.analyze_node_pressure()
        assert len(node_pressures) == 0

    def test_maximum_values(self, connected_monitor: K8sResourceMonitor) -> None:
        """Test with maximum resource values."""
        pod = V1Pod(
            metadata=V1ObjectMeta(
                name="max-pod",
                namespace="default",
                uid="uid-max",
                creation_timestamp=datetime.now(),
            ),
            spec=V1PodSpec(
                node_name="node-1",
                containers=[
                    V1Container(
                        name="app",
                        resources=V1ResourceRequirements(
                            limits={
                                "cpu": "1000000m",
                                "memory": "10000Gi",
                            },  # Huge values
                            requests={"cpu": "500000m", "memory": "5000Gi"},
                        ),
                    )
                ],
            ),
            status=V1PodStatus(
                phase="Running",
                container_statuses=[
                    V1ContainerStatus(
                        name="app",
                        container_id="docker://abc123",
                        restart_count=999999,  # High restart count
                        ready=True,
                        started=True,
                        image="nginx:latest",
                        image_id="docker://sha256:abc123",
                    )
                ],
            ),
        )

        connected_monitor.core_v1.list_namespaced_pod.return_value = V1PodList(
            items=[pod]
        )
        connected_monitor.metrics_client.get_namespaced_custom_object.return_value = {
            "containers": [
                {
                    "name": "app",
                    "usage": {"cpu": "999999m", "memory": "9999Gi"},
                }
            ]
        }

        resources = connected_monitor.get_namespace_resources("default")
        assert len(resources.pods) == 1
        assert resources.pods[0].containers[0].cpu_limit == 1000000.0  # 1000 cores
        assert resources.pods[0].containers[0].restart_count == 999999

    def test_minimum_values(self, connected_monitor: K8sResourceMonitor) -> None:
        """Test with minimum/zero resource values."""
        pod = V1Pod(
            metadata=V1ObjectMeta(
                name="min-pod",
                namespace="default",
                uid="uid-min",
                creation_timestamp=datetime.now(),
            ),
            spec=V1PodSpec(
                node_name="node-1",
                containers=[
                    V1Container(
                        name="app",
                        resources=V1ResourceRequirements(
                            limits={"cpu": "1m", "memory": "1Ki"},  # Tiny values
                            requests={"cpu": "1m", "memory": "1Ki"},
                        ),
                    )
                ],
            ),
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

        connected_monitor.core_v1.list_namespaced_pod.return_value = V1PodList(
            items=[pod]
        )
        connected_monitor.metrics_client.get_namespaced_custom_object.return_value = {
            "containers": [
                {
                    "name": "app",
                    "usage": {"cpu": "0m", "memory": "0"},
                }
            ]
        }

        resources = connected_monitor.get_namespace_resources("default")
        assert len(resources.pods) == 1
        assert resources.pods[0].containers[0].cpu_limit == 1.0  # 1 millicore
        assert resources.pods[0].containers[0].memory_limit == 1024  # 1Ki


class TestK8sResourceMonitorSpecialCases:
    """Test special cases and scenarios."""

    @pytest.fixture
    def connected_monitor(self) -> K8sResourceMonitor:
        """Create a connected monitor instance."""
        monitor = K8sResourceMonitor()
        with patch("k8s_resource_monitor.monitor.config"):
            monitor.core_v1 = MagicMock()
            monitor.apps_v1 = MagicMock()
            monitor.metrics_client = MagicMock()
            monitor.is_connected = True
        return monitor

    def test_system_namespaces(self, connected_monitor: K8sResourceMonitor) -> None:
        """Test monitoring system namespaces."""
        system_namespaces = ["kube-system", "kube-public", "kube-node-lease"]

        for ns in system_namespaces:
            pod = V1Pod(
                metadata=V1ObjectMeta(
                    name=f"{ns}-pod",
                    namespace=ns,
                    uid=f"uid-{ns}",
                    creation_timestamp=datetime.now(),
                    labels={"component": "kube-apiserver"},
                ),
                spec=V1PodSpec(
                    node_name="master-1",
                    containers=[
                        V1Container(
                            name="kube-apiserver",
                            resources=V1ResourceRequirements(
                                requests={"cpu": "250m", "memory": "512Mi"},
                            ),
                        )
                    ],
                ),
                status=V1PodStatus(
                    phase="Running",
                    container_statuses=[
                        V1ContainerStatus(
                            name="kube-apiserver",
                            container_id="docker://system123",
                            restart_count=0,
                            ready=True,
                            started=True,
                            image="k8s.gcr.io/kube-apiserver:v1.25.0",
                            image_id="docker://sha256:system123",
                        )
                    ],
                ),
            )

            connected_monitor.core_v1.list_namespaced_pod.return_value = V1PodList(
                items=[pod]
            )
            connected_monitor.metrics_client.get_namespaced_custom_object.side_effect = ApiException(
                "Not found"
            )

            resources = connected_monitor.get_namespace_resources(ns)
            assert resources.namespace == ns
            assert len(resources.pods) == 1

    def test_pod_with_init_containers(
        self, connected_monitor: K8sResourceMonitor
    ) -> None:
        """Test pod with init containers (not currently handled but shouldn't break)."""
        pod = V1Pod(
            metadata=V1ObjectMeta(
                name="init-pod",
                namespace="default",
                uid="uid-init",
                creation_timestamp=datetime.now(),
            ),
            spec=V1PodSpec(
                node_name="node-1",
                init_containers=[  # Init containers
                    V1Container(
                        name="init",
                        resources=V1ResourceRequirements(
                            requests={"cpu": "100m", "memory": "128Mi"},
                        ),
                    )
                ],
                containers=[
                    V1Container(
                        name="app",
                        resources=V1ResourceRequirements(
                            requests={"cpu": "200m", "memory": "256Mi"},
                        ),
                    )
                ],
            ),
            status=V1PodStatus(
                phase="Running",
                init_container_statuses=[  # Init container status
                    V1ContainerStatus(
                        name="init",
                        container_id="docker://init123",
                        restart_count=0,
                        ready=True,
                        started=True,
                        image="busybox:latest",
                        image_id="docker://sha256:init123",
                    )
                ],
                container_statuses=[
                    V1ContainerStatus(
                        name="app",
                        container_id="docker://app123",
                        restart_count=0,
                        ready=True,
                        started=True,
                        image="nginx:latest",
                        image_id="docker://sha256:app123",
                    )
                ],
            ),
        )

        connected_monitor.core_v1.list_namespaced_pod.return_value = V1PodList(
            items=[pod]
        )
        connected_monitor.metrics_client.get_namespaced_custom_object.side_effect = (
            ApiException("Not found")
        )

        resources = connected_monitor.get_namespace_resources("default")
        assert len(resources.pods) == 1
        # Currently only main containers are processed
        assert len(resources.pods[0].containers) == 1
        assert resources.pods[0].containers[0].name == "app"
