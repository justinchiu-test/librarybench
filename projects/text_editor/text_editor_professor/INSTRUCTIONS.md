# Educational Text Editor Analytics Library

## Overview
A specialized text editor library designed for programming education that exposes the internal workings of text manipulation algorithms. This implementation focuses on algorithm visualization, performance metrics, and comparing different text storage implementations, enabling programming professors to demonstrate the practical implications of data structure choices in text editing.

## Persona Description
Dr. Martinez teaches advanced programming courses and researches text manipulation algorithms. She wants to use a self-implemented editor as both a teaching tool for data structures and as her daily driver to deeply understand the practical implications of algorithm choices.

## Key Requirements
1. **Algorithm Visualization Engine**: Implement a tracing and visualization system that records and displays internal data structure operations during editing. This is critical for demonstrating to students how algorithms like piece tables or ropes actually manipulate text during common editing operations.

2. **Multiple Text Storage Implementation Framework**: Create a pluggable architecture supporting different text storage algorithms (gap buffer, piece table, rope) with a common interface. Dr. Martinez needs to switch between implementations during lectures to compare their behaviors and performance characteristics.

3. **Performance Instrumentation System**: Develop a comprehensive metrics collection and reporting system that captures real-time performance data on operations like insert, delete, search, and navigation. This allows students to empirically analyze algorithm efficiency instead of relying solely on theoretical complexity.

4. **Custom Algorithm Extension API**: Design a well-documented API that allows new text storage algorithms to be implemented and plugged into the editor. This enables assignments where students implement their own algorithms and directly compare them against reference implementations.

5. **Academic Documentation Generator**: Create a system that can automatically generate explanatory documentation from the actual implementation code, including algorithm flowcharts, data structure state diagrams, and performance comparison reports for educational use.

## Technical Requirements
- **Testability Requirements**:
  - All visualization and metrics components must be testable with simulated editing operations
  - The algorithm switching mechanism must maintain document integrity during transitions
  - Documentation generation must produce consistent results for identical inputs
  - Extension API must validate student implementations against correctness criteria

- **Performance Expectations**:
  - Visualization overhead should not slow editing operations by more than 20%
  - Metrics collection should have minimal impact on the measured operations
  - The system should handle files up to 10MB while maintaining visualization capabilities
  - Algorithm comparisons should be accurate enough for educational purposes

- **Integration Points**:
  - Support for exporting visualization data to common formats (JSON, CSV)
  - Integration with Jupyter notebooks for interactive educational demonstrations
  - Python API allowing programmatic manipulation of text through different algorithms
  - Documentation generation pipeline compatible with common academic publishing tools

- **Key Constraints**:
  - All algorithms must be implemented in pure Python for educational clarity
  - Implementations should prioritize transparency over optimization when necessary
  - The system must work without any UI components, focusing on the algorithmic core
  - Code must be well-documented for educational purposes

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The text editor library should implement:

1. **Text Storage Core**: Multiple implementations of text storage (gap buffer, piece table, rope) with a common interface.

2. **Operation Recording**: A system to record and replay operations performed on the text buffer.

3. **Metrics Collection**: Instrumentation points throughout the codebase to gather performance data.

4. **Algorithm Visualization**: A system to represent the internal state changes of data structures during operations.

5. **Plugin Architecture**: A well-defined API for extending the system with new algorithms.

6. **Documentation Generation**: Tools to automatically generate educational materials from implementation code.

7. **Comparative Analysis**: Utilities for running identical operations across different implementations and comparing results.

The library should use dependency injection to allow easy switching between text storage implementations. Each algorithm should provide hooks for inspection of its internal state, and operations should be recordable and replayable for educational purposes.

## Testing Requirements
- **Key Functionalities to Verify**:
  - Correctness of all text manipulation operations across all implementations
  - Accuracy of performance metrics collection
  - Consistency of algorithm visualization output
  - Integrity of the extension API when adding new implementations
  - Quality and accuracy of generated documentation

- **Critical User Scenarios**:
  - Switching between implementations mid-editing without data loss
  - Performing complex edit sequences and verifying internal state visualization
  - Adding custom algorithm implementations through the extension API
  - Generating educational materials from actual code execution
  - Comparing performance metrics across different implementations

- **Performance Benchmarks**:
  - Basic editing operations (insert, delete) should complete within 10ms for files under 1MB
  - Algorithm switching should not take more than 500ms for files under 5MB
  - Visualization generation should complete within 1 second
  - Documentation generation should process the entire codebase in under 30 seconds

- **Edge Cases and Error Conditions**:
  - Handling malformed custom algorithm implementations
  - Recovering from errors during algorithm transitions
  - Managing visualization for extremely large operations (e.g., pasting megabytes of text)
  - Properly reporting performance when operations take longer than expected

- **Required Test Coverage**:
  - 95% line coverage for core algorithm implementations
  - 90% line coverage for visualization and metrics components
  - 100% coverage for API contracts and interfaces
  - Comprehensive tests for all documented educational examples

IMPORTANT: 
- ALL functionality must be testable via pytest without any manual intervention
- Tests should verify behavior against requirements, not implementation details
- Tests should be designed to validate the WHAT (requirements) not the HOW (implementation)
- Tests should be comprehensive enough to verify all aspects of the requirements
- Tests should not assume or dictate specific implementation approaches

## Success Criteria
The implementation will be considered successful if:

1. All three text storage algorithms (gap buffer, piece table, rope) are correctly implemented and interchangeable.

2. The visualization system accurately depicts the internal operations of each algorithm in a format suitable for educational use.

3. Performance metrics provide statistically significant data for comparing algorithm efficiency.

4. Custom algorithms can be implemented and plugged into the system through the extension API.

5. Generated documentation is accurate, educational, and represents the actual implementation details.

6. All tests pass, demonstrating the correctness of the implementation and its educational value.

7. The library can be used to empirically demonstrate the theoretical advantages and disadvantages of different text storage algorithms.

To set up the virtual environment, use `uv venv` from within the project directory. The environment can be activated with `source .venv/bin/activate`.