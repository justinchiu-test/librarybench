# K8s Resource Monitor

A Kubernetes-native resource monitoring library designed for platform engineers to monitor resource usage within pods and nodes, ensuring efficient resource allocation and preventing noisy neighbor problems.

## Overview

This library provides comprehensive monitoring capabilities for Kubernetes clusters, including:

- **Container-aware Process Monitoring**: Identify processes running within containers vs host processes with namespace isolation
- **Pod Resource Limit Enforcement**: Detect when pods approach or exceed resource limits
- **Node Pressure Analysis**: Monitor node-level resource pressure for scheduling optimization
- **HPA Metric Generation**: Generate custom metrics for Horizontal Pod Autoscaler decisions
- **Resource Quota Monitoring**: Track ResourceQuota utilization across namespaces
- **Resource Optimization**: Get recommendations for optimal resource allocation

## Installation

```bash
pip install k8s-resource-monitor
```

For development:
```bash
pip install -e ".[dev]"
```

## CLI Usage

The library includes a kubectl-style CLI tool for easy interaction with your cluster:

```bash
# Get namespace resource usage
k8s-monitor namespace production

# Detect resource limit breaches
k8s-monitor breaches --threshold 80

# Analyze node pressure
k8s-monitor nodes

# Get resource recommendations
k8s-monitor recommendations production --target balanced

# Generate HPA metrics
k8s-monitor hpa my-deployment -n production --metric-type requests_per_second
```

### CLI Commands

- `namespace`: Get resource usage for a specific namespace
- `breaches`: Detect pods approaching or exceeding resource limits
- `nodes`: Analyze resource pressure on all nodes
- `recommendations`: Get resource optimization recommendations
- `hpa`: Generate metrics for Horizontal Pod Autoscaler

Use `k8s-monitor --help` for full command documentation.

## Library Usage

### Basic Connection

```python
from k8s_resource_monitor import K8sResourceMonitor

# Create monitor instance
monitor = K8sResourceMonitor()

# Connect to cluster using default kubeconfig
monitor.connect()

# Or connect with specific kubeconfig
monitor.connect(kubeconfig="/path/to/kubeconfig", context="production")
```

### Monitor Namespace Resources

```python
# Get resource usage for a namespace
namespace_stats = monitor.get_namespace_resources(
    namespace="production",
    include_pods=True,
    include_quota=True
)

print(f"Namespace: {namespace_stats.namespace}")
print(f"Total CPU Usage: {namespace_stats.total_cpu_usage}m")
print(f"Total Memory Usage: {namespace_stats.total_memory_usage / (1024**3):.2f}Gi")
print(f"Pod Count: {namespace_stats.pod_count}")

# Check quota utilization
for quota in namespace_stats.quotas:
    print(f"\nQuota: {quota.quota_name}")
    for resource, utilization in quota.utilization.items():
        print(f"  {resource}: {utilization:.1f}%")
```

### Detect Resource Limit Breaches

```python
# Detect pods approaching resource limits
breaches = monitor.detect_limit_breaches(
    threshold_percent=90,
    time_window="5m",
    namespace="production"  # Optional: filter by namespace
)

for breach in breaches:
    print(f"ALERT: {breach.pod_name}/{breach.container_name}")
    print(f"  Resource: {breach.resource_type.value}")
    print(f"  Usage: {breach.breach_percent:.1f}% of limit")
    print(f"  Severity: {breach.severity}")
```

### Analyze Node Pressure

```python
# Analyze resource pressure on nodes
node_pressures = monitor.analyze_node_pressure(
    include_scheduling_hints=True,
    predict_evictions=True
)

for node in node_pressures:
    print(f"\nNode: {node.node_name}")
    print(f"  Scheduling Pressure: {node.scheduling_pressure:.2f}")
    print(f"  Eviction Risk: {node.eviction_risk:.2f}")
    print(f"  Resource Fragmentation: {node.resource_fragmentation:.2f}")
    
    if node.eviction_risk > 0.8:
        print(f"  WARNING: High eviction risk!")
```

### Generate HPA Metrics

```python
# Generate metrics for Horizontal Pod Autoscaler
hpa_metric = monitor.generate_hpa_metrics(
    deployment="api-server",
    namespace="production",
    metric_type="resource",  # or "custom", "requests_per_second", etc.
    aggregation="p95"  # or "avg", "max", "p50", "p90", "p99"
)

print(f"Deployment: {hpa_metric.deployment}")
print(f"Current Replicas: {hpa_metric.current_replicas}")
print(f"Metric Value: {hpa_metric.value}")

# Calculate scaling recommendation
hpa_metric.target_value = 500  # Target CPU millicores per pod
hpa_metric.min_replicas = 2
hpa_metric.max_replicas = 10

desired_replicas = hpa_metric.calculate_desired_replicas()
print(f"Recommended Replicas: {desired_replicas}")
```

### Get Resource Recommendations

```python
# Get optimization recommendations
recommendations = monitor.get_resource_recommendations(
    namespace="production",
    optimization_target="balanced"  # or "performance" or "cost"
)

for rec in recommendations:
    if rec.potential_savings:
        print(f"\n{rec.pod_name}/{rec.container_name}")
        print(f"  Resource: {rec.resource_type.value}")
        print(f"  Current Request: {rec.current_request}")
        print(f"  Recommended Request: {rec.recommended_request}")
        print(f"  Potential Savings: {rec.potential_savings}")
        print(f"  Reason: {rec.reason}")
```

## API Reference

### K8sResourceMonitor

The main class for interacting with Kubernetes resources.

#### Methods

- `connect(kubeconfig=None, context=None)`: Connect to Kubernetes cluster
- `get_namespace_resources(namespace, include_pods=True, include_quota=True)`: Get resource usage for a namespace
- `detect_limit_breaches(threshold_percent=90, time_window="5m", namespace=None)`: Detect resource limit breaches
- `analyze_node_pressure(include_scheduling_hints=True, predict_evictions=True)`: Analyze node resource pressure
- `generate_hpa_metrics(deployment, namespace="default", metric_type="requests_per_second", aggregation="p95")`: Generate HPA metrics
- `get_resource_recommendations(namespace, optimization_target="balanced")`: Get resource optimization recommendations

### Data Models

The library uses Pydantic models for type safety and validation:

- `PodResources`: Pod resource information including containers
- `ContainerStats`: Individual container resource statistics
- `ResourceBreach`: Resource limit breach detection results
- `NodePressure`: Node resource pressure analysis
- `HPAMetric`: Horizontal Pod Autoscaler metrics
- `ResourceQuota`: Namespace resource quota information
- `NamespaceResources`: Aggregated namespace resource statistics
- `ResourceRecommendation`: Resource optimization recommendations

## Running Tests

Install development dependencies:
```bash
pip install -e ".[dev]"
```

Run all tests:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=k8s_resource_monitor
```

Generate JSON test report:
```bash
pytest --json-report --json-report-file=pytest_results.json
```

## Performance Considerations

The library is designed to handle:
- Clusters with up to 5000 pods
- Update metrics within 10 seconds of change
- Process node metrics for 100 nodes in <5 seconds
- Store 24 hours of detailed pod metrics
- Generate namespace reports in <3 seconds

## Requirements

- Python 3.8+
- Kubernetes 1.19+
- Dependencies:
  - kubernetes>=28.1.0
  - psutil>=5.9.0
  - prometheus-client>=0.19.0

## License

This project is licensed under the MIT License.