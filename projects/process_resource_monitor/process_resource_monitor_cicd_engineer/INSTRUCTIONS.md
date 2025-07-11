# Process Resource Monitor - CI/CD Pipeline Engineer Edition

## Overview
You are building a Python-based process resource monitoring library specifically designed for Roberto, a CI/CD engineer optimizing build farm efficiency. The library should monitor resource usage during builds and tests to identify bottlenecks and optimize pipeline execution times.

## Core Requirements

### 1. Build Job Resource Profiling with Stage Breakdown
- Track resource usage for each pipeline stage (checkout, build, test, deploy)
- Monitor compiler and linker process resource consumption
- Identify resource bottlenecks in multi-stage pipelines
- Track artifact generation and storage I/O impact
- Support various CI systems (Jenkins, GitLab CI, GitHub Actions)

### 2. Parallel Test Execution Resource Optimization
- Monitor test runner process resource usage
- Track test parallelization efficiency
- Identify resource contention in parallel test execution
- Optimize test distribution across available resources
- Detect flaky tests through resource variance analysis

### 3. Docker Layer Caching Impact on Resource Usage
- Monitor Docker daemon resource consumption
- Track layer cache hit rates and miss penalties
- Measure build context transfer overhead
- Analyze multi-stage build resource efficiency
- Identify opportunities for layer optimization

### 4. Build Artifact Storage I/O Pattern Analysis
- Track artifact upload/download I/O patterns
- Monitor storage system impact during builds
- Identify inefficient artifact packaging
- Analyze cache storage utilization
- Optimize artifact retention policies based on usage

### 5. Agent Pool Utilization and Queue Time Metrics
- Monitor build agent resource utilization
- Track job queue depths and wait times
- Identify underutilized agents in the pool
- Predict optimal agent pool sizing
- Analyze job distribution efficiency across agents

## Technical Specifications

### Data Collection
- CI system API integration for job metadata
- Process-level monitoring on build agents
- Docker API integration for container metrics
- Storage system I/O monitoring
- Real-time pipeline execution tracking

### API Design
```python
# Example usage
monitor = CICDResourceMonitor()

# Configure CI system integration
monitor.configure_ci(
    system="jenkins",
    url="https://jenkins.company.com",
    credentials=ci_credentials
)

# Profile build job resources
job_profile = monitor.profile_build_job(
    job_name="backend-service",
    build_number=1234,
    breakdown_by="stage"
)

# Analyze test parallelization
test_analysis = monitor.analyze_test_parallelization(
    job_name="backend-service",
    optimal_parallel_count=True,
    identify_bottlenecks=True
)

# Monitor Docker caching
docker_stats = monitor.get_docker_cache_impact(
    time_range="7d",
    include_recommendations=True,
    group_by="repository"
)

# Analyze artifact I/O
artifact_io = monitor.analyze_artifact_patterns(
    storage_backend="s3",
    identify_optimization=True,
    cost_analysis=True
)

# Get agent pool metrics
pool_metrics = monitor.get_agent_pool_utilization(
    pool_name="linux-builders",
    include_predictions=True,
    recommend_sizing=True
)
```

### Testing Requirements
- Mock CI system API responses for testing
- Simulated build workload testing
- Docker layer caching scenarios
- Agent pool scaling simulations
- Use pytest with pytest-json-report for test result formatting
- Integration tests with CI system sandboxes

### Performance Targets
- Monitor 1000+ concurrent build jobs
- Track resource metrics with 1-second granularity
- Process 10GB/hour of build logs
- Generate optimization reports in <30 seconds
- Support 500+ build agents in a pool

## Implementation Constraints
- Python 3.8+ compatibility required
- Use Python standard library plus: psutil, docker, requests, boto3
- No GUI components - this is a backend library only
- Support major CI/CD platforms
- Minimal impact on build performance (<1% overhead)

## Deliverables
1. Core Python library with CI/CD system integrations
2. Build job resource profiler with stage analysis
3. Test parallelization optimizer
4. Docker build cache analyzer
5. CLI tool for pipeline optimization recommendations