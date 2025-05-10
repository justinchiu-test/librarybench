# Educational Database Demonstrator (EDD)

## Overview
EDD is a transparent in-memory database specifically designed for teaching database concepts. It provides visual and interactive insights into database operations, query execution plans, indexing strategies, and transaction isolation levels, making complex database principles accessible and observable for computer science students.

## Persona Description
Dr. Chen teaches database concepts to computer science students. She needs a transparent database implementation that clearly illustrates core concepts without the complexity of production systems.

## Key Requirements

1. **Step-by-step query execution visualization**
   - Essential for making abstract query processing concepts concrete and observable for students
   - Provides visual breakdown of each operation in the query execution plan
   - Shows how data flows through different stages of query processing (parsing, planning, execution)
   - Demonstrates how different query optimizations affect execution paths
   - Critical for helping students understand the relationship between query syntax and execution strategy

2. **Configurable performance degradation modes**
   - Enables simulation of real-world database issues in a controlled environment
   - Allows students to experience and troubleshoot common performance problems
   - Demonstrates how different factors (missing indexes, poor join order, etc.) impact query performance
   - Provides hands-on scenarios for students to practice database optimization techniques
   - Essential for developing practical database tuning skills beyond theoretical knowledge

3. **Side-by-side comparison of indexing strategies**
   - Shows performance differences between various indexing approaches (B-tree, hash, etc.)
   - Provides visual representation of index structures and how they organize data
   - Demonstrates access patterns and operation counts for different query types
   - Includes metrics on index creation cost, storage overhead, and query performance benefits
   - Critical for teaching the trade-offs involved in index selection and design

4. **Interactive transaction isolation demonstrations**
   - Illustrates ACID properties and different isolation levels (read uncommitted, serializable, etc.)
   - Shows concurrency effects like dirty reads, non-repeatable reads, and phantom reads
   - Provides visualization of transaction timelines and conflict resolution
   - Demonstrates locking strategies and their impact on concurrent operations
   - Essential for understanding the subtleties of transaction management and database consistency

5. **Simplified SQL dialect for pedagogical progression**
   - Provides a streamlined syntax focused on essential concepts without overwhelming complexity
   - Follows a carefully designed learning progression that builds complexity incrementally
   - Includes clear error messages with educational explanations and suggestions
   - Supports annotations linking SQL constructs to relevant database theory
   - Critical for building student confidence and understanding before introducing full SQL complexity

## Technical Requirements

### Testability Requirements
- All components must be unit-testable with clear boundaries
- Visual components must support automated verification of correct operation
- Must support deterministic execution for reproducible demonstrations
- Test suite must verify correctness of educational examples and demonstrations
- Should include validation tests to ensure accurate representation of database concepts

### Performance Expectations
- Default mode should provide response times suitable for classroom demonstration (<1 second)
- Should support databases large enough to demonstrate performance principles but small enough for classroom use
- Visualization components should update in real-time during demonstrations
- Degradation modes should be configurable to show performance impacts without excessive wait times
- Should scale appropriately on standard classroom computing resources

### Integration Points
- Must provide Python API for easy integration with educational notebooks
- Should export visualization data in standard formats for custom rendering
- Must support import/export of datasets for classroom exercises
- Should provide hooks for custom educational extensions
- Must allow integration with automated grading systems

### Key Constraints
- Implementation must prioritize conceptual clarity over performance
- Code organization must align with database theory concepts for educational mapping
- Complexity must be manageable for student comprehension
- Must operate without external dependencies beyond standard Python libraries
- Visual representations must be accurate depictions of the underlying concepts

## Core Functionality

The core functionality of EDD includes:

1. **Transparent Database Engine**
   - Fully observable query planning and execution
   - Access to internal representations of database objects
   - Clear separation of database engine components (parser, optimizer, executor)
   - Detailed logging of all internal operations

2. **Educational Visualization Framework**
   - Step-by-step visualization of query execution
   - Visual representation of data structures and indexes
   - Timeline views for transaction processing
   - Performance metric visualization
   - Comparative views for different strategies

3. **Pedagogical SQL Interpreter**
   - Simplified SQL dialect with progressive complexity
   - Enhanced error messages with educational content
   - Syntax highlighting aligned with conceptual components
   - Support for query annotations and explanations

4. **Configurable Performance Characteristics**
   - Simulated disk I/O constraints
   - Memory limitation options
   - Artificial processing delays
   - Configurable optimization levels
   - Simulation of common performance problems

5. **Transaction Management System**
   - Visible isolation level effects
   - Interactive concurrency demonstrations
   - Locking visualizations
   - Deadlock detection and resolution
   - Recovery mechanism demonstrations

## Testing Requirements

### Key Functionalities to Verify
- Accuracy of all execution visualizations compared to actual operations
- Correctness of query results across all SQL features
- Proper implementation of all isolation levels
- Accuracy of index operations and structure representations
- Correct behavior of performance degradation modes

### Critical User Scenarios
- Students following tutorial sequences for progressive learning
- Instructor demonstrating concepts in live classroom settings
- Students experimenting with different query formulations
- Comparative analysis of different database strategies
- Troubleshooting exercises for simulated performance issues

### Performance Benchmarks
- Visualization updates should occur within 500ms for classroom usability
- Should handle databases up to 100,000 records without significant delay
- Maximum 2-second response time for complex query explanations
- Interface should remain responsive during all demonstrations
- Performance degradation modes should scale predictably

### Edge Cases and Error Conditions
- Handling of invalid SQL with informative error messages
- Behavior with edge case data (empty tables, extreme values)
- Graceful handling of resource limitations
- Response to deliberately poor query construction
- Recovery from simulated failure scenarios

### Required Test Coverage Metrics
- 100% coverage of educational demonstration scenarios
- 95% code coverage for core engine components
- Complete coverage of all SQL dialect features
- Comprehensive testing of all visualization components
- Full verification of all transaction isolation levels

## Success Criteria

1. **Educational Effectiveness**
   - Students demonstrate improved understanding of database concepts
   - Complex concepts become tangibly observable through visualizations
   - Progressive learning path successfully builds student knowledge
   - Abstract concepts are successfully translated into visible operations

2. **Functional Completeness**
   - All five key requirements fully implemented and tested
   - Complete coverage of core database concepts in the curriculum
   - All visualizations accurately represent underlying operations
   - SQL dialect covers all required educational concepts

3. **Usability for Instructors**
   - Can be effectively used in classroom demonstrations
   - Provides clear, visible examples of all key concepts
   - Supports common educational workflows
   - Reduces time needed to explain complex concepts

4. **Student Engagement**
   - Interactive elements successfully engage students with the material
   - Visualizations provide "aha moments" for understanding complex concepts
   - Error messages and guidance successfully help students learn
   - Performance comparisons effectively demonstrate optimization principles

5. **Technical Robustness**
   - Reliable operation in classroom environments
   - Graceful handling of student errors and edge cases
   - Consistent behavior across different operating systems
   - Appropriate performance for educational use cases

## Getting Started

To setup and run this project, follow these steps:

1. Initialize the project with uv:
   ```
   uv init --lib
   ```

2. Install project dependencies:
   ```
   uv sync
   ```

3. Run your code:
   ```
   uv run python script.py
   ```

4. Run tests:
   ```
   uv run pytest
   ```

5. Format code:
   ```
   uv run ruff format
   ```

6. Lint code:
   ```
   uv run ruff check .
   ```

7. Type check:
   ```
   uv run pyright
   ```