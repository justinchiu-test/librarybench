# Import Performance Optimizer

A performance-focused dependency analysis tool that helps systems engineers optimize application startup time and memory footprint by analyzing import chains, identifying bottlenecks, and suggesting lazy loading strategies.

## Overview

The Import Performance Optimizer is designed to address common performance issues in Python applications related to module imports. It provides comprehensive analysis and actionable recommendations to reduce startup time and memory consumption.

### Key Features

- **Import Time Profiling**: Measures and profiles the time taken by each import statement with microsecond precision
- **Memory Footprint Analysis**: Tracks memory consumption of each imported module and its dependencies
- **Lazy Loading Detection**: Identifies modules that can be loaded on-demand rather than at startup
- **Circular Import Analysis**: Detects circular dependencies and quantifies their performance impact
- **Dynamic Import Optimization**: Suggests converting static imports to dynamic imports based on usage patterns

## Installation

### Prerequisites

- Python 3.8 or higher
- pip or uv package manager

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd code_dependency_analyzer_performance-engineer
```

2. Create a virtual environment:
```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install the package in development mode:
```bash
uv pip install -e .
```

4. Install development dependencies (for running tests):
```bash
uv pip install -e ".[dev]"
```

## Usage Examples

### Basic Import Profiling

```python
from import_performance_optimizer import ImportProfiler

# Profile imports
profiler = ImportProfiler()

with profiler.profile():
    import your_application  # Replace with your module

# Get detailed metrics
metrics = profiler.get_import_metrics()
for metric in metrics[:10]:  # Top 10 slowest imports
    print(f"{metric.module_name}: {metric.import_time.total_seconds():.3f}s")

# Get import tree visualization
print(profiler.get_import_tree_visualization())
```

### Memory Footprint Analysis

```python
from import_performance_optimizer import MemoryAnalyzer

analyzer = MemoryAnalyzer()
analyzer.start_analysis()

# Measure memory for specific modules
analyzer.measure_module_memory('numpy')
analyzer.measure_module_memory('pandas')

# Get memory footprints
footprints = analyzer.get_memory_footprints()
for footprint in footprints:
    print(f"{footprint.module_name}: {footprint.direct_memory / (1024*1024):.2f} MB")

# Identify memory-heavy branches
heavy_branches = analyzer.identify_memory_heavy_branches(threshold_mb=10.0)
```

### Lazy Loading Detection

```python
from import_performance_optimizer import LazyLoadingDetector, ImportProfiler

# First, profile to get import times
profiler = ImportProfiler()
with profiler.profile():
    import your_application

# Analyze for lazy loading opportunities
detector = LazyLoadingDetector()
detector.analyze_directory('.')  # Analyze current directory
detector.set_module_import_times(
    {m.module_name: m.import_time.total_seconds() 
     for m in profiler.get_import_metrics()}
)

# Get optimization opportunities
opportunities = detector.detect_opportunities()
for opp in opportunities:
    print(f"{opp.module_name}: Save ~{opp.estimated_time_savings.total_seconds():.3f}s")
    print(f"  Location: {opp.import_location}")
    print(f"  First use: {opp.first_usage_location}")
    print(f"  Suggestion: {opp.transformation_suggestion}\n")
```

### Circular Import Detection

```python
from import_performance_optimizer import CircularImportAnalyzer

analyzer = CircularImportAnalyzer()
analyzer.build_import_graph('your_application')

# Get circular import analysis
circular_infos = analyzer.measure_circular_import_impact()
for info in circular_infos:
    print(f"Circular import detected: {' -> '.join(info.modules_involved)}")
    print(f"  Performance impact: {info.performance_impact.total_seconds():.3f}s")
    print(f"  Severity: {info.severity}")
    
    # Get refactoring suggestions
    suggestions = analyzer.get_refactoring_suggestions(info)
    for suggestion in suggestions:
        print(f"  - {suggestion}")
```

### Dynamic Import Optimization

```python
from import_performance_optimizer import DynamicImportOptimizer, ImportProfiler, MemoryAnalyzer

# Get performance data
profiler = ImportProfiler()
memory_analyzer = MemoryAnalyzer()

# ... perform profiling ...

# Analyze for dynamic import opportunities
optimizer = DynamicImportOptimizer()
optimizer.analyze_directory('.')
optimizer.set_performance_data(
    import_times={m.module_name: m.import_time.total_seconds() for m in metrics},
    memory_usage={f.module_name: f.direct_memory for f in footprints}
)

# Get suggestions
suggestions = optimizer.generate_suggestions()
for suggestion in suggestions:
    print(f"\nModule: {suggestion.module_name}")
    print(f"Current: {suggestion.current_import_statement}")
    print(f"Suggested: {suggestion.suggested_import_statement}")
    print(f"Time savings: {suggestion.estimated_time_improvement.total_seconds():.3f}s")
    print(f"Memory savings: {suggestion.estimated_memory_savings / (1024*1024):.2f} MB")
    
    for example in suggestion.code_examples:
        print(f"\nExample:\n{example}")
```

### Complete Analysis Workflow

```python
from import_performance_optimizer import (
    ImportProfiler, MemoryAnalyzer, LazyLoadingDetector,
    CircularImportAnalyzer, DynamicImportOptimizer
)

def analyze_application(module_name: str, source_directory: str):
    # 1. Profile imports
    profiler = ImportProfiler()
    with profiler.profile():
        __import__(module_name)
    
    import_metrics = profiler.get_import_metrics()
    
    # 2. Analyze memory
    memory_analyzer = MemoryAnalyzer()
    memory_analyzer.start_analysis()
    for metric in import_metrics:
        memory_analyzer.measure_module_memory(metric.module_name)
    
    memory_footprints = memory_analyzer.get_memory_footprints()
    
    # 3. Detect lazy loading opportunities
    lazy_detector = LazyLoadingDetector()
    lazy_detector.analyze_directory(source_directory)
    lazy_detector.set_module_import_times(
        {m.module_name: m.import_time.total_seconds() for m in import_metrics}
    )
    
    # 4. Analyze circular imports
    circular_analyzer = CircularImportAnalyzer()
    circular_analyzer.build_import_graph(module_name)
    
    # 5. Generate optimization suggestions
    dynamic_optimizer = DynamicImportOptimizer()
    dynamic_optimizer.analyze_directory(source_directory)
    dynamic_optimizer.set_performance_data(
        {m.module_name: m.import_time.total_seconds() for m in import_metrics},
        {f.module_name: f.direct_memory for f in memory_footprints}
    )
    
    # Print summary report
    print(f"=== Import Performance Analysis for {module_name} ===")
    print(f"\nTotal import time: {sum(m.import_time.total_seconds() for m in import_metrics):.3f}s")
    print(f"Total memory footprint: {sum(f.direct_memory for f in memory_footprints) / (1024*1024):.2f} MB")
    
    print("\nTop bottlenecks:")
    for metric in import_metrics[:5]:
        if metric.is_bottleneck:
            print(f"  - {metric.module_name}: {metric.cumulative_time.total_seconds():.3f}s")
    
    lazy_report = lazy_detector.get_summary_report()
    print(f"\nLazy loading opportunities: {lazy_report['total_opportunities']}")
    print(f"Potential time savings: {lazy_report['total_time_savings_seconds']:.3f}s")
    
    circular_report = circular_analyzer.get_summary_report()
    print(f"\nCircular imports found: {circular_report['total_circular_imports']}")
    print(f"Critical severity: {circular_report['critical_severity_count']}")
    
    dynamic_report = dynamic_optimizer.get_optimization_summary()
    print(f"\nDynamic import suggestions: {dynamic_report['total_suggestions']}")
    print(f"Total optimization potential: {dynamic_report['total_time_savings_seconds']:.3f}s")

# Example usage
analyze_application('my_app', './src')
```

## Running Tests

The project includes a comprehensive test suite covering all functionality:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=import_performance_optimizer

# Run specific test file
pytest tests/test_profiler.py

# Run with JSON report (required for verification)
pytest --json-report --json-report-file=pytest_results.json
```

### Test Categories

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test components working together
- **Performance Tests**: Verify performance requirements are met
- **Edge Case Tests**: Test error handling and boundary conditions

## API Reference

### ImportProfiler

- `start_profiling()`: Begin profiling imports
- `stop_profiling()`: Stop profiling imports
- `profile()`: Context manager for profiling
- `get_import_metrics()`: Get detailed metrics for all imports
- `get_slowest_imports(top_n)`: Get the N slowest imports
- `get_import_tree_visualization()`: Get text visualization of import tree

### MemoryAnalyzer

- `start_analysis()`: Initialize memory analysis
- `measure_module_memory(module_name)`: Measure memory for a specific module
- `get_memory_footprints(modules)`: Get memory footprint information
- `identify_memory_heavy_branches(threshold_mb)`: Find memory-intensive dependencies
- `get_optimization_opportunities()`: Get memory optimization suggestions

### LazyLoadingDetector

- `analyze_file(file_path)`: Analyze a Python file
- `analyze_directory(directory)`: Analyze all Python files in directory
- `set_module_import_times(times)`: Set import timing data
- `detect_opportunities()`: Get lazy loading opportunities
- `get_summary_report()`: Get analysis summary

### CircularImportAnalyzer

- `build_import_graph(root_module)`: Build dependency graph
- `measure_circular_import_impact()`: Measure performance impact
- `find_all_circular_paths(start, end)`: Find circular import paths
- `get_refactoring_suggestions(info)`: Get refactoring recommendations

### DynamicImportOptimizer

- `analyze_file(file_path)`: Analyze file for dynamic import opportunities
- `analyze_directory(directory)`: Analyze directory
- `set_performance_data(times, memory)`: Set performance metrics
- `generate_suggestions()`: Generate optimization suggestions
- `get_optimization_summary()`: Get optimization summary

## Performance Requirements

The tool is designed to handle large codebases efficiently:

- Profile 1,000 imports with less than 50ms overhead
- Complete full analysis of 10,000 imports in under 30 seconds
- Memory overhead for profiling under 50MB
- Generate optimization reports in under 5 seconds

## License

MIT License - see LICENSE file for details.