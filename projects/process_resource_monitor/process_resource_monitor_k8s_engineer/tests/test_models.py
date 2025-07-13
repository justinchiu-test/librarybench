"""Tests for data models."""



from k8s_resource_monitor.models import (
    AggregationType,
    ContainerStats,
    HPAMetric,
    MetricType,
    NamespaceResources,
    NodePressure,
    OptimizationTarget,
    PodResources,
    ResourceBreach,
    ResourceQuota,
    ResourceRecommendation,
    ResourceType,
)


class TestContainerStats:
    """Test ContainerStats model."""

    def test_container_stats_creation(self) -> None:
        """Test creating container stats."""
        stats = ContainerStats(
            name="nginx",
            container_id="docker://abc123",
            runtime="docker",
            cpu_usage=100.0,
            cpu_limit=500.0,
            memory_usage=100 * 1024 * 1024,
            memory_limit=500 * 1024 * 1024,
        )

        assert stats.name == "nginx"
        assert stats.container_id == "docker://abc123"
        assert stats.runtime == "docker"
        assert stats.cpu_usage == 100.0
        assert stats.cpu_limit == 500.0
        assert stats.memory_usage == 100 * 1024 * 1024
        assert stats.memory_limit == 500 * 1024 * 1024
        assert stats.restart_count == 0
        assert stats.is_oomkilled is False


class TestPodResources:
    """Test PodResources model."""

    def test_pod_resources_creation(self) -> None:
        """Test creating pod resources."""
        containers = [
            ContainerStats(
                name="app",
                container_id="docker://app123",
                runtime="docker",
                cpu_usage=100.0,
                cpu_request=50.0,
                memory_usage=100 * 1024 * 1024,
                memory_request=50 * 1024 * 1024,
            ),
            ContainerStats(
                name="sidecar",
                container_id="docker://side123",
                runtime="docker",
                cpu_usage=50.0,
                cpu_request=25.0,
                memory_usage=50 * 1024 * 1024,
                memory_request=25 * 1024 * 1024,
            ),
        ]

        pod = PodResources(
            name="test-pod",
            namespace="default",
            uid="uid-123",
            node_name="node-1",
            phase="Running",
            containers=containers,
            total_cpu_usage=150.0,
            total_cpu_request=75.0,
            total_memory_usage=150 * 1024 * 1024,
            total_memory_request=75 * 1024 * 1024,
        )

        assert pod.name == "test-pod"
        assert pod.namespace == "default"
        assert len(pod.containers) == 2
        assert pod.total_cpu_usage == 150.0
        assert pod.total_cpu_request == 75.0

    def test_calculate_efficiency(self) -> None:
        """Test efficiency calculation."""
        pod = PodResources(
            name="test-pod",
            namespace="default",
            uid="uid-123",
            node_name="node-1",
            phase="Running",
            containers=[],
            total_cpu_usage=100.0,
            total_cpu_request=200.0,
            total_memory_usage=100 * 1024 * 1024,
            total_memory_request=200 * 1024 * 1024,
        )

        efficiency = pod.calculate_efficiency()

        assert efficiency["cpu"] == 0.5  # 100/200
        assert efficiency["memory"] == 0.5  # 100MB/200MB

    def test_calculate_efficiency_no_requests(self) -> None:
        """Test efficiency calculation with no requests."""
        pod = PodResources(
            name="test-pod",
            namespace="default",
            uid="uid-123",
            node_name="node-1",
            phase="Running",
            containers=[],
            total_cpu_usage=100.0,
            total_memory_usage=100 * 1024 * 1024,
        )

        efficiency = pod.calculate_efficiency()

        assert efficiency == {}  # No requests, no efficiency


class TestResourceBreach:
    """Test ResourceBreach model."""

    def test_breach_severity_critical(self) -> None:
        """Test breach with critical severity."""
        breach = ResourceBreach(
            pod_name="test-pod",
            namespace="default",
            container_name="app",
            resource_type=ResourceType.CPU,
            current_usage=950.0,
            limit=1000.0,
            threshold_percent=90.0,
        )

        assert breach.breach_percent == 95.0
        assert breach.severity == "critical"

    def test_breach_severity_warning(self) -> None:
        """Test breach with warning severity."""
        breach = ResourceBreach(
            pod_name="test-pod",
            namespace="default",
            container_name="app",
            resource_type=ResourceType.CPU,
            current_usage=920.0,
            limit=1000.0,
            threshold_percent=90.0,
        )

        assert breach.breach_percent == 92.0
        assert breach.severity == "warning"

    def test_breach_severity_info(self) -> None:
        """Test breach with info severity."""
        breach = ResourceBreach(
            pod_name="test-pod",
            namespace="default",
            container_name="app",
            resource_type=ResourceType.CPU,
            current_usage=850.0,
            limit=1000.0,
            threshold_percent=80.0,
        )

        assert breach.breach_percent == 85.0
        assert breach.severity == "info"


class TestNodePressure:
    """Test NodePressure model."""

    def test_node_pressure_creation(self) -> None:
        """Test creating node pressure."""
        node = NodePressure(
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
        )

        assert node.node_name == "node-1"
        assert node.cpu_capacity == 4000.0
        assert node.cpu_allocatable == 3800.0

    def test_calculate_pressure_metrics(self) -> None:
        """Test pressure metrics calculation."""
        node = NodePressure(
            node_name="node-1",
            cpu_capacity=4000.0,
            cpu_allocatable=3800.0,
            cpu_allocated=3420.0,  # 90% of allocatable
            cpu_usage=3040.0,  # 80% of allocatable
            memory_capacity=8 * 1024 * 1024 * 1024,
            memory_allocatable=7 * 1024 * 1024 * 1024,
            memory_allocated=int(5.6 * 1024 * 1024 * 1024),  # 80% of allocatable
            memory_usage=int(5.6 * 1024 * 1024 * 1024),  # 80% of allocatable
            ephemeral_storage_capacity=100 * 1024 * 1024 * 1024,
            ephemeral_storage_allocatable=90 * 1024 * 1024 * 1024,
            ephemeral_storage_usage=50 * 1024 * 1024 * 1024,
            pod_capacity=110,
            pod_count=88,  # 80% of capacity
        )

        node.calculate_pressure_metrics()

        assert (
            node.scheduling_pressure == 0.9
        )  # Max of CPU (90%), memory (80%), pods (80%)
        assert node.eviction_risk == 0.8  # Max of CPU usage (80%), memory usage (80%)

        # Fragmentation: CPU allocated but not fully used
        expected_cpu_frag = 1 - (3040.0 / 3420.0)  # ~0.111
        expected_memory_frag = 0.0  # Memory is fully utilized
        expected_total_frag = (expected_cpu_frag + expected_memory_frag) / 2

        assert abs(node.resource_fragmentation - expected_total_frag) < 0.01


class TestHPAMetric:
    """Test HPAMetric model."""

    def test_hpa_metric_creation(self) -> None:
        """Test creating HPA metric."""
        metric = HPAMetric(
            deployment="api-server",
            namespace="production",
            metric_type=MetricType.REQUESTS_PER_SECOND,
            metric_name="api_requests_per_second",
            value=100.0,
            aggregation=AggregationType.P95,
            current_replicas=3,
            target_value=50.0,
        )

        assert metric.deployment == "api-server"
        assert metric.value == 100.0
        assert metric.target_value == 50.0

    def test_calculate_desired_replicas(self) -> None:
        """Test desired replicas calculation."""
        metric = HPAMetric(
            deployment="api-server",
            namespace="production",
            metric_type=MetricType.REQUESTS_PER_SECOND,
            metric_name="api_requests_per_second",
            value=100.0,
            aggregation=AggregationType.P95,
            current_replicas=3,
            target_value=50.0,
            min_replicas=2,
            max_replicas=10,
        )

        desired = metric.calculate_desired_replicas()

        assert desired == 6  # 3 * (100/50) = 6
        assert metric.desired_replicas == 6

    def test_calculate_desired_replicas_bounds(self) -> None:
        """Test desired replicas respects bounds."""
        # Test max bound
        metric = HPAMetric(
            deployment="api-server",
            namespace="production",
            metric_type=MetricType.REQUESTS_PER_SECOND,
            metric_name="api_requests_per_second",
            value=500.0,
            aggregation=AggregationType.P95,
            current_replicas=3,
            target_value=50.0,
            min_replicas=2,
            max_replicas=8,
        )

        desired = metric.calculate_desired_replicas()
        assert desired == 8  # Would be 30, but capped at max

        # Test min bound
        metric.value = 10.0
        metric.current_replicas = 5

        desired = metric.calculate_desired_replicas()
        assert desired == 2  # Would be 1, but min is 2


class TestResourceQuota:
    """Test ResourceQuota model."""

    def test_resource_quota_creation(self) -> None:
        """Test creating resource quota."""
        quota = ResourceQuota(
            namespace="production",
            quota_name="compute-quota",
            hard_limits={
                "cpu": "100",
                "memory": "200Gi",
                "persistentvolumeclaims": "10",
            },
            used={
                "cpu": "80",
                "memory": "150Gi",
                "persistentvolumeclaims": "8",
            },
        )

        assert quota.namespace == "production"
        assert quota.hard_limits["cpu"] == "100"
        assert quota.used["memory"] == "150Gi"

    def test_calculate_utilization(self) -> None:
        """Test utilization calculation."""
        quota = ResourceQuota(
            namespace="production",
            quota_name="compute-quota",
            hard_limits={
                "cpu": "100",
                "memory": "200Gi",
                "persistentvolumeclaims": "10",
            },
            used={
                "cpu": "80",
                "memory": "150Gi",
                "persistentvolumeclaims": "8",
            },
        )

        quota.calculate_utilization()

        assert quota.utilization["cpu"] == 80.0  # 80/100
        assert quota.utilization["memory"] == 75.0  # 150/200
        assert quota.utilization["persistentvolumeclaims"] == 80.0  # 8/10

    def test_parse_resource_value(self) -> None:
        """Test parsing Kubernetes resource values."""
        # CPU values
        assert ResourceQuota._parse_resource_value("100m") == 100
        assert ResourceQuota._parse_resource_value("1") == 1
        assert ResourceQuota._parse_resource_value("1000n") == 0.001

        # Memory values
        assert ResourceQuota._parse_resource_value("1Ki") == 1024
        assert ResourceQuota._parse_resource_value("1Mi") == 1024 * 1024
        assert ResourceQuota._parse_resource_value("1Gi") == 1024 * 1024 * 1024
        assert ResourceQuota._parse_resource_value("1K") == 1000
        assert ResourceQuota._parse_resource_value("1M") == 1000 * 1000

        # Plain numbers
        assert ResourceQuota._parse_resource_value("100") == 100
        assert ResourceQuota._parse_resource_value("0") == 0


class TestNamespaceResources:
    """Test NamespaceResources model."""

    def test_namespace_resources_creation(self) -> None:
        """Test creating namespace resources."""
        pods = [
            PodResources(
                name="pod-1",
                namespace="default",
                uid="uid-1",
                node_name="node-1",
                phase="Running",
                containers=[],
                total_cpu_usage=100.0,
                total_cpu_request=50.0,
                total_cpu_limit=200.0,
                total_memory_usage=100 * 1024 * 1024,
                total_memory_request=50 * 1024 * 1024,
                total_memory_limit=200 * 1024 * 1024,
            ),
            PodResources(
                name="pod-2",
                namespace="default",
                uid="uid-2",
                node_name="node-2",
                phase="Running",
                containers=[
                    ContainerStats(
                        name="container-1",
                        container_id="docker://c1",
                        runtime="docker",
                        cpu_usage=50.0,
                        memory_usage=50 * 1024 * 1024,
                    ),
                    ContainerStats(
                        name="container-2",
                        container_id="docker://c2",
                        runtime="docker",
                        cpu_usage=50.0,
                        memory_usage=50 * 1024 * 1024,
                    ),
                ],
                total_cpu_usage=100.0,
                total_cpu_request=50.0,
                total_cpu_limit=200.0,
                total_memory_usage=100 * 1024 * 1024,
                total_memory_request=50 * 1024 * 1024,
                total_memory_limit=200 * 1024 * 1024,
            ),
        ]

        namespace = NamespaceResources(
            namespace="default",
            pods=pods,
        )

        namespace.calculate_totals()

        assert namespace.pod_count == 2
        assert namespace.container_count == 2  # Only pod-2 has containers
        assert namespace.total_cpu_usage == 200.0
        assert namespace.total_cpu_request == 100.0
        assert namespace.total_cpu_limit == 400.0
        assert namespace.total_memory_usage == 200 * 1024 * 1024
        assert namespace.total_memory_request == 100 * 1024 * 1024
        assert namespace.total_memory_limit == 400 * 1024 * 1024


class TestResourceRecommendation:
    """Test ResourceRecommendation model."""

    def test_resource_recommendation_creation(self) -> None:
        """Test creating resource recommendation."""
        rec = ResourceRecommendation(
            namespace="production",
            pod_name="api-server",
            container_name="api",
            resource_type=ResourceType.CPU,
            current_request=100.0,
            current_limit=500.0,
            recommended_request=150.0,
            recommended_limit=300.0,
            optimization_target=OptimizationTarget.BALANCED,
            reason="Based on historical usage patterns",
            potential_savings=None,
        )

        assert rec.namespace == "production"
        assert rec.recommended_request == 150.0
        assert rec.optimization_target == OptimizationTarget.BALANCED

    def test_resource_recommendation_with_savings(self) -> None:
        """Test recommendation with cost savings."""
        rec = ResourceRecommendation(
            namespace="production",
            pod_name="api-server",
            container_name="api",
            resource_type=ResourceType.MEMORY,
            current_request=4 * 1024 * 1024 * 1024,
            current_limit=8 * 1024 * 1024 * 1024,
            recommended_request=2 * 1024 * 1024 * 1024,
            recommended_limit=4 * 1024 * 1024 * 1024,
            optimization_target=OptimizationTarget.COST,
            reason="Overprovisioned based on actual usage",
            potential_savings=2 * 1024 * 1024 * 1024,
        )

        assert rec.potential_savings == 2 * 1024 * 1024 * 1024
        assert rec.optimization_target == OptimizationTarget.COST
