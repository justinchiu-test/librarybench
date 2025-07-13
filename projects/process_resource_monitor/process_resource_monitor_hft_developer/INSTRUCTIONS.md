# Process Resource Monitor - High-Frequency Trading Developer Edition

## Overview
You are building a Python-based process resource monitoring library specifically designed for Yuki, an HFT developer optimizing trading algorithms. The library should provide microsecond-precision monitoring of process behavior to understand CPU cache performance and context switching impact on trading latency.

## Core Requirements

### 1. CPU Affinity and Cache Miss Rate Monitoring
- Track L1/L2/L3 cache hit/miss rates per process
- Monitor CPU core affinity and migration events
- Measure cache line bouncing between cores
- Track TLB (Translation Lookaside Buffer) misses
- Identify false sharing in multi-threaded applications

### 2. Context Switch Tracking with Microsecond Precision
- Count voluntary and involuntary context switches
- Measure context switch duration with microsecond accuracy
- Track CPU scheduling latency and run queue depth
- Monitor preemption events and their causes
- Correlate context switches with trading event timestamps

### 3. Interrupt and Softirq Impact Measurement
- Track hardware interrupt frequency and duration
- Monitor softirq processing time per CPU core
- Identify interrupt sources causing latency spikes
- Measure interrupt coalescing effectiveness
- Track deferred interrupt processing impact

### 4. NUMA Node Memory Access Pattern Analysis
- Monitor local vs remote NUMA memory accesses
- Track memory bandwidth usage per NUMA node
- Identify memory allocation hot spots
- Measure inter-socket communication overhead
- Optimize memory placement for latency-critical data

### 5. Real-time Thread Priority and Scheduling Visualization
- Monitor real-time thread scheduling behavior
- Track priority inversions and their duration
- Visualize CPU time distribution among threads
- Measure scheduling jitter for time-critical threads
- Identify priority inheritance chains

## Technical Specifications

### Data Collection
- Use performance counters and hardware monitoring features
- Kernel-level event tracing for microsecond precision
- Direct MSR (Model Specific Register) access where needed
- Lock-free data structures for minimal measurement overhead
- Zero-copy mechanisms for data collection

### API Design
```python
# Example usage
monitor = HFTResourceMonitor()

# Configure ultra-low latency monitoring
monitor.configure(
    sampling_interval_us=100,  # 100 microseconds
    cpu_affinity=[0, 1],       # Pin to specific cores
    realtime_priority=99
)

# Start monitoring trading process
monitor.attach_process(
    pid=trading_pid,
    track_cache=True,
    track_numa=True
)

# Get cache performance metrics
cache_stats = monitor.get_cache_metrics(
    time_window_us=1000,  # Last millisecond
    percentiles=[50, 95, 99, 99.9]
)

# Analyze context switches
context_switches = monitor.get_context_switches(
    include_stack_trace=True,
    min_duration_us=10
)

# Check NUMA efficiency
numa_stats = monitor.get_numa_stats(
    include_heatmap=True,
    resolution="cache_line"
)

# Detect latency spikes
spikes = monitor.detect_latency_spikes(
    threshold_us=50,
    include_cause_analysis=True
)
```

### Testing Requirements
- Microsecond-precision timing validation tests
- Stress tests under high-frequency load
- Hardware counter accuracy verification
- Multi-core scaling and interference tests
- Use pytest with pytest-json-report for test result formatting
- Benchmark against known latency patterns

### Performance Targets
- Sub-microsecond measurement overhead
- Support 1MHz sampling rate for critical metrics
- Process 10 million events per second
- Detect latency spikes within 10 microseconds
- Zero allocation in hot path monitoring code

## Implementation Constraints
- Python 3.8+ compatibility with C extensions for performance
- Use Python standard library plus: psutil, numpy, python-msr
- Critical paths implemented in Cython or C
- Support for Linux perf_events subsystem
- Require CAP_SYS_ADMIN for hardware counter access

## Deliverables
1. Core Python library with C extensions for performance-critical parts
2. Hardware performance counter interface
3. Real-time latency analysis and spike detection
4. NUMA optimization recommendations engine
5. CLI tool for latency investigation and tuning