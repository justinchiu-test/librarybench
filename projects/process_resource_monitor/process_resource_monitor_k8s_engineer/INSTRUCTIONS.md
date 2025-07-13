# Process Resource Monitor - Kubernetes Platform Engineer Edition

## Overview
You are building a Python-based process resource monitoring library specifically designed for Aisha, a platform engineer managing containerized workloads. The library should monitor resource usage within pods and nodes to ensure efficient resource allocation and prevent noisy neighbor problems.

## Core Requirements

### 1. Container-aware Process Monitoring with Namespace Isolation
- Identify processes running within containers vs host processes
- Map processes to Kubernetes pods, containers, and namespaces
- Track cgroup resource limits and actual usage per container
- Monitor container runtime overhead (Docker, containerd, CRI-O)
- Support multi-container pods with shared process namespaces

### 2. Pod Resource Limit Enforcement and Breach Detection
- Monitor CPU and memory usage against configured limits and requests
- Detect when pods approach or exceed resource limits
- Track OOMKilled events and correlate with memory pressure
- Identify pods without resource limits defined
- Calculate resource utilization efficiency (actual vs requested)

### 3. Node Pressure Analysis for Scheduling Optimization
- Monitor node-level resource pressure signals
- Track allocatable vs capacity for CPU, memory, and ephemeral storage
- Identify nodes with high scheduling pressure
- Detect pod eviction risks due to resource pressure
- Analyze resource fragmentation preventing pod scheduling

### 4. Horizontal Pod Autoscaler Metric Generation
- Generate custom metrics for HPA decisions
- Track request rate, response time, and queue depth per pod
- Calculate rolling averages and percentiles for scaling metrics
- Support both resource and custom metric types
- Predict scaling events based on trend analysis

### 5. Resource Quota Utilization Across Namespaces
- Monitor ResourceQuota usage per namespace
- Track quota consumption trends over time
- Alert on approaching quota limits
- Identify unused quota allocations
- Generate namespace resource usage reports

## Technical Specifications

### Data Collection
- Direct integration with Kubernetes API and metrics-server
- Support for Prometheus metrics exposition
- Container runtime API integration for detailed stats
- Real-time event streaming from Kubernetes watch API
- Efficient batch collection to minimize API server load

### API Design
```python
# Example usage
monitor = K8sResourceMonitor()

# Connect to cluster
monitor.connect(
    kubeconfig="/path/to/kubeconfig",
    context="production"
)

# Monitor namespace resources
namespace_stats = monitor.get_namespace_resources(
    namespace="production",
    include_pods=True,
    include_quota=True
)

# Detect resource limit breaches
breaches = monitor.detect_limit_breaches(
    threshold_percent=90,
    time_window="5m"
)

# Analyze node pressure
node_pressure = monitor.analyze_node_pressure(
    include_scheduling_hints=True,
    predict_evictions=True
)

# Generate HPA metrics
hpa_metrics = monitor.generate_hpa_metrics(
    deployment="api-server",
    metric_type="requests_per_second",
    aggregation="p95"
)

# Get resource recommendations
recommendations = monitor.get_resource_recommendations(
    namespace="production",
    optimization_target="balanced"  # or "performance" or "cost"
)
```

### Testing Requirements
- Unit tests with mocked Kubernetes API responses
- Integration tests with kind/minikube clusters
- Chaos testing for pod eviction scenarios
- Load tests with 1000+ pod simulations
- Use pytest with pytest-json-report for test result formatting
- Test against multiple Kubernetes versions

### Performance Targets
- Monitor clusters with up to 5000 pods
- Update metrics within 10 seconds of change
- Process node metrics for 100 nodes in <5 seconds
- Store 24 hours of detailed pod metrics
- Generate namespace reports in <3 seconds

## Implementation Constraints
- Python 3.8+ compatibility required
- Use only Python standard library plus: kubernetes, psutil, prometheus-client
- No GUI components - this is a backend library only
- Support RBAC with minimal required permissions
- Compatible with Kubernetes 1.19+

## Deliverables
1. Core Python library with Kubernetes-native resource monitoring
2. Prometheus metrics exporter for integration
3. Resource recommendation engine based on usage patterns
4. CLI tool for kubectl-style resource investigations
5. Helm chart for deploying as DaemonSet with minimal privileges