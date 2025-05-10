# Educational Text Editor with Algorithm Visualization

## Overview
An advanced text editor library designed specifically for teaching and researching text manipulation algorithms. This implementation focuses on algorithm visualization, multiple data structure implementations, and performance instrumentation to serve as both a teaching tool and a practical demonstration of text manipulation theory.

## Persona Description
Dr. Martinez teaches advanced programming courses and researches text manipulation algorithms. She wants to use a self-implemented editor as both a teaching tool for data structures and as her daily driver to deeply understand the practical implications of algorithm choices.

## Key Requirements

1. **Algorithm Visualization Mode**
   - Implement a visualization system that records and outputs internal data structure operations during editing
   - Critical for Dr. Martinez as it allows students to visually understand how text operations affect the underlying data structures, making abstract concepts concrete
   - Must provide step-by-step visual representation of operations like insertions, deletions, and cursor movements

2. **Multiple Text Storage Algorithm Implementation**
   - Develop interchangeable implementations of different text storage algorithms (gap buffer, piece table, rope)
   - Essential for comparing performance characteristics of different approaches and demonstrating algorithm tradeoffs in real-time
   - Must allow toggling between implementations while preserving document state to facilitate direct comparisons

3. **Performance Instrumentation**
   - Create a comprehensive metrics system that displays real-time statistics on operation efficiency
   - Crucial for empirical analysis of algorithm performance under different editing patterns and document sizes
   - Must track and report metrics such as operation latency, memory usage, and complexity calculations

4. **Custom Data Structure Extension API**
   - Design a plugin architecture that allows for student-implemented algorithms to be integrated
   - Enables hands-on learning by allowing students to implement their own data structures and see how they perform in a real editor
   - Must provide clear interfaces for new algorithm implementation with minimal boilerplate

5. **Academic Documentation Generator**
   - Build functionality to automatically generate explanatory materials from the actual implementation
   - Allows creation of teaching materials that are synchronized with the actual code, ensuring accuracy
   - Must be able to extract code samples, performance data, and visualization outputs into formatted documentation

## Technical Requirements

### Testability Requirements
- All algorithms must be testable in isolation from the core editor functionality
- Visualization outputs must be captured in a standardized format for automated verification
- Performance metrics must be collected in a way that allows for statistical analysis and regression testing
- The extension API must have comprehensive test harnesses to verify correct integration

### Performance Expectations
- Editing operations must remain responsive (under 50ms) even with visualization enabled
- Memory usage should be optimized to handle documents of at least 10MB
- Algorithm switching must complete in under 1 second for documents up to 1MB
- Documentation generation should complete in under 30 seconds for the entire codebase

### Integration Points
- Extension API must provide clear interfaces for algorithm plugins
- Visualization system should be able to output to standard formats (SVG, PNG, or JSON)
- Documentation generator should support output to markdown, HTML, and PDF formats
- Performance data should be exportable to CSV or JSON for external analysis

### Key Constraints
- All visualization and metrics must be available via API with no UI dependencies
- The architecture must maintain separation between the text processing algorithms and the instrumentation code
- Implementations must be pedagogically clear, potentially favoring clarity over optimization when necessary
- The system should be designed to work with standard testing tools like pytest

## Core Functionality

The implementation should provide a comprehensive text editing library with:

1. **Core Text Manipulation Engine**
   - Multiple implementations of text storage data structures (gap buffer, piece table, rope)
   - Complete set of editing operations (insert, delete, copy, paste, etc.)
   - Cursor management and selection functionality

2. **Algorithm Visualization System**
   - Event capturing mechanism for all data structure operations
   - Transformation of these events into visual representations
   - Ability to step through operations for educational purposes

3. **Performance Analysis Framework**
   - Metrics collection for key performance indicators
   - Statistical analysis of algorithm efficiency
   - Comparison tools for different implementations

4. **Extension Architecture**
   - Plugin system for new algorithm implementations
   - Interface definitions and abstract classes
   - Example student implementations

5. **Documentation Generation System**
   - Code extraction and formatting
   - Integration of performance data and visualizations
   - Template system for creating educational materials

## Testing Requirements

### Key Functionalities to Verify
- Correct text manipulation across all algorithm implementations
- Accurate visualization of internal operations
- Precise performance metrics collection and reporting
- Successful integration of custom algorithm implementations
- Complete and accurate documentation generation

### Critical User Scenarios
- Loading large files (>5MB) and measuring performance across algorithms
- Performing complex edit operations and verifying visualization correctness
- Switching between algorithm implementations mid-editing
- Integrating a new student-created algorithm implementation
- Generating documentation for a specific algorithm feature

### Performance Benchmarks
- Text insertion/deletion operations should complete in <10ms for files up to 1MB
- Algorithm switching should preserve all document state and complete in <1s
- Visualization overhead should not increase operation time by more than 100%
- Memory usage should not exceed 5x the size of the document being edited
- Documentation generation should process >1000 lines of code per second

### Edge Cases and Error Conditions
- Recovery from failed algorithm implementations
- Handling of extremely large files (>100MB)
- Concurrent modification of the document
- Invalid or malformed extension API usage
- Graceful degradation when performance limits are reached

### Required Test Coverage Metrics
- >90% code coverage for core algorithm implementations
- >85% coverage for visualization and instrumentation code
- 100% interface coverage for the extension API
- >80% overall project coverage

## Success Criteria
- Students demonstrate improved understanding of text editor data structures through visualization
- Performance analysis correctly identifies algorithmic complexity and bottlenecks
- At least three different algorithm implementations can be toggled seamlessly
- Student-implemented algorithms can be integrated with minimal assistance
- Generated documentation is complete, accurate, and pedagogically valuable
- Dr. Martinez can use the editor for both teaching demonstrations and personal use

## Getting Started

To set up your development environment:

```bash
# Create a new virtual environment and install dependencies
uv init --lib

# Run a Python script
uv run python your_script.py

# Run tests
uv run pytest

# Check code quality
uv run ruff check .
uv run pyright
```

Focus on implementing the core functionality as library components with well-defined APIs. Remember that this implementation should have NO UI components and should be designed for testing and educational purposes.