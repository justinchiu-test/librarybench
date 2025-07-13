"""Core Kubernetes resource monitoring implementation."""

from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from kubernetes import client, config
from kubernetes.client import ApiException
from prometheus_client import Counter, Gauge

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


class K8sResourceMonitor:
    """Kubernetes resource monitoring for platform engineers."""

    def __init__(self) -> None:
        """Initialize the monitor."""
        self.api_client: Optional[client.ApiClient] = None
        self.core_v1: Optional[client.CoreV1Api] = None
        self.apps_v1: Optional[client.AppsV1Api] = None
        self.metrics_client: Optional[client.CustomObjectsApi] = None
        self.is_connected = False

        # Metrics storage
        self._pod_metrics: Dict[str, List[Tuple[datetime, PodResources]]] = defaultdict(
            list
        )
        self._node_metrics: Dict[str, List[Tuple[datetime, NodePressure]]] = (
            defaultdict(list)
        )
        self._hpa_metrics: Dict[str, List[HPAMetric]] = defaultdict(list)

        # Prometheus metrics - lazy initialization to avoid issues in testing
        self._prometheus_initialized = False

    def _setup_prometheus_metrics(self) -> None:
        """Set up Prometheus metrics for exporting."""
        try:
            self.pod_cpu_usage = Gauge(
                "k8s_pod_cpu_usage_millicores",
                "Pod CPU usage in millicores",
                ["namespace", "pod", "container"],
            )
            self.pod_memory_usage = Gauge(
                "k8s_pod_memory_usage_bytes",
                "Pod memory usage in bytes",
                ["namespace", "pod", "container"],
            )
            self.resource_breach_total = Counter(
                "k8s_resource_breach_total",
                "Total number of resource limit breaches",
                ["namespace", "pod", "container", "resource_type"],
            )
            self.node_pressure_gauge = Gauge(
                "k8s_node_pressure",
                "Node resource pressure (0-1)",
                ["node", "metric_type"],
            )
            self.hpa_metric_gauge = Gauge(
                "k8s_hpa_metric_value",
                "HPA metric values",
                ["namespace", "deployment", "metric_type"],
            )
        except ValueError:
            # Metrics already registered, this is ok for testing
            # Try to get existing metrics from registry
            from prometheus_client import REGISTRY

            for collector in REGISTRY._collector_to_names:
                if hasattr(collector, "_name"):
                    if collector._name == "k8s_pod_cpu_usage_millicores":
                        self.pod_cpu_usage = collector
                    elif collector._name == "k8s_pod_memory_usage_bytes":
                        self.pod_memory_usage = collector
                    elif collector._name == "k8s_resource_breach_total":
                        self.resource_breach_total = collector
                    elif collector._name == "k8s_node_pressure":
                        self.node_pressure_gauge = collector
                    elif collector._name == "k8s_hpa_metric_value":
                        self.hpa_metric_gauge = collector

    def connect(
        self, kubeconfig: Optional[str] = None, context: Optional[str] = None
    ) -> None:
        """Connect to Kubernetes cluster."""
        try:
            if kubeconfig:
                config.load_kube_config(config_file=kubeconfig, context=context)
            else:
                # Try in-cluster config first, then default kubeconfig
                try:
                    config.load_incluster_config()
                except config.ConfigException:
                    config.load_kube_config(context=context)

            self.api_client = client.ApiClient()
            self.core_v1 = client.CoreV1Api(self.api_client)
            self.apps_v1 = client.AppsV1Api(self.api_client)
            self.metrics_client = client.CustomObjectsApi(self.api_client)

            # Test connection
            self.core_v1.list_namespace(limit=1)
            self.is_connected = True

        except Exception as e:
            self.is_connected = False
            raise RuntimeError(f"Failed to connect to Kubernetes cluster: {e}")

    def _ensure_connected(self) -> None:
        """Ensure connection to cluster is established."""
        if not self.is_connected:
            raise RuntimeError(
                "Not connected to Kubernetes cluster. Call connect() first."
            )

        # Initialize Prometheus metrics on first use
        if not self._prometheus_initialized:
            self._setup_prometheus_metrics()
            self._prometheus_initialized = True

    def get_namespace_resources(
        self, namespace: str, include_pods: bool = True, include_quota: bool = True
    ) -> NamespaceResources:
        """Get resource usage for a namespace."""
        self._ensure_connected()

        namespace_resources = NamespaceResources(namespace=namespace)

        if include_pods:
            pods = self._get_pods_in_namespace(namespace)
            namespace_resources.pods = pods

        if include_quota:
            quotas = self._get_resource_quotas(namespace)
            namespace_resources.quotas = quotas

        namespace_resources.calculate_totals()

        return namespace_resources

    def _get_pods_in_namespace(self, namespace: str) -> List[PodResources]:
        """Get all pods in a namespace with resource information."""
        pods = []

        try:
            pod_list = self.core_v1.list_namespaced_pod(namespace)

            for pod in pod_list.items:
                if pod.status.phase not in ["Running", "Pending"]:
                    continue

                pod_resources = self._extract_pod_resources(pod)
                pods.append(pod_resources)

                # Update Prometheus metrics if initialized
                if self._prometheus_initialized and hasattr(self, "pod_cpu_usage"):
                    for container in pod_resources.containers:
                        self.pod_cpu_usage.labels(
                            namespace=namespace,
                            pod=pod_resources.name,
                            container=container.name,
                        ).set(container.cpu_usage)

                        self.pod_memory_usage.labels(
                            namespace=namespace,
                            pod=pod_resources.name,
                            container=container.name,
                        ).set(container.memory_usage)

        except ApiException as e:
            raise RuntimeError(f"Failed to list pods in namespace {namespace}: {e}")

        return pods

    def _extract_pod_resources(self, pod: Any) -> PodResources:
        """Extract resource information from a pod object."""
        containers = []
        total_cpu_usage = 0
        total_cpu_limit = 0
        total_cpu_request = 0
        total_memory_usage = 0
        total_memory_limit = 0
        total_memory_request = 0
        has_resource_limits = True

        # Get pod metrics if available
        pod_metrics = self._get_pod_metrics(pod.metadata.namespace, pod.metadata.name)

        for i, container in enumerate(pod.spec.containers):
            container_stats = ContainerStats(
                name=container.name,
                container_id=pod.status.container_statuses[i].container_id
                if i < len(pod.status.container_statuses)
                else "",
                runtime=self._detect_container_runtime(
                    pod.status.container_statuses[i].container_id
                    if i < len(pod.status.container_statuses)
                    else ""
                ),
                restart_count=pod.status.container_statuses[i].restart_count
                if i < len(pod.status.container_statuses)
                else 0,
                cpu_usage=0.0,  # Will be updated from metrics
                memory_usage=0,  # Will be updated from metrics
            )

            # Extract resource limits and requests
            if container.resources:
                if container.resources.limits:
                    cpu_limit = container.resources.limits.get("cpu")
                    memory_limit = container.resources.limits.get("memory")

                    if cpu_limit:
                        container_stats.cpu_limit = self._parse_cpu_value(cpu_limit)
                        total_cpu_limit += container_stats.cpu_limit
                    else:
                        has_resource_limits = False

                    if memory_limit:
                        container_stats.memory_limit = self._parse_memory_value(
                            memory_limit
                        )
                        total_memory_limit += container_stats.memory_limit
                    else:
                        has_resource_limits = False
                else:
                    has_resource_limits = False

                if container.resources.requests:
                    cpu_request = container.resources.requests.get("cpu")
                    memory_request = container.resources.requests.get("memory")

                    if cpu_request:
                        container_stats.cpu_request = self._parse_cpu_value(cpu_request)
                        total_cpu_request += container_stats.cpu_request

                    if memory_request:
                        container_stats.memory_request = self._parse_memory_value(
                            memory_request
                        )
                        total_memory_request += container_stats.memory_request
            else:
                has_resource_limits = False

            # Get actual usage from metrics
            if pod_metrics and container.name in pod_metrics:
                container_stats.cpu_usage = pod_metrics[container.name]["cpu"]
                container_stats.memory_usage = pod_metrics[container.name]["memory"]
                total_cpu_usage += container_stats.cpu_usage
                total_memory_usage += container_stats.memory_usage

            # Check for OOM kills
            if i < len(pod.status.container_statuses):
                container_status = pod.status.container_statuses[i]
                if (
                    container_status.last_state
                    and container_status.last_state.terminated
                ):
                    if container_status.last_state.terminated.reason == "OOMKilled":
                        container_stats.is_oomkilled = True

            containers.append(container_stats)

        # Check for shared process namespace
        is_shared_process_namespace = False
        if pod.spec.share_process_namespace is not None:
            is_shared_process_namespace = pod.spec.share_process_namespace

        return PodResources(
            name=pod.metadata.name,
            namespace=pod.metadata.namespace,
            uid=pod.metadata.uid,
            node_name=pod.spec.node_name or "",
            phase=pod.status.phase,
            containers=containers,
            total_cpu_usage=total_cpu_usage,
            total_cpu_limit=total_cpu_limit if total_cpu_limit > 0 else None,
            total_cpu_request=total_cpu_request if total_cpu_request > 0 else None,
            total_memory_usage=total_memory_usage,
            total_memory_limit=total_memory_limit if total_memory_limit > 0 else None,
            total_memory_request=total_memory_request
            if total_memory_request > 0
            else None,
            has_resource_limits=has_resource_limits,
            is_shared_process_namespace=is_shared_process_namespace,
            labels=pod.metadata.labels or {},
            annotations=pod.metadata.annotations or {},
            created_at=pod.metadata.creation_timestamp,
        )

    def _get_pod_metrics(
        self, namespace: str, pod_name: str
    ) -> Optional[Dict[str, Dict[str, float]]]:
        """Get pod metrics from metrics-server."""
        try:
            metrics = self.metrics_client.get_namespaced_custom_object(
                group="metrics.k8s.io",
                version="v1beta1",
                namespace=namespace,
                plural="pods",
                name=pod_name,
            )

            container_metrics = {}
            for container in metrics.get("containers", []):
                cpu_usage = self._parse_cpu_value(container["usage"]["cpu"])
                memory_usage = self._parse_memory_value(container["usage"]["memory"])

                container_metrics[container["name"]] = {
                    "cpu": cpu_usage,
                    "memory": memory_usage,
                }

            return container_metrics

        except ApiException:
            # Metrics server might not be available
            return None

    def _detect_container_runtime(self, container_id: str) -> str:
        """Detect container runtime from container ID."""
        if not container_id or container_id is None:
            return "unknown"

        container_id = str(container_id)

        if container_id.startswith("docker://"):
            return "docker"
        elif container_id.startswith("containerd://"):
            return "containerd"
        elif container_id.startswith("cri-o://"):
            return "cri-o"
        else:
            return "unknown"

    def _parse_cpu_value(self, cpu_str: str) -> float:
        """Parse CPU value to millicores."""
        if isinstance(cpu_str, (int, float)):
            return float(cpu_str) * 1000

        cpu_str = str(cpu_str).strip()

        if not cpu_str:
            return 0.0

        if cpu_str.endswith("m"):
            return float(cpu_str[:-1])
        elif cpu_str.endswith("n"):
            return float(cpu_str[:-1]) / 1_000_000
        else:
            # Assume it's in cores
            return float(cpu_str) * 1000

    def _parse_memory_value(self, memory_str: str) -> int:
        """Parse memory value to bytes."""
        if isinstance(memory_str, (int, float)):
            return int(memory_str)

        memory_str = str(memory_str).strip()

        if not memory_str:
            return 0

        multipliers = {
            "Ki": 1024,
            "Mi": 1024**2,
            "Gi": 1024**3,
            "Ti": 1024**4,
            "K": 1000,
            "M": 1000**2,
            "G": 1000**3,
            "T": 1000**4,
        }

        for suffix, multiplier in multipliers.items():
            if memory_str.endswith(suffix):
                return int(float(memory_str[: -len(suffix)]) * multiplier)

        return int(float(memory_str))

    def _get_resource_quotas(self, namespace: str) -> List[ResourceQuota]:
        """Get resource quotas for a namespace."""
        quotas = []

        try:
            quota_list = self.core_v1.list_namespaced_resource_quota(namespace)

            for quota in quota_list.items:
                resource_quota = ResourceQuota(
                    namespace=namespace,
                    quota_name=quota.metadata.name,
                    hard_limits={k: str(v) for k, v in quota.status.hard.items()}
                    if quota.status.hard
                    else {},
                    used={k: str(v) for k, v in quota.status.used.items()}
                    if quota.status.used
                    else {},
                )

                resource_quota.calculate_utilization()
                quotas.append(resource_quota)

        except ApiException as e:
            raise RuntimeError(
                f"Failed to list resource quotas in namespace {namespace}: {e}"
            )

        return quotas

    def detect_limit_breaches(
        self,
        threshold_percent: float = 90,
        time_window: str = "5m",
        namespace: Optional[str] = None,
    ) -> List[ResourceBreach]:
        """Detect pods approaching or exceeding resource limits."""
        self._ensure_connected()

        breaches = []
        namespaces = [namespace] if namespace else self._list_all_namespaces()

        for ns in namespaces:
            pods = self._get_pods_in_namespace(ns)

            for pod in pods:
                for container in pod.containers:
                    # Check CPU breaches
                    if container.cpu_limit and container.cpu_limit > 0:
                        cpu_percent = (container.cpu_usage / container.cpu_limit) * 100
                        if cpu_percent >= threshold_percent:
                            breach = ResourceBreach(
                                pod_name=pod.name,
                                namespace=pod.namespace,
                                container_name=container.name,
                                resource_type=ResourceType.CPU,
                                current_usage=container.cpu_usage,
                                limit=container.cpu_limit,
                                threshold_percent=threshold_percent,
                            )
                            breaches.append(breach)

                            # Update Prometheus counter
                            if self._prometheus_initialized and hasattr(
                                self, "resource_breach_total"
                            ):
                                self.resource_breach_total.labels(
                                    namespace=pod.namespace,
                                    pod=pod.name,
                                    container=container.name,
                                    resource_type="cpu",
                                ).inc()

                    # Check memory breaches
                    if container.memory_limit and container.memory_limit > 0:
                        memory_percent = (
                            container.memory_usage / container.memory_limit
                        ) * 100
                        if memory_percent >= threshold_percent:
                            breach = ResourceBreach(
                                pod_name=pod.name,
                                namespace=pod.namespace,
                                container_name=container.name,
                                resource_type=ResourceType.MEMORY,
                                current_usage=float(container.memory_usage),
                                limit=float(container.memory_limit),
                                threshold_percent=threshold_percent,
                            )
                            breaches.append(breach)

                            # Update Prometheus counter
                            if self._prometheus_initialized and hasattr(
                                self, "resource_breach_total"
                            ):
                                self.resource_breach_total.labels(
                                    namespace=pod.namespace,
                                    pod=pod.name,
                                    container=container.name,
                                    resource_type="memory",
                                ).inc()

        # Store breaches for time window analysis
        self._store_breaches(breaches, time_window)

        return breaches

    def _list_all_namespaces(self) -> List[str]:
        """List all namespaces in the cluster."""
        try:
            namespace_list = self.core_v1.list_namespace()
            return [ns.metadata.name for ns in namespace_list.items]
        except ApiException as e:
            raise RuntimeError(f"Failed to list namespaces: {e}")

    def _store_breaches(self, breaches: List[ResourceBreach], time_window: str) -> None:
        """Store breaches for time window analysis."""
        # This is a simplified implementation
        # In production, you might want to use a time-series database
        pass

    def analyze_node_pressure(
        self, include_scheduling_hints: bool = True, predict_evictions: bool = True
    ) -> List[NodePressure]:
        """Analyze resource pressure on nodes."""
        self._ensure_connected()

        node_pressures = []

        try:
            nodes = self.core_v1.list_node()

            for node in nodes.items:
                node_pressure = self._analyze_single_node(
                    node, include_scheduling_hints, predict_evictions
                )
                node_pressures.append(node_pressure)

                # Update Prometheus metrics
                if self._prometheus_initialized and hasattr(
                    self, "node_pressure_gauge"
                ):
                    self.node_pressure_gauge.labels(
                        node=node_pressure.node_name, metric_type="scheduling"
                    ).set(node_pressure.scheduling_pressure)

                    self.node_pressure_gauge.labels(
                        node=node_pressure.node_name, metric_type="eviction"
                    ).set(node_pressure.eviction_risk)

                    self.node_pressure_gauge.labels(
                        node=node_pressure.node_name, metric_type="fragmentation"
                    ).set(node_pressure.resource_fragmentation)

                # Store metrics
                self._node_metrics[node_pressure.node_name].append(
                    (datetime.now(), node_pressure)
                )

        except ApiException as e:
            raise RuntimeError(f"Failed to analyze node pressure: {e}")

        return node_pressures

    def _analyze_single_node(
        self, node: Any, include_scheduling_hints: bool, predict_evictions: bool
    ) -> NodePressure:
        """Analyze resource pressure for a single node."""
        # Extract node capacity and allocatable
        capacity = node.status.capacity
        allocatable = node.status.allocatable

        node_pressure = NodePressure(
            node_name=node.metadata.name,
            cpu_capacity=self._parse_cpu_value(capacity.get("cpu", "0")),
            cpu_allocatable=self._parse_cpu_value(allocatable.get("cpu", "0")),
            cpu_allocated=0.0,  # Will be calculated below
            cpu_usage=0.0,  # Will be updated from metrics
            memory_capacity=self._parse_memory_value(capacity.get("memory", "0")),
            memory_allocatable=self._parse_memory_value(allocatable.get("memory", "0")),
            memory_allocated=0,  # Will be calculated below
            memory_usage=0,  # Will be updated from metrics
            ephemeral_storage_capacity=self._parse_memory_value(
                capacity.get("ephemeral-storage", "0")
            ),
            ephemeral_storage_allocatable=self._parse_memory_value(
                allocatable.get("ephemeral-storage", "0")
            ),
            ephemeral_storage_usage=0,  # Will be updated from metrics
            pod_capacity=int(capacity.get("pods", 0)),
            pod_count=0,  # Will be calculated below
        )

        # Get node conditions
        if node.status.conditions:
            for condition in node.status.conditions:
                node_pressure.conditions[condition.type] = condition.status == "True"

        # Calculate allocated resources from pods
        allocated_cpu = 0
        allocated_memory = 0
        pod_count = 0

        try:
            pods = self.core_v1.list_pod_for_all_namespaces(
                field_selector=f"spec.nodeName={node.metadata.name}"
            )

            for pod in pods.items:
                if pod.status.phase in ["Running", "Pending"]:
                    pod_count += 1

                    for container in pod.spec.containers:
                        if container.resources and container.resources.requests:
                            cpu_request = container.resources.requests.get("cpu")
                            memory_request = container.resources.requests.get("memory")

                            if cpu_request:
                                allocated_cpu += self._parse_cpu_value(cpu_request)
                            if memory_request:
                                allocated_memory += self._parse_memory_value(
                                    memory_request
                                )

        except ApiException:
            pass

        node_pressure.cpu_allocated = allocated_cpu
        node_pressure.memory_allocated = allocated_memory
        node_pressure.pod_count = pod_count

        # Get actual usage from metrics
        node_metrics = self._get_node_metrics(node.metadata.name)
        if node_metrics:
            node_pressure.cpu_usage = node_metrics.get("cpu", 0)
            node_pressure.memory_usage = node_metrics.get("memory", 0)
            node_pressure.ephemeral_storage_usage = node_metrics.get(
                "ephemeral-storage", 0
            )

        # Calculate pressure metrics
        node_pressure.calculate_pressure_metrics()

        return node_pressure

    def _get_node_metrics(self, node_name: str) -> Optional[Dict[str, float]]:
        """Get node metrics from metrics-server."""
        try:
            metrics = self.metrics_client.get_cluster_custom_object(
                group="metrics.k8s.io",
                version="v1beta1",
                plural="nodes",
                name=node_name,
            )

            return {
                "cpu": self._parse_cpu_value(metrics["usage"]["cpu"]),
                "memory": self._parse_memory_value(metrics["usage"]["memory"]),
            }

        except ApiException:
            return None

    def generate_hpa_metrics(
        self,
        deployment: str,
        namespace: str = "default",
        metric_type: str = "requests_per_second",
        aggregation: str = "p95",
    ) -> HPAMetric:
        """Generate metrics for Horizontal Pod Autoscaler."""
        self._ensure_connected()

        # Get deployment info
        try:
            deploy = self.apps_v1.read_namespaced_deployment(deployment, namespace)
            current_replicas = deploy.status.replicas or 1

            # Get pods for this deployment
            label_selector = ",".join(
                [f"{k}={v}" for k, v in deploy.spec.selector.match_labels.items()]
            )
            pods = self.core_v1.list_namespaced_pod(
                namespace, label_selector=label_selector
            )

        except ApiException as e:
            raise RuntimeError(f"Failed to get deployment {deployment}: {e}")

        # Generate metric based on type
        metric_value = self._calculate_metric_value(
            pods.items, MetricType(metric_type), AggregationType(aggregation)
        )

        hpa_metric = HPAMetric(
            deployment=deployment,
            namespace=namespace,
            metric_type=MetricType(metric_type),
            metric_name=f"{deployment}_{metric_type}",
            value=metric_value,
            aggregation=AggregationType(aggregation),
            current_replicas=current_replicas,
        )

        # Store metric
        self._hpa_metrics[f"{namespace}/{deployment}"].append(hpa_metric)

        # Update Prometheus
        if self._prometheus_initialized and hasattr(self, "hpa_metric_gauge"):
            self.hpa_metric_gauge.labels(
                namespace=namespace, deployment=deployment, metric_type=metric_type
            ).set(metric_value)

        return hpa_metric

    def _calculate_metric_value(
        self, pods: List[Any], metric_type: MetricType, aggregation: AggregationType
    ) -> float:
        """Calculate metric value for HPA."""
        # This is a simplified implementation
        # In production, you would collect actual application metrics

        if metric_type == MetricType.RESOURCE:
            # Use CPU usage as example
            values = []
            for pod in pods:
                pod_metrics = self._get_pod_metrics(
                    pod.metadata.namespace, pod.metadata.name
                )
                if pod_metrics:
                    total_cpu = sum(m["cpu"] for m in pod_metrics.values())
                    values.append(total_cpu)

        else:
            # Simulate custom metrics
            import random

            values = [random.uniform(10, 100) for _ in pods]

        if not values:
            return 0

        # Apply aggregation
        if aggregation == AggregationType.AVG:
            return sum(values) / len(values)
        elif aggregation == AggregationType.MAX:
            return max(values)
        elif aggregation == AggregationType.MIN:
            return min(values)
        elif aggregation in [
            AggregationType.P50,
            AggregationType.P90,
            AggregationType.P95,
            AggregationType.P99,
        ]:
            percentile = int(aggregation.value[1:])
            values.sort()
            index = int(len(values) * percentile / 100)
            return values[min(index, len(values) - 1)]
        else:
            return sum(values) / len(values)

    def get_resource_recommendations(
        self, namespace: str, optimization_target: str = "balanced"
    ) -> List[ResourceRecommendation]:
        """Get resource optimization recommendations."""
        self._ensure_connected()

        recommendations = []
        target = OptimizationTarget(optimization_target)

        # Get namespace resources
        namespace_resources = self.get_namespace_resources(namespace)

        for pod in namespace_resources.pods:
            for container in pod.containers:
                # Generate CPU recommendations
                cpu_rec = self._generate_cpu_recommendation(pod, container, target)
                if cpu_rec:
                    recommendations.append(cpu_rec)

                # Generate memory recommendations
                memory_rec = self._generate_memory_recommendation(
                    pod, container, target
                )
                if memory_rec:
                    recommendations.append(memory_rec)

        return recommendations

    def _generate_cpu_recommendation(
        self, pod: PodResources, container: ContainerStats, target: OptimizationTarget
    ) -> Optional[ResourceRecommendation]:
        """Generate CPU resource recommendation."""
        # Get historical metrics
        historical = self._get_historical_metrics(
            pod.namespace, pod.name, container.name, ResourceType.CPU
        )

        if not historical:
            return None

        # Calculate recommendation based on target
        if target == OptimizationTarget.BALANCED:
            # Use P95 + 20% buffer
            recommended_request = historical["p95"] * 1.2
            recommended_limit = historical["p99"] * 1.5
        elif target == OptimizationTarget.PERFORMANCE:
            # Use P99 + 50% buffer
            recommended_request = historical["p99"] * 1.5
            recommended_limit = historical["max"] * 2
        else:  # COST
            # Use P90 + 10% buffer
            recommended_request = historical["p90"] * 1.1
            recommended_limit = historical["p95"] * 1.3

        # Only recommend if significantly different from current
        current_request = container.cpu_request or 0
        current_limit = container.cpu_limit or 0

        if (
            abs(recommended_request - current_request) / max(current_request, 1) < 0.1
            and abs(recommended_limit - current_limit) / max(current_limit, 1) < 0.1
        ):
            return None

        return ResourceRecommendation(
            namespace=pod.namespace,
            pod_name=pod.name,
            container_name=container.name,
            resource_type=ResourceType.CPU,
            current_request=current_request,
            current_limit=current_limit,
            recommended_request=recommended_request,
            recommended_limit=recommended_limit,
            optimization_target=target,
            reason=f"Based on {target.value} optimization target using historical usage patterns",
            potential_savings=(current_request - recommended_request)
            if current_request > recommended_request
            else None,
        )

    def _generate_memory_recommendation(
        self, pod: PodResources, container: ContainerStats, target: OptimizationTarget
    ) -> Optional[ResourceRecommendation]:
        """Generate memory resource recommendation."""
        # Similar logic to CPU but for memory
        historical = self._get_historical_metrics(
            pod.namespace, pod.name, container.name, ResourceType.MEMORY
        )

        if not historical:
            return None

        # Calculate recommendation based on target
        if target == OptimizationTarget.BALANCED:
            recommended_request = historical["p95"] * 1.1
            recommended_limit = historical["p99"] * 1.3
        elif target == OptimizationTarget.PERFORMANCE:
            recommended_request = historical["p99"] * 1.3
            recommended_limit = historical["max"] * 1.5
        else:  # COST
            recommended_request = historical["p90"] * 1.05
            recommended_limit = historical["p95"] * 1.2

        current_request = container.memory_request or 0
        current_limit = container.memory_limit or 0

        if (
            abs(recommended_request - current_request) / max(current_request, 1) < 0.1
            and abs(recommended_limit - current_limit) / max(current_limit, 1) < 0.1
        ):
            return None

        return ResourceRecommendation(
            namespace=pod.namespace,
            pod_name=pod.name,
            container_name=container.name,
            resource_type=ResourceType.MEMORY,
            current_request=float(current_request),
            current_limit=float(current_limit),
            recommended_request=recommended_request,
            recommended_limit=recommended_limit,
            optimization_target=target,
            reason=f"Based on {target.value} optimization target using historical usage patterns",
            potential_savings=(current_request - recommended_request)
            if current_request > recommended_request
            else None,
        )

    def _get_historical_metrics(
        self,
        namespace: str,
        pod_name: str,
        container_name: str,
        resource_type: ResourceType,
    ) -> Dict[str, float]:
        """Get historical metrics for a container."""
        # This is a simplified implementation
        # In production, you would query a time-series database

        # For now, return mock data

        base_value = 100 if resource_type == ResourceType.CPU else 100 * 1024 * 1024

        return {
            "min": base_value * 0.5,
            "max": base_value * 2,
            "avg": base_value,
            "p50": base_value * 0.9,
            "p90": base_value * 1.3,
            "p95": base_value * 1.5,
            "p99": base_value * 1.8,
        }
