# Memory Profiler Tool - Embedded Systems Engineer Pavel Instructions

You are tasked with implementing a memory profiler tool specifically designed for Pavel, an embedded systems engineer running Python on resource-constrained devices who needs to minimize memory footprint. He requires precise control over memory allocation and detailed reporting of even small allocations.

## Core Requirements

### 1. Micro-allocation tracking with byte-level precision
- Track every memory allocation down to individual bytes
- Record allocation timestamps with microsecond precision
- Identify allocation sources with full stack traces
- Categorize allocations by size classes (tiny, small, medium, large)
- Provide real-time allocation event streaming

### 2. Static memory usage analysis before deployment
- Analyze Python bytecode for potential memory usage
- Estimate memory requirements for different code paths
- Identify memory-intensive operations before runtime
- Generate pre-deployment memory usage reports
- Validate against device memory constraints

### 3. Memory fragmentation visualization and metrics
- Calculate fragmentation percentage and patterns
- Visualize memory layout as text-based diagrams
- Track free memory block distribution
- Identify fragmentation hotspots in code
- Suggest defragmentation strategies

### 4. Compile-time memory optimization recommendations
- Analyze code for memory optimization opportunities
- Suggest more memory-efficient data structures
- Identify redundant allocations
- Recommend object pooling candidates
- Generate optimization priority rankings

### 5. Cross-compilation memory prediction for target platforms
- Model memory usage for different architectures
- Account for platform-specific overhead
- Predict memory alignment requirements
- Estimate runtime memory for embedded targets
- Validate predictions against actual device measurements

## Implementation Guidelines

- Use Python exclusively for all implementations
- No UI components - focus on programmatic APIs and CLI tools
- All output should be text-based (JSON, CSV, or formatted text)
- Design for minimal runtime overhead on constrained devices
- Ensure compatibility with Python 3.8+

## Testing Requirements

All tests must be written using pytest and follow these guidelines:
- Generate detailed test reports using pytest-json-report
- Include memory usage assertions in tests
- Test with constrained memory scenarios
- Validate accuracy of byte-level tracking
- Ensure thread-safety where applicable

## Project Structure

```
memory_profiler_tool_embedded_engineer/
├── src/
│   ├── __init__.py
│   ├── micro_tracker.py      # Byte-level allocation tracking
│   ├── static_analyzer.py    # Pre-deployment analysis
│   ├── fragmentation.py      # Fragmentation metrics
│   ├── optimizer.py          # Optimization recommendations
│   └── cross_platform.py     # Cross-compilation prediction
├── tests/
│   ├── __init__.py
│   ├── test_micro_tracker.py
│   ├── test_static_analyzer.py
│   ├── test_fragmentation.py
│   ├── test_optimizer.py
│   └── test_cross_platform.py
├── requirements.txt
└── README.md
```

Remember: This tool must be lightweight enough to run on embedded devices while providing precise memory profiling capabilities that embedded engineers need for resource-constrained environments.