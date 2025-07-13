# PyPatternGuard - Performance Pattern Detection Engine

## Overview
A specialized code pattern detection system designed for performance engineers to identify code patterns that impact application performance. The system detects inefficient algorithms, resource-intensive operations, and performance anti-patterns before they reach production.

## Persona Description
A performance optimization specialist who identifies code patterns that impact application performance. He needs to detect inefficient algorithms and resource-intensive operations before they reach production.

## Key Requirements

1. **Algorithm complexity analysis with Big O notation detection**: Critical for identifying performance bottlenecks by analyzing loops, recursion, and data structure operations to determine computational complexity and flag inefficient algorithms.

2. **Memory leak pattern detection including circular references**: Essential for preventing memory-related performance degradation by identifying object retention cycles, improper resource cleanup, and memory allocation patterns that could lead to leaks.

3. **Database query pattern analysis for N+1 problems**: Detects inefficient database access patterns like N+1 queries, missing indexes usage, and unnecessary data fetching that significantly impact application performance.

4. **Concurrency anti-pattern detection for race conditions**: Identifies thread safety issues, deadlock possibilities, and inefficient synchronization patterns that could cause performance problems or application instability.

5. **Performance regression tracking across code versions**: Tracks performance-critical code patterns over time, identifying when changes introduce performance degradations and providing historical context for optimization efforts.

## Technical Requirements

### Testability Requirements
- All complexity analysis must produce consistent, verifiable results
- Support for creating synthetic performance scenarios
- Ability to simulate various concurrency conditions
- Deterministic detection of performance patterns

### Performance Expectations
- Analyze codebases up to 1 million lines within 10 minutes
- Complexity analysis in near real-time for IDE integration
- Memory footprint under 2GB for analysis operations
- Support for incremental analysis in CI/CD pipelines

### Integration Points
- AST analysis using Python's `ast` module
- Static analysis for loop and recursion detection
- Pattern matching for database query identification
- Git integration for historical performance tracking

### Key Constraints
- Must work with Python 3.8+ codebases
- No external dependencies beyond Python standard library
- Must provide actionable performance insights
- Analysis must not impact system being analyzed

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The system must provide:

1. **Complexity Analyzer**: Analyzes code to determine Big O complexity by examining loop nesting, recursive calls, and data structure operations, providing both time and space complexity estimates with detailed breakdowns.

2. **Memory Leak Detector**: Identifies circular references between objects, detects missing cleanup in __del__ methods, analyzes generator and iterator usage for memory efficiency, and tracks object lifecycle patterns.

3. **Database Pattern Analyzer**: Detects N+1 query patterns in ORM usage, identifies missing bulk operations, analyzes query complexity and join patterns, validates connection pooling usage, and flags inefficient pagination.

4. **Concurrency Analyzer**: Identifies race conditions in shared state access, detects potential deadlocks from lock ordering, analyzes thread pool and async patterns, validates proper synchronization primitive usage, and flags blocking operations in async code.

5. **Performance Regression Tracker**: Compares complexity metrics across code versions, tracks performance-critical function changes, identifies newly introduced inefficiencies, maintains performance baseline metrics, and generates trend reports.

## Testing Requirements

### Key Functionalities to Verify
- Accurate Big O complexity calculation for various algorithms
- Correct identification of memory leak patterns
- Comprehensive N+1 query detection across ORMs
- Reliable race condition and deadlock detection
- Consistent performance regression identification

### Critical User Scenarios
- Analyzing a web application for database performance issues
- Detecting memory leaks in long-running data processing services
- Identifying algorithmic inefficiencies in computational code
- Finding concurrency issues in multi-threaded applications
- Tracking performance impact of recent code changes

### Performance Benchmarks
- Complexity analysis: < 100ms per function
- Memory pattern detection: < 2 seconds per module
- Database pattern analysis: < 1 second per query site
- Concurrency analysis: < 3 seconds per thread interaction
- Full analysis of 100,000 LOC: < 5 minutes

### Edge Cases and Error Conditions
- Dynamically generated code and eval usage
- Complex metaclass and decorator patterns
- Async generators and coroutines
- Native extension interactions
- Highly recursive algorithms with memoization

### Required Test Coverage Metrics
- Line coverage: minimum 90%
- Branch coverage: minimum 85%
- All complexity classes (O(1) through O(n!)) must be tested
- Common performance anti-patterns must have test cases
- Integration tests with real-world performance scenarios

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

The implementation successfully meets this persona's needs when:

1. **Detection Accuracy**: The system correctly identifies 95% of performance anti-patterns with complexity analysis accurate to within one complexity class.

2. **Actionable Results**: Each detected issue includes specific performance impact estimates and optimization recommendations.

3. **Measurable Impact**: Code optimized based on tool recommendations shows 50%+ performance improvement in identified hotspots.

4. **Regression Prevention**: Integration prevents 90% of performance regressions from reaching production.

5. **Scalability**: The tool itself maintains linear or better performance characteristics when analyzing large codebases.

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

## Environment Setup

From within the project directory, set up the virtual environment:
```
uv venv
source .venv/bin/activate
uv pip install -e .
```

Run tests with pytest-json-report:
```
uv pip install pytest-json-report
pytest --json-report --json-report-file=pytest_results.json
```