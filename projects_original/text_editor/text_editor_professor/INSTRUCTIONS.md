# Educational Algorithm-Focused Text Editor

A specialized text editor library designed for teaching and researching text manipulation algorithms with visualization capabilities.

## Overview

This project implements a text editor library specifically designed for teaching and researching text manipulation algorithms. It provides algorithm visualization, multiple text storage algorithm implementations, performance measurement, a custom data structure extension API, and academic documentation generation capabilities.

## Persona Description

Dr. Martinez teaches advanced programming courses and researches text manipulation algorithms. She wants to use a self-implemented editor as both a teaching tool for data structures and as her daily driver to deeply understand the practical implications of algorithm choices.

## Key Requirements

1. **Algorithm Visualization Mode**: Implement a system that can visually represent the internal operations of text data structures during editing actions. This is critical for Dr. Martinez to demonstrate to students how algorithms like piece tables or ropes function internally when text is inserted, deleted, or modified.

2. **Multiple Implementation Toggle**: Create a mechanism to switch between different text storage algorithms (gap buffer, piece table, rope) at runtime. This allows Dr. Martinez to directly compare algorithm performance characteristics and teach students about the trade-offs between different approaches.

3. **Performance Instrumentation**: Develop comprehensive metrics collection and reporting for all text operations, measuring time complexity and memory usage. This enables empirical analysis of algorithmic efficiency for research purposes and provides real-world examples for teaching.

4. **Custom Data Structure Extension API**: Design an extensible API that allows new text storage algorithms to be implemented and plugged into the editor. This is essential for Dr. Martinez's students to implement their own algorithms as part of coursework and see them function within a real editor.

5. **Academic Documentation Generator**: Create functionality to generate explanatory materials from the actual implementation, including algorithm visualizations, performance comparisons, and code annotations. This helps Dr. Martinez create high-quality teaching materials directly from working code.

## Technical Requirements

### Testability Requirements
- All algorithm operations must be independently testable without UI components
- Visualization events must be capturable and verifiable through the testing framework
- Performance metrics must be quantifiable and comparable across algorithms
- Extension API must be verifiable through the creation of mock algorithms

### Performance Expectations
- Efficient handling of files up to 10MB in size for in-class demonstrations
- Performance metrics collection with minimal overhead (<5% impact on operation speed)
- Algorithm switching must preserve document state completely
- Rendering of algorithm visualization data should complete in under 50ms

### Integration Points
- API for plugging in custom student-implemented data structures
- Metrics export system for external analysis tools
- Documentation generation output in markdown and HTML formats
- Support for algorithm animation data export

### Key Constraints
- No UI/UX components; all functionality should be implemented as library code
- All visualization must be data-driven rather than rendering directly
- Focus on educational clarity over maximum possible performance
- Compatible with Python 3.8+ ecosystem

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The library should implement a text editor core with the following functionality:

1. A text buffer system that supports:
   - Multiple interchangeable implementations (gap buffer, piece table, rope)
   - Full range of text operations (insert, delete, replace, etc.)
   - Event emission for all operations to enable visualization

2. An algorithm visualization system that:
   - Captures internal state changes during text operations
   - Provides data representations of algorithm behavior
   - Supports step-by-step inspection of operations

3. A performance monitoring system that:
   - Collects timing and memory metrics for all operations
   - Compares performance across different algorithm implementations
   - Provides reporting capabilities for analysis

4. An extension API that:
   - Allows implementation of new text storage algorithms
   - Provides clear interfaces for essential text operations
   - Supports automatic integration with visualization and metrics systems

5. A documentation generator that:
   - Extracts implementation details and algorithm descriptions
   - Creates visualizations of algorithm behavior
   - Generates teaching materials with code annotations

## Testing Requirements

### Key Functionalities to Verify
- Text operations (insert, delete, etc.) work correctly across all algorithm implementations
- Algorithm visualization correctly represents the internal state during operations
- Performance metrics accurately measure and report operation efficiency
- Custom algorithms can be implemented and integrated via the extension API
- Documentation generation produces accurate and useful teaching materials

### Critical User Scenarios
- Switching between text storage algorithms while preserving document state
- Capturing and replaying a sequence of operations with visualization
- Comparing performance metrics across different algorithms on the same operations
- Implementing and integrating a new text storage algorithm
- Generating documentation for a specific algorithm or operation

### Performance Benchmarks
- Text operations should complete within specified complexity bounds (O(log n) for rope operations, etc.)
- Algorithm switching should complete in under 100ms for documents up to 1MB
- Memory usage should remain within 2x the optimal for each algorithm type
- Documentation generation should complete in under 5 seconds for full codebase

### Edge Cases and Error Conditions
- Handling very large files (10MB+) without excessive memory usage
- Gracefully managing invalid operations or cursor positions
- Properly handling algorithm switching during ongoing operations
- Recovering from errors in custom implemented algorithms
- Dealing with malformed or incomplete documentation annotations

### Required Test Coverage Metrics
- Minimum 90% code coverage across all core modules
- 100% coverage of algorithm implementation code
- Complete coverage of all public API methods
- All documented features must have corresponding tests

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

1. All three text storage algorithms (gap buffer, piece table, rope) are correctly implemented with the ability to switch between them at runtime
2. Algorithm visualization data is properly generated for all operations
3. Performance metrics show accurate measurements across different algorithms
4. The extension API successfully supports custom algorithm implementations
5. Documentation generation produces useful teaching materials from the code

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