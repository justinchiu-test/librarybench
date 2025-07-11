# Process Resource Monitor - Embedded IoT Platform Developer Edition

## Overview
You are building a Python-based process resource monitoring library specifically designed for Wei, an IoT platform developer monitoring edge device resource usage. The library should ensure applications run within strict resource constraints on ARM and other embedded processors while tracking detailed resource usage patterns.

## Core Requirements

### 1. Cross-architecture Process Monitoring (ARM, MIPS, x86)
- Support process monitoring across different CPU architectures
- Handle architecture-specific performance counters
- Account for big.LITTLE and heterogeneous architectures
- Monitor architecture-specific instruction usage
- Track cross-compilation process resource usage

### 2. Power Consumption Correlation with Process Activity
- Correlate CPU frequency scaling with power usage
- Track process wake locks and their power impact
- Monitor peripheral activation by processes
- Measure idle vs active power consumption
- Identify power-hungry code patterns

### 3. Flash Storage Wear Leveling Impact Tracking
- Monitor flash write patterns per process
- Track write amplification factors
- Identify processes causing excessive flash wear
- Monitor filesystem journal activity
- Predict flash lifetime based on usage patterns

### 4. Temperature-based Throttling Detection
- Monitor CPU/GPU temperature vs frequency
- Detect thermal throttling events
- Correlate process activity with temperature spikes
- Track cooling effectiveness during high load
- Identify thermal hotspots in the system

### 5. Mesh Network Communication Resource Overhead
- Monitor network stack resource usage
- Track mesh routing protocol overhead
- Measure packet forwarding resource cost
- Identify communication pattern inefficiencies
- Monitor battery impact of mesh participation

## Technical Specifications

### Data Collection
- Low-overhead monitoring suitable for constrained devices
- Support for limited memory environments (<256MB RAM)
- Efficient data compression for storage
- Power-aware sampling strategies
- Remote monitoring capabilities for headless devices

### API Design
```python
# Example usage
monitor = IoTResourceMonitor()

# Configure for embedded platform
monitor.configure(
    architecture="armv7",
    cpu_governor="ondemand",
    storage_type="emmc",
    max_memory_kb=256000
)

# Monitor process with power correlation
process_stats = monitor.monitor_process(
    process_name="sensor_daemon",
    include_power=True,
    sample_rate_hz=10
)

# Analyze power consumption
power_analysis = monitor.analyze_power_usage(
    time_window="1h",
    correlate_with_processes=True,
    identify_optimization=True
)

# Track flash wear
flash_stats = monitor.get_flash_wear_status(
    partition="/dev/mmcblk0p2",
    include_predictions=True,
    per_process_breakdown=True
)

# Detect thermal issues
thermal_events = monitor.detect_thermal_throttling(
    include_process_correlation=True,
    temperature_threshold=70
)

# Monitor mesh network overhead
mesh_stats = monitor.analyze_mesh_overhead(
    interface="mesh0",
    include_battery_impact=True,
    optimization_hints=True
)
```

### Testing Requirements
- Cross-compilation testing for multiple architectures
- Power measurement validation with hardware
- Flash wear simulation testing
- Thermal throttling scenario testing
- Use pytest with pytest-json-report for test result formatting
- Test on real IoT hardware when possible

### Performance Targets
- Use <5% CPU on embedded processors
- Memory footprint <10MB
- Support devices with 32MB+ RAM
- Monitor 50+ processes simultaneously
- Generate reports with minimal resource spike

## Implementation Constraints
- Python 3.8+ compatibility (or MicroPython where applicable)
- Use minimal dependencies: psutil (if available), standard library
- No GUI components - this is a backend library only
- Support both Linux and RTOS environments
- Work with limited or no filesystem access

## Deliverables
1. Core Python library optimized for embedded systems
2. Cross-architecture process monitoring support
3. Power consumption analysis tools
4. Flash wear prediction system
5. CLI tool suitable for embedded device debugging