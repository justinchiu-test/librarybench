# EdDB: Educational In-Memory Database for Teaching Database Concepts

## Overview
A transparent, educational in-memory database implementation that clearly demonstrates core database concepts and internals. The system prioritizes clarity and insight into database operations over performance, making it an ideal teaching tool for computer science education.

## Persona Description
Dr. Chen teaches database concepts to computer science students. She needs a transparent database implementation that clearly illustrates core concepts without the complexity of production systems.

## Key Requirements

1. **Step-by-step query execution visualization**
   - Critical for students to understand how database operations actually work
   - Must visually break down each step in query planning and execution
   - Should show parse trees, execution plans, index usage decisions, and row-by-row processing
   - Must allow pausing, stepping through, and inspecting state at each execution phase
   - Should include execution statistics and explain why specific execution paths were chosen

2. **Configurable performance degradation modes**
   - Essential for teaching students about real-world database issues and optimization
   - Must simulate various performance problems (missing indexes, poor join orders, etc.)
   - Should allow instructors to deliberately create suboptimal conditions for students to diagnose
   - Must include detailed metrics showing the impact of each simulated issue
   - Should provide hints and guidance for identifying and resolving the performance problems

3. **Side-by-side comparison of indexing strategies**
   - Vital for demonstrating the importance and impact of proper database indexing
   - Must support multiple index types (B-tree, hash, bitmap) with visualization of their structure
   - Should execute identical queries with different indexes to demonstrate performance differences
   - Must show detailed metrics on index creation, maintenance, and query performance
   - Should visualize index traversal during query execution

4. **Interactive transaction isolation demonstrations**
   - Key for teaching complex concurrency concepts in an understandable way
   - Must support different isolation levels (read uncommitted through serializable)
   - Should demonstrate anomalies (dirty reads, non-repeatable reads, phantoms) when they occur
   - Must visualize transaction timelines and lock acquisition/release
   - Should allow creating and resolving deadlock situations for educational purposes

5. **Simplified SQL dialect for pedagogical progression**
   - Important for gradually introducing SQL concepts without overwhelming students
   - Must support basic to advanced SQL features that can be enabled progressively
   - Should provide clear error messages that explain syntax and semantic issues
   - Must include built-in examples and templates for common SQL patterns
   - Should offer hints and suggestions when students write suboptimal queries

## Technical Requirements

### Testability Requirements
- All components must be thoroughly testable with pytest
- Tests must verify correctness of visualization and educational outputs
- Performance degradation modes must be testable with measurable impact
- Comparative tests must validate that index performance differences are accurately represented
- Transaction isolation tests must confirm correct behavior at each isolation level

### Performance Expectations
- Performance itself is not critical, but must be consistent and predictable
- Visualization must be responsive even with larger datasets (up to 100,000 rows)
- Deliberately degraded performance must be measurably different but not completely unusable
- Side-by-side comparisons must show meaningful, consistent differences between approaches
- System should scale appropriately for classroom usage (25-50 simultaneous users)

### Integration Points
- Must provide Python APIs for integration with Jupyter notebooks and classroom tools
- Should offer export capabilities for visualizations and execution plans
- Must support importing and exporting datasets in common formats (CSV, JSON)
- Should include integration with common educational platforms or LMS systems

### Key Constraints
- No UI components - purely APIs and libraries that can be integrated into educational tools
- Must operate without external database dependencies - self-contained Python library
- All operations must be traceable and explainable - no "black box" components
- Simplifications must maintain conceptual accuracy - educational value over performance

## Core Functionality

The implementation must provide:

1. **Transparent Data Storage Layer**
   - In-memory relational storage with visible internal structures
   - Schema definition with support for common data types and constraints
   - Storage formats that can be inspected and visualized
   - Transaction support with visible ACID property implementation

2. **Educational Query Engine**
   - SQL parser with detailed parse tree visualization
   - Query planner showing decision-making process for execution strategies
   - Step-by-step execution mechanism with state inspection at each point
   - Support for both optimal and deliberately suboptimal execution paths

3. **Indexing Framework**
   - Multiple index type implementations with visualizable structures
   - Index creation, maintenance, and usage statistics
   - Side-by-side performance comparison tools for different indexing strategies
   - Visual demonstrations of index traversal during query execution

4. **Concurrency Control System**
   - Transaction manager with different isolation level implementations
   - Lock manager with visualization of lock acquisition and contention
   - Deadlock detection and resolution mechanisms
   - Demonstration capabilities for common concurrency anomalies

5. **Educational Tooling**
   - Progressive SQL dialect with configurable feature sets
   - Performance issue simulation framework
   - Visualization generators for key database components and operations
   - Example datasets and query scenarios for teaching different concepts

## Testing Requirements

### Key Functionalities to Verify
- Accuracy of query execution and results across all SQL features
- Correctness of visualization outputs for parse trees and execution plans
- Impact of different indexing strategies on measurable performance
- Behavior of transactions at different isolation levels
- Effectiveness of performance degradation modes in simulating real-world issues

### Critical User Scenarios
- Students following along with lecture demonstrations in individual environments
- Instructor creating custom scenarios to demonstrate specific database concepts
- Students diagnosing deliberately introduced performance issues
- Comparative analysis of different approaches to the same database problem
- Progressive learning path from basic SQL through advanced concepts

### Performance Benchmarks
- Measure baseline performance for standard operations as reference points
- Verify performance deltas between optimal and degraded configurations
- Validate index performance improvements match theoretical expectations
- Confirm visualization generation remains responsive with larger datasets
- Measure transaction throughput at different isolation levels

### Edge Cases and Error Conditions
- Malformed SQL queries with helpful error messages
- Complex transaction scenarios with deadlocks and resolution
- Queries that would typically require optimization in real databases
- Schema edge cases with unusual constraints or relationships
- Recovery from simulated failure scenarios

### Required Test Coverage
- 90% code coverage for all components
- 100% coverage of educational visualization generation
- Comprehensive tests for all SQL features and edge cases
- Complete verification of transaction isolation level behaviors
- Validation of all performance simulation modes

## Success Criteria

The implementation will be considered successful if it:

1. Accurately demonstrates core database concepts through clear visualizations and step-by-step execution
2. Effectively illustrates performance differences between varying approaches to the same problem
3. Correctly implements transaction isolation levels with visible effects of different choices
4. Provides meaningful and educational explanations for query execution decisions
5. Simulates realistic database performance issues that students can diagnose and resolve
6. Supports progressive learning from basic to advanced database concepts
7. Integrates smoothly with common educational environments like Jupyter notebooks
8. Includes comprehensive documentation and examples for instructors to build upon
9. Demonstrates all ACID properties visibly and accurately
10. Maintains conceptual accuracy while simplifying implementation for educational clarity