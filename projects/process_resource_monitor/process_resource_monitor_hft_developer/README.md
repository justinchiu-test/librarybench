# HFT Resource Monitor

A high-performance Python library for monitoring process resources with microsecond precision, designed specifically for high-frequency trading (HFT) applications. This library provides detailed insights into CPU cache performance, context switching, NUMA memory access patterns, and latency spikes.

## Features

- **CPU Cache Monitoring**: Track L1/L2/L3 cache hit/miss rates, TLB misses, and false sharing events
- **Context Switch Tracking**: Monitor voluntary/involuntary context switches with microsecond precision
- **NUMA Analysis**: Analyze local vs remote memory accesses and bandwidth usage per NUMA node
- **Latency Spike Detection**: Detect and analyze latency spikes with cause analysis
- **Thread Scheduling**: Monitor real-time thread priorities, CPU affinity, and scheduling jitter
- **Interrupt Monitoring**: Track hardware interrupts and softirq processing impact

## Installation

```bash
pip install psutil numpy
```

For development and testing:
```bash
pip install pytest pytest-json-report
```

## Usage

### Basic Example

```python
from hft_resource_monitor import HFTResourceMonitor

# Create monitor instance
monitor = HFTResourceMonitor()

# Configure with microsecond precision
monitor.configure(
    sampling_interval_us=100,  # 100 microseconds
    cpu_affinity=[0, 1],       # Pin to specific cores
    realtime_priority=99       # Set real-time priority
)

# Attach to a trading process
monitor.attach_process(trading_pid)

# Start monitoring
monitor.start_monitoring()

# ... your trading application runs ...

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

# Stop monitoring
monitor.stop_monitoring()
```

### Monitoring Multiple Processes

```python
# Attach multiple processes
monitor.attach_process(process1_pid, track_cache=True, track_numa=True)
monitor.attach_process(process2_pid, track_cache=True, track_numa=False)

# Monitor all attached processes
monitor.start_monitoring()
```

### Real-time Analysis

```python
# Get thread scheduling information
scheduling_info = monitor.get_thread_scheduling_info(pid=trading_pid)

for thread in scheduling_info:
    print(f"Thread {thread.tid}: Priority={thread.priority}, "
          f"CPU Time={thread.cpu_time_us}µs, "
          f"Jitter={thread.scheduling_jitter_us}µs")
```

## Performance Targets

- Sub-microsecond measurement overhead
- Support for 1MHz sampling rate for critical metrics
- Process 10 million events per second
- Detect latency spikes within 10 microseconds
- Zero allocation in hot path monitoring code

## System Requirements

- Python 3.8+
- Linux operating system
- CAP_SYS_ADMIN capability for hardware counter access (or run as root)
- psutil and numpy packages

## Running Tests

Run the complete test suite:

```bash
pytest
```

Generate JSON test report (required):

```bash
pytest --json-report --json-report-file=pytest_results.json
```

Run specific test categories:

```bash
# Unit tests only
pytest tests/test_monitor.py tests/test_metrics.py tests/test_exceptions.py

# Integration tests
pytest tests/test_integration.py

# With verbose output
pytest -v
```

## Architecture

The library consists of several key components:

- **HFTResourceMonitor**: Main monitoring class that coordinates data collection
- **Metrics Classes**: Data classes for different metric types (cache, context switches, etc.)
- **Performance Counters**: Interface to hardware performance monitoring
- **Lock-free Buffers**: Circular buffers for zero-copy metric storage

## Limitations

- Currently uses simulated performance counters (real hardware counter integration planned)
- Requires elevated privileges for hardware access
- Linux-only (Windows/macOS not supported)

## License

This project is part of the LibraryBench benchmark suite.