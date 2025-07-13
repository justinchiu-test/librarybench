# Process Resource Monitor - Scientific Computing Admin Edition

## Overview
You are building a Python-based process resource monitoring library specifically designed for Dr. Patel, a HPC cluster administrator supporting research workloads. The library should ensure fair resource allocation among users and track long-running jobs while preventing resource monopolization.

## Core Requirements

### 1. Job Scheduler Integration for Workload Monitoring
- Integrate with popular job schedulers (SLURM, PBS, LSF, SGE)
- Track job resource allocation vs actual usage
- Monitor job states and queue wait times
- Identify inefficient resource requests
- Support array jobs and job dependencies

### 2. Fair-share Policy Enforcement with Usage Tracking
- Calculate user and group fair-share scores
- Track historical resource usage for fair-share calculations
- Monitor share tree and priority calculations
- Detect users exceeding fair-share allocations
- Generate reports for policy compliance

### 3. GPU Utilization Monitoring for ML Workloads
- Track GPU compute and memory utilization
- Monitor CUDA core usage and tensor core activity
- Identify GPU memory leaks and fragmentation
- Track multi-GPU job efficiency and scaling
- Monitor GPU-CPU data transfer bottlenecks

### 4. Memory Bandwidth Saturation Detection
- Monitor memory bandwidth usage per NUMA node
- Detect memory bandwidth bottlenecks
- Track cache coherency traffic overhead
- Identify memory-bound vs compute-bound processes
- Measure impact of memory bandwidth on job performance

### 5. Inter-process Communication Overhead Analysis
- Monitor MPI communication patterns and overhead
- Track shared memory usage between processes
- Analyze network fabric utilization for distributed jobs
- Identify communication bottlenecks in parallel jobs
- Measure collective operation performance

## Technical Specifications

### Data Collection
- Direct integration with job scheduler APIs and accounting logs
- GPU metrics via NVML/ROCM-SMI libraries
- InfiniBand/OmniPath performance counter access
- Memory bandwidth monitoring via hardware counters
- Process tree tracking for parallel job monitoring

### API Design
```python
# Example usage
monitor = HPCResourceMonitor()

# Connect to job scheduler
monitor.connect_scheduler(
    type="slurm",
    config_file="/etc/slurm/slurm.conf"
)

# Monitor active jobs
job_stats = monitor.get_job_statistics(
    partition="gpu",
    time_window="24h",
    include_efficiency=True
)

# Check fair-share compliance
fairshare = monitor.analyze_fairshare(
    users=["user1", "user2"],
    groups=["physics", "chemistry"],
    include_projections=True
)

# Monitor GPU utilization
gpu_stats = monitor.get_gpu_utilization(
    job_id="12345",
    metrics=["compute", "memory", "power"],
    aggregate_by="node"
)

# Analyze MPI communication
mpi_analysis = monitor.analyze_mpi_overhead(
    job_id="12345",
    include_trace=True,
    identify_hotspots=True
)

# Detect resource waste
waste_report = monitor.identify_resource_waste(
    threshold_efficiency=0.5,
    min_job_duration="1h"
)
```

### Testing Requirements
- Integration tests with job scheduler simulators
- GPU monitoring tests with CUDA/ROCm applications
- MPI communication pattern analysis validation
- Scalability tests with 1000+ concurrent jobs
- Use pytest with pytest-json-report for test result formatting
- Test with various HPC workload patterns

### Performance Targets
- Monitor clusters with 10,000+ cores
- Track 1000+ concurrent jobs with minimal overhead
- Update GPU metrics every second
- Process job accounting data for 100k jobs in <30 seconds
- Generate user reports for 6-month periods in <1 minute

## Implementation Constraints
- Python 3.8+ compatibility required
- Use Python standard library plus: psutil, py-slurm, nvidia-ml-py, mpi4py
- No GUI components - this is a backend library only
- Support multiple job scheduler backends
- Run with minimal privileges (no root required)

## Deliverables
1. Core Python library with multi-scheduler support
2. GPU and accelerator monitoring capabilities
3. Fair-share analysis and reporting tools
4. MPI and communication overhead analyzer
5. CLI tool for cluster utilization reports and user summaries