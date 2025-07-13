# Memory Profiler Tool - Fintech Backend Engineer Alex Instructions

You are tasked with implementing a memory profiler tool specifically designed for Alex, a backend engineer at a trading firm who needs microsecond-precision memory profiling without affecting latency. He requires understanding of memory allocation patterns during high-frequency trading operations.

## Core Requirements

### 1. Lock-free memory profiling for ultra-low latency
- Implement wait-free data structures for profiling
- Use atomic operations for metric collection
- Minimize cache line contention
- Support zero-allocation profiling mode
- Provide nanosecond timestamp precision

### 2. Memory allocation jitter analysis and histograms
- Track allocation timing variations
- Generate latency histograms and percentiles
- Identify allocation pattern outliers
- Measure GC-induced jitter
- Calculate jitter impact on trading performance

### 3. Pre-allocated memory pool utilization tracking
- Monitor memory pool usage and fragmentation
- Track pool allocation/deallocation patterns
- Identify pool exhaustion risks
- Measure pool allocation efficiency
- Optimize pool sizing recommendations

### 4. GC pause correlation with memory pressure
- Track garbage collection events and duration
- Correlate GC pauses with memory usage
- Predict GC triggers based on allocation rate
- Identify GC-friendly allocation patterns
- Generate GC tuning recommendations

### 5. Trading session memory pattern analysis
- Profile memory usage by trading session phase
- Identify market open/close memory spikes
- Track order book memory requirements
- Analyze position tracking memory costs
- Generate session-based optimization reports

## Implementation Guidelines

- Use Python exclusively for all implementations
- No UI components - focus on programmatic APIs and CLI tools
- All output should be text-based (JSON, CSV, or formatted text)
- Design for minimal latency impact (< 1 microsecond overhead)
- Support high-frequency data collection

## Testing Requirements

All tests must be written using pytest and follow these guidelines:
- Generate detailed test reports using pytest-json-report
- Test profiling overhead and latency impact
- Validate microsecond timing accuracy
- Test under high-frequency allocation scenarios
- Ensure thread-safety and lock-free guarantees

## Project Structure

```
memory_profiler_tool_fintech_engineer/
├── src/
│   ├── __init__.py
│   ├── lockfree_profiler.py  # Lock-free profiling implementation
│   ├── jitter_analyzer.py     # Allocation jitter analysis
│   ├── pool_tracker.py        # Memory pool monitoring
│   ├── gc_correlator.py       # GC pause analysis
│   └── session_analyzer.py    # Trading session patterns
├── tests/
│   ├── __init__.py
│   ├── test_lockfree_profiler.py
│   ├── test_jitter_analyzer.py
│   ├── test_pool_tracker.py
│   ├── test_gc_correlator.py
│   └── test_session_analyzer.py
├── requirements.txt
└── README.md
```

Remember: This tool must meet the extreme performance requirements of high-frequency trading systems while providing actionable insights for optimizing memory allocation patterns in latency-critical environments.