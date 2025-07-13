"""Comprehensive tests to ensure full coverage."""

from unittest.mock import MagicMock, patch

from k8s_resource_monitor.models import (
    AggregationType,
    ContainerStats,
    HPAMetric,
    MetricType,
    OptimizationTarget,
    ResourceType,
)
from k8s_resource_monitor.monitor import K8sResourceMonitor


class TestComprehensiveCoverage:
    """Additional comprehensive tests."""

    def test_container_runtime_all_types(self) -> None:
        """Test all container runtime types."""
        monitor = K8sResourceMonitor()

        runtimes = {
            "docker://abc123": "docker",
            "containerd://def456": "containerd",
            "cri-o://ghi789": "cri-o",
            "unknown://xyz": "unknown",
            "": "unknown",
        }

        for container_id, expected_runtime in runtimes.items():
            assert monitor._detect_container_runtime(container_id) == expected_runtime

    def test_metric_type_conversions(self) -> None:
        """Test metric type string conversions."""
        assert MetricType.RESOURCE.value == "resource"
        assert MetricType.CUSTOM.value == "custom"
        assert MetricType.REQUESTS_PER_SECOND.value == "requests_per_second"
        assert MetricType.RESPONSE_TIME.value == "response_time"
        assert MetricType.QUEUE_DEPTH.value == "queue_depth"

    def test_aggregation_type_conversions(self) -> None:
        """Test aggregation type string conversions."""
        assert AggregationType.AVG.value == "avg"
        assert AggregationType.MAX.value == "max"
        assert AggregationType.MIN.value == "min"
        assert AggregationType.P50.value == "p50"
        assert AggregationType.P90.value == "p90"
        assert AggregationType.P95.value == "p95"
        assert AggregationType.P99.value == "p99"

    def test_resource_type_all_values(self) -> None:
        """Test all resource type values."""
        assert ResourceType.CPU.value == "cpu"
        assert ResourceType.MEMORY.value == "memory"
        assert ResourceType.STORAGE.value == "storage"
        assert ResourceType.EPHEMERAL_STORAGE.value == "ephemeral-storage"

    def test_optimization_target_all_values(self) -> None:
        """Test all optimization target values."""
        assert OptimizationTarget.BALANCED.value == "balanced"
        assert OptimizationTarget.PERFORMANCE.value == "performance"
        assert OptimizationTarget.COST.value == "cost"

    def test_monitor_metrics_storage(self) -> None:
        """Test internal metrics storage."""
        monitor = K8sResourceMonitor()

        # Check initial state
        assert len(monitor._pod_metrics) == 0
        assert len(monitor._node_metrics) == 0
        assert len(monitor._hpa_metrics) == 0

    def test_hpa_metric_with_all_fields(self) -> None:
        """Test HPA metric with all optional fields."""
        metric = HPAMetric(
            deployment="test-deployment",
            namespace="default",
            metric_type=MetricType.CUSTOM,
            metric_name="custom_metric",
            value=100.0,
            aggregation=AggregationType.P95,
            current_replicas=3,
            target_value=80.0,
            min_replicas=2,
            max_replicas=10,
            window="5m",
        )

        # Test scaling calculation
        desired = metric.calculate_desired_replicas()
        # 100/80 = 1.25, so 3 * 1.25 = 3.75, which rounds down to 3
        assert desired == 3

    def test_container_stats_field_descriptions(self) -> None:
        """Test container stats field descriptions are present."""
        fields = ContainerStats.model_fields

        # Check that fields with descriptions are properly defined
        assert (
            fields["runtime"].description
            == "Container runtime (docker, containerd, cri-o)"
        )
        assert fields["cpu_usage"].description == "CPU usage in millicores"
        assert fields["memory_usage"].description == "Memory usage in bytes"

    def test_prometheus_metrics_lazy_init(self) -> None:
        """Test Prometheus metrics lazy initialization."""
        monitor = K8sResourceMonitor()

        # Initially not initialized
        assert not monitor._prometheus_initialized

        # Setup connection (mocked)
        with patch("k8s_resource_monitor.monitor.config"):
            monitor.core_v1 = MagicMock()
            monitor.apps_v1 = MagicMock()
            monitor.metrics_client = MagicMock()
            monitor.is_connected = True

            # First ensure_connected should initialize Prometheus metrics
            monitor._ensure_connected()
            assert monitor._prometheus_initialized

    def test_empty_string_handling_throughout(self) -> None:
        """Test empty string handling in various methods."""
        monitor = K8sResourceMonitor()

        # Empty CPU string
        assert monitor._parse_cpu_value("") == 0.0
        assert monitor._parse_cpu_value("   ") == 0.0

        # Empty memory string
        assert monitor._parse_memory_value("") == 0
        assert monitor._parse_memory_value("   ") == 0

        # Empty container runtime
        assert monitor._detect_container_runtime("") == "unknown"
        assert monitor._detect_container_runtime("   ") == "unknown"
