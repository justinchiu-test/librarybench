# Memory Profiler Tool - DevOps Manager Rachel Instructions

You are tasked with implementing a memory profiler tool specifically designed for Rachel, a DevOps manager monitoring production services who needs to prevent memory-related outages. She wants automated memory leak detection and alerting integrated with existing monitoring infrastructure.

## Core Requirements

### 1. Prometheus/Grafana integration for memory metrics export
- Export memory metrics in Prometheus format
- Support custom metric labels and dimensions
- Provide metric aggregation and sampling
- Include memory trend calculations
- Enable metric push gateway support

### 2. Anomaly detection with ML-based memory pattern analysis
- Implement statistical anomaly detection algorithms
- Detect memory usage pattern deviations
- Learn baseline memory behavior automatically
- Identify seasonal and cyclical patterns
- Generate anomaly severity scores

### 3. Automated memory leak reporting with root cause analysis
- Detect gradual memory growth patterns
- Identify leak sources with stack traces
- Calculate leak rates and impact projections
- Generate actionable leak reports
- Prioritize leaks by severity and impact

### 4. Kubernetes pod memory optimization recommendations
- Analyze pod memory usage patterns
- Recommend optimal memory limits and requests
- Identify over-provisioned pods
- Suggest pod autoscaling configurations
- Calculate memory efficiency scores

### 5. Memory usage forecasting for capacity planning
- Predict future memory requirements
- Model growth trends and patterns
- Generate capacity planning reports
- Identify resource exhaustion timelines
- Support what-if scenario analysis

## Implementation Guidelines

- Use Python exclusively for all implementations
- No UI components - focus on programmatic APIs and CLI tools
- All output should be text-based (JSON, CSV, or formatted text)
- Design for production environment compatibility
- Ensure minimal performance overhead

## Testing Requirements

All tests must be written using pytest and follow these guidelines:
- Generate detailed test reports using pytest-json-report
- Test integration with monitoring systems
- Validate anomaly detection accuracy
- Test with production-like data volumes
- Ensure reliability under high load

## Project Structure

```
memory_profiler_tool_devops_manager/
├── src/
│   ├── __init__.py
│   ├── prometheus_exporter.py    # Metrics export functionality
│   ├── anomaly_detector.py       # ML-based anomaly detection
│   ├── leak_analyzer.py          # Memory leak detection
│   ├── k8s_optimizer.py          # Kubernetes optimization
│   └── forecaster.py             # Capacity planning
├── tests/
│   ├── __init__.py
│   ├── test_prometheus_exporter.py
│   ├── test_anomaly_detector.py
│   ├── test_leak_analyzer.py
│   ├── test_k8s_optimizer.py
│   └── test_forecaster.py
├── requirements.txt
└── README.md
```

Remember: This tool must integrate seamlessly with existing DevOps infrastructure and provide actionable insights for preventing memory-related incidents in production environments.