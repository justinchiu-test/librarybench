"""Extended tests for data models with edge cases and validation."""

from datetime import datetime, timedelta

import pytest
from pydantic import ValidationError

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


class TestContainerStatsExtended:
    """Extended tests for ContainerStats model."""

    def test_container_stats_negative_values(self) -> None:
        """Test container stats with negative values."""
        # Currently negative values are allowed by the model
        stats = ContainerStats(
            name="app",
            container_id="docker://abc123",
            runtime="docker",
            cpu_usage=-100.0,  # Negative CPU
            memory_usage=100 * 1024 * 1024,
        )
        assert stats.cpu_usage == -100.0

    def test_container_stats_zero_values(self) -> None:
        """Test container stats with zero values."""
        stats = ContainerStats(
            name="app",
            container_id="",
            runtime="unknown",
            cpu_usage=0.0,
            memory_usage=0,
        )
        assert stats.cpu_usage == 0.0
        assert stats.memory_usage == 0
        assert stats.runtime == "unknown"

    def test_container_stats_max_values(self) -> None:
        """Test container stats with very large values."""
        stats = ContainerStats(
            name="heavy-app",
            container_id="docker://xyz789",
            runtime="containerd",
            cpu_usage=64000.0,  # 64 cores
            cpu_limit=128000.0,  # 128 cores
            memory_usage=256 * 1024 * 1024 * 1024,  # 256GB
            memory_limit=512 * 1024 * 1024 * 1024,  # 512GB
            restart_count=9999,
        )
        assert stats.cpu_usage == 64000.0
        assert stats.memory_usage == 256 * 1024 * 1024 * 1024

    def test_container_stats_all_fields(self) -> None:
        """Test container stats with all fields populated."""
        stats = ContainerStats(
            name="full-app",
            container_id="cri-o://full123",
            runtime="cri-o",
            cpu_usage=1000.0,
            cpu_limit=2000.0,
            cpu_request=500.0,
            memory_usage=1024 * 1024 * 1024,
            memory_limit=2048 * 1024 * 1024,
            memory_request=512 * 1024 * 1024,
            restart_count=5,
            is_oomkilled=True,
            cgroup_path="/sys/fs/cgroup/memory/kubepods/pod123/container456",
        )
        assert stats.is_oomkilled is True
        assert stats.cgroup_path != ""
        assert stats.restart_count == 5


class TestPodResourcesExtended:
    """Extended tests for PodResources model."""

    def test_pod_resources_empty_containers(self) -> None:
        """Test pod with no containers."""
        pod = PodResources(
            name="empty-pod",
            namespace="default",
            uid="uid-empty",
            node_name="node-1",
            phase="Pending",
            containers=[],
        )
        assert len(pod.containers) == 0
        assert pod.total_cpu_usage == 0

    def test_pod_resources_many_containers(self) -> None:
        """Test pod with many containers."""
        containers = [
            ContainerStats(
                name=f"container-{i}",
                container_id=f"docker://c{i}",
                runtime="docker",
                cpu_usage=float(i * 100),
                memory_usage=i * 1024 * 1024,
            )
            for i in range(20)
        ]

        pod = PodResources(
            name="multi-container-pod",
            namespace="default",
            uid="uid-multi",
            node_name="node-1",
            phase="Running",
            containers=containers,
        )
        assert len(pod.containers) == 20

    def test_pod_resources_special_namespaces(self) -> None:
        """Test pods in system namespaces."""
        system_namespaces = ["kube-system", "kube-public", "kube-node-lease", "default"]

        for ns in system_namespaces:
            pod = PodResources(
                name=f"system-pod-{ns}",
                namespace=ns,
                uid=f"uid-{ns}",
                node_name="master-1",
                phase="Running",
                containers=[],
            )
            assert pod.namespace == ns

    def test_pod_resources_various_phases(self) -> None:
        """Test pods in different phases."""
        phases = ["Pending", "Running", "Succeeded", "Failed", "Unknown"]

        for phase in phases:
            pod = PodResources(
                name=f"pod-{phase.lower()}",
                namespace="default",
                uid=f"uid-{phase}",
                node_name="node-1",
                phase=phase,
                containers=[],
            )
            assert pod.phase == phase

    def test_pod_resources_with_labels_and_annotations(self) -> None:
        """Test pod with complex labels and annotations."""
        pod = PodResources(
            name="labeled-pod",
            namespace="default",
            uid="uid-labeled",
            node_name="node-1",
            phase="Running",
            containers=[],
            labels={
                "app": "web",
                "version": "v1.2.3",
                "environment": "production",
                "team": "platform",
                "app.kubernetes.io/name": "my-app",
                "app.kubernetes.io/version": "1.2.3",
            },
            annotations={
                "prometheus.io/scrape": "true",
                "prometheus.io/port": "9090",
                "kubectl.kubernetes.io/last-applied-configuration": "{}",
                "deployment.kubernetes.io/revision": "5",
            },
        )
        assert len(pod.labels) == 6
        assert len(pod.annotations) == 4
        assert pod.labels["app"] == "web"


class TestResourceBreachExtended:
    """Extended tests for ResourceBreach model."""

    def test_breach_boundary_values(self) -> None:
        """Test breaches at exact boundary values."""
        # Exactly at 90% threshold
        breach = ResourceBreach(
            pod_name="test-pod",
            namespace="default",
            container_name="app",
            resource_type=ResourceType.CPU,
            current_usage=900.0,
            limit=1000.0,
            threshold_percent=90.0,
        )
        assert breach.breach_percent == 90.0
        assert breach.severity == "warning"

        # Exactly at 95% threshold
        breach = ResourceBreach(
            pod_name="test-pod",
            namespace="default",
            container_name="app",
            resource_type=ResourceType.MEMORY,
            current_usage=950.0,
            limit=1000.0,
            threshold_percent=90.0,
        )
        assert breach.breach_percent == 95.0
        assert breach.severity == "critical"

    def test_breach_different_resource_types(self) -> None:
        """Test breaches for different resource types."""
        for resource_type in ResourceType:
            breach = ResourceBreach(
                pod_name="test-pod",
                namespace="default",
                container_name="app",
                resource_type=resource_type,
                current_usage=900.0,
                limit=1000.0,
                threshold_percent=80.0,
            )
            assert breach.resource_type == resource_type

    def test_breach_over_100_percent(self) -> None:
        """Test breach over 100% of limit."""
        breach = ResourceBreach(
            pod_name="test-pod",
            namespace="default",
            container_name="app",
            resource_type=ResourceType.CPU,
            current_usage=1500.0,
            limit=1000.0,
            threshold_percent=90.0,
        )
        assert breach.breach_percent == 150.0
        assert breach.severity == "critical"

    def test_breach_timestamp(self) -> None:
        """Test breach timestamp is recent."""
        breach = ResourceBreach(
            pod_name="test-pod",
            namespace="default",
            container_name="app",
            resource_type=ResourceType.CPU,
            current_usage=900.0,
            limit=1000.0,
            threshold_percent=90.0,
        )
        assert (datetime.now() - breach.timestamp) < timedelta(seconds=1)


class TestNodePressureExtended:
    """Extended tests for NodePressure model."""

    def test_node_pressure_edge_cases(self) -> None:
        """Test node pressure calculation edge cases."""
        # Node with no allocatable resources
        node = NodePressure(
            node_name="edge-node",
            cpu_capacity=4000.0,
            cpu_allocatable=0.0,  # No allocatable CPU
            cpu_allocated=0.0,
            cpu_usage=0.0,
            memory_capacity=8 * 1024 * 1024 * 1024,
            memory_allocatable=0,  # No allocatable memory
            memory_allocated=0,
            memory_usage=0,
            ephemeral_storage_capacity=100 * 1024 * 1024 * 1024,
            ephemeral_storage_allocatable=0,
            ephemeral_storage_usage=0,
            pod_capacity=0,
            pod_count=0,
        )

        node.calculate_pressure_metrics()
        assert node.scheduling_pressure == 0
        assert node.eviction_risk == 0

    def test_node_pressure_full_node(self) -> None:
        """Test fully utilized node."""
        node = NodePressure(
            node_name="full-node",
            cpu_capacity=4000.0,
            cpu_allocatable=3800.0,
            cpu_allocated=3800.0,  # Fully allocated
            cpu_usage=3800.0,  # Fully used
            memory_capacity=8 * 1024 * 1024 * 1024,
            memory_allocatable=7 * 1024 * 1024 * 1024,
            memory_allocated=7 * 1024 * 1024 * 1024,  # Fully allocated
            memory_usage=7 * 1024 * 1024 * 1024,  # Fully used
            ephemeral_storage_capacity=100 * 1024 * 1024 * 1024,
            ephemeral_storage_allocatable=90 * 1024 * 1024 * 1024,
            ephemeral_storage_usage=90 * 1024 * 1024 * 1024,
            pod_capacity=110,
            pod_count=110,  # At capacity
        )

        node.calculate_pressure_metrics()
        assert node.scheduling_pressure == 1.0  # Maximum pressure
        assert node.eviction_risk == 1.0  # Maximum risk
        assert node.resource_fragmentation == 0.0  # No fragmentation

    def test_node_conditions(self) -> None:
        """Test various node conditions."""
        node = NodePressure(
            node_name="condition-node",
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
            conditions={
                "Ready": True,
                "MemoryPressure": False,
                "DiskPressure": False,
                "PIDPressure": False,
                "NetworkUnavailable": False,
            },
        )

        assert len(node.conditions) == 5
        assert node.conditions["Ready"] is True
        assert node.conditions["MemoryPressure"] is False


class TestHPAMetricExtended:
    """Extended tests for HPAMetric model."""

    def test_hpa_metric_all_types(self) -> None:
        """Test all metric types."""
        for metric_type in MetricType:
            metric = HPAMetric(
                deployment="test-deployment",
                namespace="default",
                metric_type=metric_type,
                metric_name=f"test_{metric_type.value}",
                value=100.0,
                aggregation=AggregationType.AVG,
            )
            assert metric.metric_type == metric_type

    def test_hpa_metric_all_aggregations(self) -> None:
        """Test all aggregation types."""
        for agg_type in AggregationType:
            metric = HPAMetric(
                deployment="test-deployment",
                namespace="default",
                metric_type=MetricType.CUSTOM,
                metric_name="test_metric",
                value=100.0,
                aggregation=agg_type,
            )
            assert metric.aggregation == agg_type

    def test_hpa_scaling_scenarios(self) -> None:
        """Test various scaling scenarios."""
        # Scale up scenario
        metric = HPAMetric(
            deployment="api-server",
            namespace="production",
            metric_type=MetricType.RESOURCE,
            metric_name="cpu_usage",
            value=800.0,  # High usage
            aggregation=AggregationType.AVG,
            current_replicas=2,
            target_value=500.0,
            min_replicas=1,
            max_replicas=10,
        )

        desired = metric.calculate_desired_replicas()
        assert desired > metric.current_replicas  # Should scale up

        # Scale down scenario
        metric.value = 100.0  # Low usage
        metric.current_replicas = 5

        desired = metric.calculate_desired_replicas()
        assert desired < metric.current_replicas  # Should scale down

    def test_hpa_metric_windows(self) -> None:
        """Test different time windows."""
        windows = ["30s", "1m", "5m", "10m", "30m", "1h"]

        for window in windows:
            metric = HPAMetric(
                deployment="test-deployment",
                namespace="default",
                metric_type=MetricType.CUSTOM,
                metric_name="test_metric",
                value=100.0,
                aggregation=AggregationType.AVG,
                window=window,
            )
            assert metric.window == window


class TestResourceQuotaExtended:
    """Extended tests for ResourceQuota model."""

    def test_quota_various_resources(self) -> None:
        """Test quota with various resource types."""
        quota = ResourceQuota(
            namespace="test-namespace",
            quota_name="comprehensive-quota",
            hard_limits={
                "cpu": "100",
                "memory": "200Gi",
                "requests.cpu": "50",
                "requests.memory": "100Gi",
                "limits.cpu": "100",
                "limits.memory": "200Gi",
                "persistentvolumeclaims": "10",
                "pods": "50",
                "services": "10",
                "services.loadbalancers": "2",
                "services.nodeports": "5",
                "configmaps": "100",
                "secrets": "100",
            },
            used={
                "cpu": "75",
                "memory": "150Gi",
                "requests.cpu": "40",
                "requests.memory": "80Gi",
                "limits.cpu": "75",
                "limits.memory": "150Gi",
                "persistentvolumeclaims": "8",
                "pods": "35",
                "services": "7",
                "services.loadbalancers": "1",
                "services.nodeports": "3",
                "configmaps": "50",
                "secrets": "60",
            },
        )

        quota.calculate_utilization()

        assert len(quota.utilization) == 13
        assert quota.utilization["cpu"] == 75.0
        assert quota.utilization["pods"] == 70.0  # 35/50

    def test_quota_empty_usage(self) -> None:
        """Test quota with no usage."""
        quota = ResourceQuota(
            namespace="empty-namespace",
            quota_name="unused-quota",
            hard_limits={
                "cpu": "10",
                "memory": "20Gi",
            },
            used={},  # No usage
        )

        quota.calculate_utilization()
        assert len(quota.utilization) == 0

    def test_quota_parse_special_values(self) -> None:
        """Test parsing special resource values."""
        # Test parsing decimal values
        assert ResourceQuota._parse_resource_value("0.5") == 0.5
        assert ResourceQuota._parse_resource_value("1.5") == 1.5

        # Test parsing with spaces
        assert ResourceQuota._parse_resource_value(" 100m ") == 100
        assert ResourceQuota._parse_resource_value(" 1Gi ") == 1024 * 1024 * 1024


class TestNamespaceResourcesExtended:
    """Extended tests for NamespaceResources model."""

    def test_namespace_large_scale(self) -> None:
        """Test namespace with many pods."""
        pods = []
        for i in range(100):
            pod = PodResources(
                name=f"pod-{i}",
                namespace="large-namespace",
                uid=f"uid-{i}",
                node_name=f"node-{i % 10}",
                phase="Running",
                containers=[
                    ContainerStats(
                        name="app",
                        container_id=f"docker://c{i}",
                        runtime="docker",
                        cpu_usage=100.0,
                        memory_usage=100 * 1024 * 1024,
                    )
                ],
                total_cpu_usage=100.0,
                total_memory_usage=100 * 1024 * 1024,
            )
            pods.append(pod)

        namespace = NamespaceResources(
            namespace="large-namespace",
            pods=pods,
        )

        namespace.calculate_totals()

        assert namespace.pod_count == 100
        assert namespace.container_count == 100
        assert namespace.total_cpu_usage == 10000.0  # 100 * 100

    def test_namespace_mixed_pod_states(self) -> None:
        """Test namespace with pods in different states."""
        pods = [
            PodResources(
                name="running-pod",
                namespace="mixed",
                uid="uid-1",
                node_name="node-1",
                phase="Running",
                containers=[],
                total_cpu_usage=100.0,
                total_memory_usage=100 * 1024 * 1024,
            ),
            PodResources(
                name="pending-pod",
                namespace="mixed",
                uid="uid-2",
                node_name="",
                phase="Pending",
                containers=[],
                total_cpu_usage=0.0,
                total_memory_usage=0,
            ),
            PodResources(
                name="failed-pod",
                namespace="mixed",
                uid="uid-3",
                node_name="node-1",
                phase="Failed",
                containers=[],
                total_cpu_usage=0.0,
                total_memory_usage=0,
            ),
        ]

        namespace = NamespaceResources(
            namespace="mixed",
            pods=pods,
        )

        namespace.calculate_totals()
        assert namespace.pod_count == 3
        assert namespace.total_cpu_usage == 100.0  # Only from running pod


class TestResourceRecommendationExtended:
    """Extended tests for ResourceRecommendation model."""

    def test_recommendation_all_targets(self) -> None:
        """Test recommendations for all optimization targets."""
        for target in OptimizationTarget:
            rec = ResourceRecommendation(
                namespace="test",
                pod_name="test-pod",
                container_name="app",
                resource_type=ResourceType.CPU,
                current_request=1000.0,
                current_limit=2000.0,
                recommended_request=800.0,
                recommended_limit=1600.0,
                optimization_target=target,
                reason=f"Optimized for {target.value}",
            )
            assert rec.optimization_target == target

    def test_recommendation_no_current_values(self) -> None:
        """Test recommendation when no current values exist."""
        rec = ResourceRecommendation(
            namespace="test",
            pod_name="new-pod",
            container_name="app",
            resource_type=ResourceType.MEMORY,
            current_request=None,
            current_limit=None,
            recommended_request=512 * 1024 * 1024,
            recommended_limit=1024 * 1024 * 1024,
            optimization_target=OptimizationTarget.BALANCED,
            reason="Initial recommendation for new pod",
        )
        assert rec.current_request is None
        assert rec.current_limit is None
        assert rec.recommended_request > 0

    def test_recommendation_increase_resources(self) -> None:
        """Test recommendation to increase resources."""
        rec = ResourceRecommendation(
            namespace="test",
            pod_name="underprovisioned-pod",
            container_name="app",
            resource_type=ResourceType.CPU,
            current_request=100.0,
            current_limit=200.0,
            recommended_request=500.0,
            recommended_limit=1000.0,
            optimization_target=OptimizationTarget.PERFORMANCE,
            reason="Pod experiencing CPU throttling",
            potential_savings=None,  # No savings when increasing
        )
        assert rec.recommended_request > rec.current_request
        assert rec.recommended_limit > rec.current_limit
        assert rec.potential_savings is None


class TestEnumValidation:
    """Test enum validation for all enums."""

    def test_resource_type_validation(self) -> None:
        """Test ResourceType enum validation."""
        valid_types = ["cpu", "memory", "storage", "ephemeral-storage"]
        for t in valid_types:
            assert ResourceType(t) in ResourceType

        with pytest.raises(ValueError):
            ResourceType("invalid-type")

    def test_optimization_target_validation(self) -> None:
        """Test OptimizationTarget enum validation."""
        valid_targets = ["balanced", "performance", "cost"]
        for t in valid_targets:
            assert OptimizationTarget(t) in OptimizationTarget

        with pytest.raises(ValueError):
            OptimizationTarget("invalid-target")

    def test_metric_type_validation(self) -> None:
        """Test MetricType enum validation."""
        valid_types = [
            "resource",
            "custom",
            "requests_per_second",
            "response_time",
            "queue_depth",
        ]
        for t in valid_types:
            assert MetricType(t) in MetricType

        with pytest.raises(ValueError):
            MetricType("invalid-metric")

    def test_aggregation_type_validation(self) -> None:
        """Test AggregationType enum validation."""
        valid_types = ["avg", "max", "min", "p50", "p90", "p95", "p99"]
        for t in valid_types:
            assert AggregationType(t) in AggregationType

        with pytest.raises(ValueError):
            AggregationType("invalid-agg")


class TestModelSerialization:
    """Test model serialization and deserialization."""

    def test_container_stats_serialization(self) -> None:
        """Test ContainerStats serialization."""
        stats = ContainerStats(
            name="app",
            container_id="docker://abc123",
            runtime="docker",
            cpu_usage=100.0,
            memory_usage=100 * 1024 * 1024,
        )

        # Serialize to dict
        data = stats.model_dump()
        assert data["name"] == "app"
        assert data["cpu_usage"] == 100.0

        # Deserialize from dict
        stats2 = ContainerStats(**data)
        assert stats2.name == stats.name
        assert stats2.cpu_usage == stats.cpu_usage

    def test_pod_resources_json(self) -> None:
        """Test PodResources JSON serialization."""
        pod = PodResources(
            name="test-pod",
            namespace="default",
            uid="uid-123",
            node_name="node-1",
            phase="Running",
            containers=[],
            created_at=datetime.now(),
        )

        # Serialize to JSON
        json_str = pod.model_dump_json()
        assert "test-pod" in json_str
        assert "uid-123" in json_str

    def test_resource_breach_copy(self) -> None:
        """Test ResourceBreach deep copy."""
        breach = ResourceBreach(
            pod_name="test-pod",
            namespace="default",
            container_name="app",
            resource_type=ResourceType.CPU,
            current_usage=900.0,
            limit=1000.0,
            threshold_percent=90.0,
        )

        # Create a copy
        breach_copy = breach.model_copy()
        assert breach_copy.pod_name == breach.pod_name
        assert breach_copy.breach_percent == breach.breach_percent
        assert breach_copy is not breach  # Different object
