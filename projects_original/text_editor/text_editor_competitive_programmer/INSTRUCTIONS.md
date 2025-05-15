# Competitive Programming Text Editor

A specialized text editor library optimized for competitive programming with advanced code templating and testing capabilities.

## Overview

This project implements a text editor library specifically designed for competitive programmers who need extremely efficient text manipulation with minimal keystrokes and specialized features for algorithmic problem-solving. It provides code templates, input/output testing, timing-aware features, algorithm libraries, and keystroke efficiency analysis.

## Persona Description

Miguel participates in programming competitions where editing speed directly impacts performance. He needs extremely efficient text manipulation with minimal keystrokes and specialized features for algorithmic problem-solving.

## Key Requirements

1. **Code Template System**: Implement a flexible template system with parameterized snippets for common algorithmic patterns. This is critical for Miguel to rapidly insert optimized implementations of standard algorithms (sorting, searching, graph traversal, etc.) without writing them from scratch during time-constrained competitions.

2. **Input/Output Testing Panel**: Develop functionality to quickly validate code solutions against test cases, showing both expected and actual outputs. This allows Miguel to immediately verify his solutions during practice and competitions, catching edge cases or logical errors before submission.

3. **Timing-Aware Features**: Create competition-specific timing features that adapt to contest duration and problem constraints. This helps Miguel manage his time effectively during competitions, prioritizing problems appropriately and ensuring he doesn't spend too long on any single challenge.

4. **Algorithm Library**: Implement a searchable collection of common competitive programming algorithms and data structures with instant access. This provides Miguel with reference implementations of complex algorithms (dynamic programming, network flow, etc.) that can be quickly adapted to specific problems.

5. **Keystroke Efficiency Analyzer**: Develop a system that analyzes coding patterns and suggests shorter command sequences for common operations. This helps Miguel continuously improve his coding efficiency by identifying repetitive patterns that could be automated or shortened.

## Technical Requirements

### Testability Requirements
- Template expansion must be verifiable with predetermined inputs and expected outputs
- Testing functionality must be mockable with fixed input/output examples
- Timing features must be testable with simulated contest durations
- Algorithm library access must be testable through defined retrieval operations
- Keystroke efficiency analysis must be testable with recorded keystroke sequences

### Performance Expectations
- Template expansion must complete in under 10ms
- Test case execution must support problems with up to 1 million operations in under 1 second
- Time tracking must have millisecond precision
- Algorithm library searches must return results in under 50ms
- Keystroke analysis must process at least 10,000 operations per second

### Integration Points
- Code execution environment for testing solutions
- Algorithm database for storing and retrieving implementations
- Performance profiling for solution optimization
- Input/output validation against expected results
- Keystroke recording and analysis system

### Key Constraints
- No UI/UX components; all functionality should be implemented as library code
- Must work entirely through API calls without requiring mouse interaction
- All operations must be optimized for minimal keystrokes
- Solution testing must run in sandboxed environment for security
- Compatible with Python 3.8+ ecosystem

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The library should implement a text editor core with the following functionality:

1. A template system that:
   - Stores and manages parameterized code snippets
   - Supports quick template insertion with parameter substitution
   - Allows template customization and creation
   - Organizes templates by algorithm type and complexity

2. A testing system that:
   - Executes code against provided test cases
   - Compares outputs with expected results
   - Measures execution time and memory usage
   - Highlights differences between actual and expected outputs

3. A timing management system that:
   - Tracks time spent on each problem
   - Adapts to competition-specific time constraints
   - Provides time-based recommendations for problem prioritization
   - Alerts when time thresholds are reached

4. An algorithm library that:
   - Provides organized access to common competitive programming algorithms
   - Supports searching and filtering by algorithm characteristics
   - Includes usage examples and complexity information
   - Allows quick adaptation to specific problems

5. A keystroke efficiency system that:
   - Records and analyzes editing patterns
   - Identifies repeated operations that could be optimized
   - Suggests shortcuts or macros for common sequences
   - Tracks efficiency improvements over time

## Testing Requirements

### Key Functionalities to Verify
- Templates correctly expand with provided parameters
- Testing system accurately validates solutions against test cases
- Timing features properly track and manage competition time constraints
- Algorithm library successfully retrieves appropriate implementations
- Keystroke analyzer correctly identifies optimization opportunities

### Critical User Scenarios
- Solving a competitive programming problem from start to finish
- Using templates to quickly implement standard algorithms
- Testing a solution against multiple test cases with varying inputs
- Finding and adapting an algorithm from the library
- Improving editing efficiency based on keystroke analysis

### Performance Benchmarks
- Template expansion should handle at least 100 templates per second
- Test execution should support at least 100 test cases in rapid succession
- Timing system should maintain accurate tracking with less than 10ms deviation
- Algorithm library should support a collection of at least 100 algorithms with sub-50ms retrieval
- Keystroke analysis should process at least 1000 keystrokes per second

### Edge Cases and Error Conditions
- Handling template expansion with invalid parameters
- Managing test cases that cause infinite loops or excessive resource usage
- Dealing with competition timing in various formats and constraints
- Handling very large algorithm implementations
- Analyzing complex or unusual keystroke patterns

### Required Test Coverage Metrics
- Minimum 90% code coverage across all core modules
- 100% coverage of template expansion code
- Complete coverage of all public API methods
- All algorithm types in the library must have test coverage
- All timing and tracking features must have verification tests

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

1. The template system enables rapid insertion of common algorithms with parameter customization
2. The testing system accurately validates solutions against provided test cases
3. The timing features effectively manage competition time constraints
4. The algorithm library provides quick access to optimized implementations
5. The keystroke efficiency analyzer successfully identifies opportunities for improvement

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

## Environment Setup

To set up the development environment:

1. Create a virtual environment:
   ```
   uv venv
   ```

2. Activate the virtual environment:
   ```
   source .venv/bin/activate
   ```

3. Install the project in development mode:
   ```
   uv pip install -e .
   ```

4. CRITICAL: For running tests and generating the required json report:
   ```
   pip install pytest-json-report
   pytest --json-report --json-report-file=pytest_results.json
   ```

REMINDER: Generating and providing pytest_results.json is a critical requirement for project completion.