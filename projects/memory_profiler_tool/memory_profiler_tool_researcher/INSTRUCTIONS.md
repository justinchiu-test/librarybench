# Memory Profiler Tool - Scientific Computing Researcher Dr. Chen Instructions

You are tasked with implementing a memory profiler tool specifically designed for Dr. Chen, a researcher running long computational simulations who needs to track memory usage across distributed computing nodes. He requires aggregated memory analysis for parallel processing applications.

## Core Requirements

### 1. MPI-aware memory profiling across compute nodes
- Track memory usage per MPI rank
- Aggregate memory statistics across all nodes
- Monitor inter-process communication buffers
- Identify memory imbalances between ranks
- Support both OpenMPI and MPICH environments

### 2. Memory usage correlation with computation phases
- Tag memory snapshots with computation phases
- Track phase transitions and memory patterns
- Identify memory-intensive computation stages
- Generate phase-based memory reports
- Support custom phase annotations

### 3. Shared memory optimization for multi-processing
- Analyze shared memory segment usage
- Identify opportunities for memory sharing
- Track copy-on-write behavior
- Monitor shared memory lock contention
- Recommend optimal shared memory configurations

### 4. Memory-bound vs compute-bound analysis
- Measure memory bandwidth utilization
- Calculate memory access patterns
- Identify performance bottlenecks
- Generate memory/compute balance reports
- Suggest optimization strategies

### 5. Checkpoint memory footprint optimization
- Analyze checkpoint memory requirements
- Identify redundant checkpoint data
- Suggest incremental checkpointing strategies
- Calculate checkpoint compression potential
- Optimize checkpoint frequency based on memory

## Implementation Guidelines

- Use Python exclusively for all implementations
- No UI components - focus on programmatic APIs and CLI tools
- All output should be text-based (JSON, CSV, or formatted text)
- Design for HPC cluster environments
- Support distributed memory profiling

## Testing Requirements

All tests must be written using pytest and follow these guidelines:
- Generate detailed test reports using pytest-json-report
- Test with simulated MPI environments
- Validate distributed memory tracking
- Test scalability with multiple processes
- Ensure accuracy of aggregated metrics

## Project Structure

```
memory_profiler_tool_researcher/
├── src/
│   ├── __init__.py
│   ├── mpi_profiler.py       # MPI-aware profiling
│   ├── phase_tracker.py      # Computation phase analysis
│   ├── shared_memory.py      # Shared memory optimization
│   ├── performance_analyzer.py # Memory/compute analysis
│   └── checkpoint_optimizer.py # Checkpoint optimization
├── tests/
│   ├── __init__.py
│   ├── test_mpi_profiler.py
│   ├── test_phase_tracker.py
│   ├── test_shared_memory.py
│   ├── test_performance_analyzer.py
│   └── test_checkpoint_optimizer.py
├── requirements.txt
└── README.md
```

Remember: This tool must handle the complexities of distributed scientific computing while providing insights that help researchers optimize their memory usage across large-scale simulations.