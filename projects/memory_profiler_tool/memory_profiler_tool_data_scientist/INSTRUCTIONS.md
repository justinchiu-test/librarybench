# PyMemTrace for Data Science Workloads

## Overview
A specialized memory profiling tool designed for data scientists working with memory-intensive operations in pandas, NumPy, and deep learning frameworks. This implementation focuses on tracking memory usage patterns during data transformations, model training, and large-scale data processing to prevent out-of-memory errors and optimize computational efficiency.

## Persona Description
A data scientist working with large pandas DataFrames who experiences out-of-memory errors during model training. She needs to understand memory spikes during data transformations and identify opportunities for memory-efficient operations.

## Key Requirements

1. **DataFrame Memory Footprint Analysis with Column-level Breakdown**
   - Track memory usage for each DataFrame column individually
   - Provide dtype optimization suggestions (e.g., float64 to float32)
   - Monitor memory overhead from multi-indexing and categorical data
   - Calculate memory efficiency ratios for sparse vs dense representations
   - Essential for identifying which columns consume the most memory and can be optimized

2. **Memory Spike Prediction Before Operations Based on Data Shapes**
   - Predict memory requirements before executing operations like merges, pivots, and groupby
   - Estimate temporary memory overhead during operations
   - Provide warnings when operations would exceed available memory
   - Calculate memory multipliers for common DataFrame operations
   - Critical for preventing crashes during large data transformations

3. **Alternative Operation Suggestions for Memory-heavy Transformations**
   - Suggest chunk-based processing when operations exceed memory limits
   - Recommend in-place operations where applicable
   - Propose memory-efficient alternatives (e.g., using iterators instead of full materialization)
   - Identify opportunities for lazy evaluation strategies
   - Vital for enabling data scientists to work with datasets larger than available RAM

4. **Jupyter Notebook Integration with Cell-by-cell Memory Tracking**
   - Track memory allocation and deallocation per notebook cell
   - Provide memory usage visualization in notebook output
   - Monitor memory leaks across cell executions
   - Support memory profiling magic commands
   - Essential for interactive data exploration and debugging memory issues

5. **GPU Memory Tracking for Deep Learning Workloads**
   - Monitor CUDA memory allocation for tensors and models
   - Track memory fragmentation on GPU devices
   - Provide memory optimization for batch size tuning
   - Support multi-GPU memory profiling
   - Critical for optimizing deep learning training on GPU-constrained systems

## Technical Requirements

### Testability Requirements
- All functionality must be implemented as Python modules with no UI components
- Comprehensive test coverage using pytest with parametrized tests
- Mock data generators for simulating large DataFrames and tensors
- Test fixtures for various memory scenarios (normal, spike, leak)
- Performance benchmarks to ensure profiling overhead remains under 5%

### Performance Expectations
- Memory profiling overhead must not exceed 5% of total runtime
- Support for profiling DataFrames up to 100GB in size
- Real-time memory tracking with sub-second update intervals
- Efficient memory snapshot storage using compression
- Minimal memory footprint for the profiler itself (<100MB)

### Integration Points
- Native integration with pandas DataFrame internals
- Jupyter notebook kernel communication for cell tracking
- PyTorch/TensorFlow hooks for GPU memory monitoring
- IPython magic command registration
- Export capabilities to common monitoring formats (JSON, CSV)

### Key Constraints
- Must work with Python 3.8+ standard library
- No external dependencies beyond standard data science stack
- Thread-safe for concurrent DataFrame operations
- Compatible with distributed computing frameworks (Dask, Ray)
- Must not interfere with garbage collection cycles

## Core Functionality

The memory profiler must provide a comprehensive library for tracking and analyzing memory usage in data science workflows:

1. **DataFrame Memory Analyzer**
   - Column-level memory tracking with dtype analysis
   - Memory usage history for DataFrames across transformations
   - Automatic detection of memory-inefficient operations
   - Integration with pandas internals for accurate measurements

2. **Predictive Memory Estimator**
   - Operation-specific memory prediction algorithms
   - Data shape analysis for memory requirement calculation
   - Warning system for operations exceeding memory thresholds
   - Suggestion engine for memory-efficient alternatives

3. **Notebook Memory Tracker**
   - Cell execution memory profiling
   - Memory delta visualization between cells
   - Persistent memory tracking across kernel restarts
   - Export of memory profiles for reproducibility

4. **GPU Memory Monitor**
   - Real-time GPU memory allocation tracking
   - Model memory footprint analysis
   - Batch size optimization recommendations
   - Multi-GPU memory distribution analysis

5. **Memory Optimization Advisor**
   - Automated suggestions for dtype optimization
   - Chunking strategies for large operations
   - Memory-efficient coding patterns
   - Memory leak detection and reporting

## Testing Requirements

### Key Functionalities to Verify
- Accurate memory measurement for DataFrames of various sizes and dtypes
- Correct prediction of memory requirements for operations
- Proper integration with Jupyter notebooks
- GPU memory tracking accuracy
- Performance overhead within acceptable limits

### Critical User Scenarios
- Processing a 10GB CSV file with memory constraints
- Training a deep learning model with optimal batch size
- Performing complex DataFrame transformations without OOM errors
- Identifying memory leaks in long-running notebook sessions
- Optimizing memory usage in production data pipelines

### Performance Benchmarks
- Memory tracking overhead < 5% for operations > 1 second
- Memory prediction accuracy > 90% for common operations
- Support for DataFrames with > 1000 columns
- Real-time updates with < 100ms latency
- Snapshot generation < 1 second for 1GB DataFrames

### Edge Cases and Error Conditions
- Handling of out-of-memory errors during profiling
- Recovery from corrupted memory snapshots
- Concurrent DataFrame modifications during profiling
- GPU memory fragmentation scenarios
- Kernel interruption during memory tracking

### Required Test Coverage Metrics
- Code coverage > 90%
- Branch coverage > 85%
- Integration test coverage for all major features
- Performance regression tests for each release
- Memory leak tests for profiler itself

**IMPORTANT**: All tests must be run with pytest-json-report to generate a pytest_results.json file:
```bash
pip install pytest-json-report
pytest --json-report --json-report-file=pytest_results.json
```

## Success Criteria

The implementation will be considered successful when:

1. **All functional requirements are met** with comprehensive test coverage
2. **Memory profiling accuracy** is within 2% of actual memory usage
3. **Performance overhead** remains below 5% for typical workloads
4. **Integration works seamlessly** with Jupyter notebooks and GPU frameworks
5. **Memory optimization suggestions** reduce memory usage by at least 20% in test scenarios
6. **All tests pass** when run with pytest and a valid pytest_results.json file is generated
7. **Documentation** includes clear examples for common data science use cases

**REQUIRED FOR SUCCESS**:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

## Implementation Guidelines

Use `uv venv` to set up the virtual environment. From within the project directory, activate the environment with `source .venv/bin/activate`. Install the project with `uv pip install -e .`.

Focus on creating a robust, production-ready library that data scientists can rely on for memory optimization in their daily work. The implementation should prioritize accuracy, low overhead, and actionable insights over complex features.