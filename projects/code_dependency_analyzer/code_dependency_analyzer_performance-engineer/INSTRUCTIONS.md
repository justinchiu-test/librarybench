# Import Performance Optimizer

## Overview
A performance-focused dependency analysis tool that helps systems engineers optimize application startup time and memory footprint by analyzing import chains, identifying bottlenecks, and suggesting lazy loading strategies.

## Persona Description
A systems engineer focused on application startup time and memory footprint optimization. They analyze import chains to identify bottlenecks and unnecessary dependencies.

## Key Requirements
1. **Import time profiling with bottleneck identification**: The tool must measure and profile the time taken by each import statement, building a performance tree that highlights the slowest imports and their cumulative impact on application startup time.

2. **Lazy loading opportunity detection for heavy modules**: Critical for optimization, the system must identify modules that are imported but not immediately used, suggesting candidates for lazy loading to defer their initialization cost until actually needed.

3. **Memory footprint analysis per dependency branch**: Essential for resource-constrained environments, the tool must measure memory consumption of each imported module and its dependencies, providing detailed breakdowns of memory usage by import branch.

4. **Circular import performance impact measurement**: To quantify hidden costs, the system must detect circular imports and measure their specific performance penalties, including repeated initialization and memory overhead from circular reference handling.

5. **Dynamic import optimization suggestions**: For maximum performance gains, the tool must analyze usage patterns and suggest converting static imports to dynamic imports, providing code transformation templates and estimated performance improvements.

## Technical Requirements
- **Testability requirements**: All profiling functions must be unit testable with mock import systems and timing data. Integration tests should verify accurate measurements against known performance scenarios.
- **Performance expectations**: Profiling overhead must be less than 5% of actual import time. Must handle applications with 10,000+ imports within reasonable analysis time.
- **Integration points**: Must integrate with Python's import system hooks, memory profilers, and provide APIs for CI/CD performance regression detection.
- **Key constraints**: Must work with various Python versions, handle compiled extensions (.pyd/.so files), and provide accurate measurements despite system load variations.

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The analyzer must hook into Python's import system to measure timing and memory usage, build detailed import dependency trees with performance metrics, identify optimization opportunities through usage analysis, generate lazy loading recommendations with code examples, and provide APIs for continuous performance monitoring. The system should support baseline comparisons and trend analysis.

## Testing Requirements
- **Key functionalities that must be verified**:
  - Accurate import time measurement with microsecond precision
  - Correct memory footprint calculation for module trees
  - Reliable lazy loading opportunity identification
  - Proper circular import impact quantification
  - Valid dynamic import transformation suggestions

- **Critical user scenarios that should be tested**:
  - Profiling a web application with heavy framework imports
  - Analyzing a data science project with large numerical libraries
  - Optimizing a CLI tool with slow startup time
  - Identifying memory waste in a microservice application
  - Detecting performance regressions in import chains

- **Performance benchmarks that must be met**:
  - Profile 1,000 imports with less than 50ms overhead
  - Complete full analysis of 10,000 imports in under 30 seconds
  - Memory overhead for profiling under 50MB
  - Generate optimization reports in under 5 seconds

- **Edge cases and error conditions that must be handled properly**:
  - Import errors and missing modules
  - C extension modules with no Python source
  - Conditional imports based on platform or version
  - Import hooks and custom importers
  - Multi-threaded import scenarios

- **Required test coverage metrics**:
  - Minimum 90% code coverage for profiling modules
  - 100% coverage for optimization recommendation engine
  - Full coverage of import hook integration
  - Performance regression tests for all major features

IMPORTANT:
- ALL functionality must be testable via pytest without any manual intervention
- Tests should verify behavior against requirements, not implementation details
- Tests should be designed to validate the WHAT (requirements) not the HOW (implementation)
- Tests should be comprehensive enough to verify all aspects of the requirements
- Tests should not assume or dictate specific implementation approaches
- REQUIRED: Tests must be run with pytest-json-report to generate a pytest_results.json file:
  ```
  pip install pytest-json-report
  pytest --json-report --json-report-file=pytest_results.json
  ```
- The pytest_results.json file must be included as proof that all tests pass

## Success Criteria
Clear metrics and outcomes that would indicate the implementation successfully meets this persona's needs:
- Reduces application startup time by 40% through optimization recommendations
- Identifies 90% of lazy loading opportunities in typical applications
- Measures import times with 95% accuracy compared to manual profiling
- Decreases memory footprint by 30% through targeted optimizations
- Provides actionable suggestions that developers implement in 80% of cases

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

## Environment Setup
From within the project directory, set up the development environment:
```bash
uv venv
source .venv/bin/activate
uv pip install -e .
```