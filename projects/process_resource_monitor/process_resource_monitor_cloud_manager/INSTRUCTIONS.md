# Process Resource Monitor - Cloud Infrastructure Manager Edition

## Overview
You are building a Python-based process resource monitoring library specifically designed for Carlos, a cloud infrastructure manager overseeing hundreds of virtual machines. The library should help identify cost optimization opportunities through aggregate resource usage analysis across VM fleets to right-size instances and reduce cloud spending.

## Core Requirements

### 1. Multi-host Resource Aggregation with Fleet-wide Statistics
- Implement a system to collect and aggregate resource metrics from multiple hosts simultaneously
- Calculate fleet-wide statistics including mean, median, p95, and p99 resource usage
- Support clustering and grouping of hosts by tags, regions, or instance types
- Provide time-series aggregation for trend analysis over days/weeks/months

### 2. Cloud Instance Right-sizing Recommendations
- Analyze historical resource usage patterns to identify over-provisioned instances
- Generate recommendations for optimal instance types based on actual usage
- Calculate potential cost savings from right-sizing actions
- Identify instances consistently using less than 20% of allocated resources

### 3. Cost Projection Modeling
- Integrate with cloud provider pricing APIs to fetch current instance costs
- Model cost implications of different instance type migrations
- Project monthly/annual savings from recommended optimizations
- Support multi-cloud cost comparison (AWS, GCP, Azure)

### 4. Idle Resource Detection
- Implement algorithms to detect consistently idle or underutilized resources
- Define customizable idle thresholds for CPU, memory, network, and disk
- Generate automated shutdown candidates based on usage patterns
- Track resource wake/sleep cycles for better idle detection

### 5. Resource Usage Chargeback Reporting
- Attribute resource consumption to specific departments, projects, or cost centers
- Generate detailed chargeback reports with customizable billing periods
- Support tag-based resource allocation and cost distribution
- Export reports in multiple formats (CSV, JSON, PDF)

## Technical Specifications

### Data Collection
- Poll system resource metrics at configurable intervals (default: 60 seconds)
- Support both agent-based and agentless collection methods
- Implement efficient data compression for metric storage
- Handle network failures gracefully with local buffering

### API Design
```python
# Example usage
monitor = CloudResourceMonitor()
monitor.add_host("vm-prod-001", tags={"dept": "engineering", "env": "prod"})
monitor.add_host("vm-prod-002", tags={"dept": "engineering", "env": "prod"})

# Get fleet-wide statistics
stats = monitor.get_fleet_statistics(
    metric="cpu_usage",
    time_range="7d",
    groupby="dept"
)

# Get right-sizing recommendations
recommendations = monitor.get_rightsizing_recommendations(
    cost_threshold=0.20,  # 20% potential savings
    confidence=0.95
)

# Generate chargeback report
report = monitor.generate_chargeback_report(
    start_date="2024-01-01",
    end_date="2024-01-31",
    groupby="dept"
)
```

### Testing Requirements
- Comprehensive unit tests with >80% code coverage
- Integration tests simulating multi-host environments
- Performance tests ensuring sub-second response times for fleet queries
- Use pytest with pytest-json-report for test result formatting
- Mock cloud provider APIs for cost calculation tests

### Performance Targets
- Support monitoring up to 1000 hosts concurrently
- Process and aggregate metrics within 5 seconds for 100 hosts
- Store 90 days of metrics with <1GB storage per host
- Generate reports for 30-day periods in under 10 seconds

## Implementation Constraints
- Python 3.8+ compatibility required
- Use only Python standard library plus: psutil, requests, pandas, numpy
- No GUI components - this is a backend library only
- All user interaction through Python API or CLI commands
- Configuration via YAML/JSON files, not hardcoded values

## Deliverables
1. Core Python library with all five key features implemented
2. Comprehensive test suite with pytest-json-report output
3. CLI tool for common operations (status checks, report generation)
4. Example scripts demonstrating typical usage patterns
5. Performance benchmarking results showing adherence to targets