# Educational In-Memory Database with Visual Query Execution

## Overview
A transparent in-memory database implementation designed specifically for teaching database concepts to computer science students. This educational database provides clear visualization of internal operations, configurable performance scenarios, and side-by-side comparison of different implementation strategies to illustrate core database concepts without the complexity of production systems.

## Persona Description
Dr. Chen teaches database concepts to computer science students. She needs a transparent database implementation that clearly illustrates core concepts without the complexity of production systems.

## Key Requirements

1. **Step-by-Step Query Execution Visualization**
   - Implementation of a detailed query execution visualization system showing each operation in the query plan
   - Visual representation of intermediate results at each step of query processing
   - Detailed metrics collection at each query execution phase
   - This feature is critical for Dr. Chen's teaching as it makes abstract database concepts concrete and observable, allowing students to understand exactly how queries are executed and optimized

2. **Configurable Performance Degradation Modes**
   - Implementation of artificial performance limitation scenarios that simulate real-world database issues
   - Configurable bottlenecks in different database subsystems (memory, CPU, I/O)
   - Ability to introduce controlled performance problems for educational demonstrations
   - This feature allows Dr. Chen to demonstrate how database performance problems manifest and how they can be diagnosed and resolved, giving students practical troubleshooting experience

3. **Side-by-Side Indexing Strategy Comparison**
   - Implementation of multiple indexing strategies (B-tree, hash, bitmap, etc.) with comparative metrics
   - Visual representation of index structures and how they accelerate different query types
   - Performance dashboards showing metrics for each indexing approach
   - Understanding different indexing strategies is a core concept in database education, and this feature allows Dr. Chen to demonstrate the concrete advantages and trade-offs of each approach

4. **Interactive Transaction Isolation Demonstrations**
   - Implementation of different transaction isolation levels with clear visualization of their effects
   - Scenarios demonstrating phenomena like dirty reads, non-repeatable reads, and phantoms
   - Step-by-step execution of concurrent transactions showing isolation effects
   - Transaction isolation is one of the most challenging concepts for students to grasp, and this feature allows Dr. Chen to demonstrate exactly how different isolation levels affect concurrent operations

5. **Pedagogical SQL Dialect**
   - Implementation of a simplified SQL dialect designed specifically for teaching fundamental concepts
   - Progressive complexity levels that introduce advanced features incrementally
   - Clear error messages with educational explanations and suggestions
   - A simplified SQL dialect allows Dr. Chen to focus student attention on core concepts without overwhelming them with the complexity of full SQL, while providing a growth path to more advanced features

## Technical Requirements

### Testability Requirements
- Each visualization component must be testable through programmatic interfaces
- Performance degradation scenarios must be reproducible and measurable
- Indexing strategy comparisons must produce consistent, measurable results
- Transaction isolation behaviors must be consistently demonstrable through test cases

### Performance Expectations
- Base system should perform efficiently enough to support interactive classroom demonstrations
- Performance degradation modes should be precisely controllable to demonstrate specific concepts
- Visualization generation should not significantly impact system performance when disabled
- All operations should be traceable with minimal overhead

### Integration Points
- Output formats for visualizations should be standard and easily integrated into teaching materials
- Export functionality for query plans and execution traces
- Simple API for integrating custom examples and demonstrations
- Compatibility with standard educational database examples and benchmarks

### Key Constraints
- The implementation must use only Python standard library with no external dependencies
- All components must prioritize clarity and observability over production-grade performance
- The system must operate entirely in-memory with optional persistence
- The implementation should favor clarity of code over optimization where appropriate for teaching

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces. Visualizations should be generated as data structures or exported formats, not as interactive UI components.

## Core Functionality

The system must provide the following core functionality:

1. **In-Memory Database Engine**
   - Implementation of basic relational database structures (tables, indexes, etc.)
   - Support for fundamental SQL operations (SELECT, INSERT, UPDATE, DELETE)
   - Transaction management with different isolation levels

2. **Query Execution Engine**
   - Parser for the pedagogical SQL dialect
   - Query optimizer with clear execution plan generation
   - Step-by-step execution with access to intermediate results

3. **Visualization System**
   - Representation of database structures and operations
   - Capture of execution metrics at each processing step
   - Export of visualization data in standardized formats

4. **Performance Simulation Framework**
   - Controlled introduction of performance bottlenecks
   - Accurate measurement of performance impacts
   - Comparison tools for different execution scenarios

5. **Educational Scaffolding**
   - Progressive complexity levels for different educational stages
   - Clear documentation aimed at educational use cases
   - Example datasets and queries for common teaching scenarios

## Testing Requirements

### Key Functionalities to Verify
- Correct execution of SQL queries at all complexity levels
- Accurate visualization of query execution steps
- Proper implementation of different indexing strategies
- Correct behavior of transaction isolation levels
- Reproducible performance degradation scenarios

### Critical User Scenarios
- Classroom demonstration of basic SQL operations
- Comparison of query performance with and without indexes
- Observation of transaction isolation phenomena
- Analysis of query execution plans and optimization strategies
- Progressive learning scenarios from basic to advanced concepts

### Performance Benchmarks
- Base system should execute simple queries in under 50ms
- Visualization data should be generated within 100ms
- Performance degradation modes should show measurable but controlled impacts
- System should handle databases with up to 100,000 records for demonstration purposes

### Edge Cases and Error Conditions
- Handling of incorrect SQL syntax with educational error messages
- Behavior under memory pressure
- Recovery from transaction failures
- Performance with complex join operations
- Handling of large result sets

### Required Test Coverage Metrics
- Minimum 90% code coverage for all modules
- 100% coverage of SQL parsing and execution code
- All transaction isolation levels must be tested
- All indexing strategies must have comparative benchmarks
- All performance degradation scenarios must be tested

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

The implementation will be considered successful if:

1. It clearly demonstrates core database concepts through visualization and instrumentation
2. Different indexing strategies show measurable performance differences in appropriate scenarios
3. Transaction isolation levels correctly demonstrate database phenomena
4. Performance degradation modes accurately simulate common database issues
5. The pedagogical SQL dialect effectively supports progressive learning

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

## Development Setup

To set up the development environment:

1. Clone the repository and navigate to the project directory
2. Create a virtual environment using:
   ```
   uv venv
   ```
3. Activate the virtual environment:
   ```
   source .venv/bin/activate
   ```
4. Install the project in development mode:
   ```
   uv pip install -e .
   ```
5. Run tests with:
   ```
   pip install pytest-json-report
   pytest --json-report --json-report-file=pytest_results.json
   ```

CRITICAL REMINDER: Generating and providing the pytest_results.json file is a MANDATORY requirement for project completion.