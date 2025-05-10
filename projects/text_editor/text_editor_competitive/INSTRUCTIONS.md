# Speed-Optimized Competitive Programming Editor

## Overview
A high-performance text editing library specifically designed for competitive programming scenarios. This implementation focuses on maximizing coding efficiency through templates, integrated testing, competition time awareness, algorithm libraries, and keystroke optimization to gain crucial time advantages during coding competitions.

## Persona Description
Miguel participates in programming competitions where editing speed directly impacts performance. He needs extremely efficient text manipulation with minimal keystrokes and specialized features for algorithmic problem-solving.

## Key Requirements

1. **Code Template System with Parameterized Snippets**
   - Implement a sophisticated template engine for common algorithmic patterns with parameter customization
   - Critical for Miguel as it enables rapid implementation of standard algorithms (graph traversal, dynamic programming, etc.) without rewriting boilerplate code
   - Must support variable substitution, optional sections, and intelligent insertion based on context

2. **Input/Output Testing Panel**
   - Develop an integrated testing framework for validating solutions against test cases
   - Essential for verifying correctness of solutions before submission, reducing penalties for incorrect answers
   - Must efficiently parse problem inputs, execute code against them, and verify outputs without disrupting the coding workflow

3. **Timing-Aware Features**
   - Create a competition clock system that adapts editor behavior based on remaining time
   - Crucial for optimizing strategy during competitions with strict time limits, enabling appropriate risk assessment
   - Must provide timing statistics, warnings, and behavior modifications as the competition deadline approaches

4. **Algorithm Library with Searchable Implementations**
   - Develop a comprehensive database of algorithm implementations relevant to competitive programming
   - Allows rapid access to optimized implementations of complex algorithms, saving valuable implementation time
   - Must include search functionality by algorithm type, problem pattern, and complexity characteristics

5. **Keystroke Efficiency Analyzer**
   - Build a system that analyzes common editing patterns and suggests shorter command sequences
   - Helps Miguel continuously improve his editing efficiency, reducing the time spent on non-algorithmic tasks
   - Must learn from usage patterns and provide actionable recommendations for faster text manipulation

## Technical Requirements

### Testability Requirements
- Template system must be testable with various algorithm patterns and substitution scenarios
- Testing framework must be verifiable with sample problems and solutions
- Timing features must be testable with simulated competition scenarios
- Algorithm library must be testable for search accuracy and result relevance
- Keystroke analysis must be quantifiably testable for efficiency improvements

### Performance Expectations
- Template insertion and parameter substitution must complete in under 50ms
- Test execution and validation must run within 200ms for typical problem sizes
- Algorithm search must return results in under 100ms
- Keystroke analysis must not impact editor performance (background operation)
- All operations must prioritize responsiveness, with minimal latency (<20ms)

### Integration Points
- Code execution engine for testing solutions
- Timer system for competition phase tracking
- Algorithm categorization framework
- Keystroke recording and analysis system
- Template engine with parameter substitution

### Key Constraints
- All functionality must be accessible programmatically with no UI dependencies
- Operations must be extremely performant, optimizing for speed at every level
- Memory usage must be minimal to ensure stable performance
- The system must function without external dependencies during competitions
- Data structures must be optimized for the specific access patterns of competitive programming

## Core Functionality

The implementation should provide a comprehensive competitive programming editing library with:

1. **Template Management System**
   - Parameterized code template storage and retrieval
   - Context-aware template suggestion
   - Template customization and version management
   - Intelligent parameter substitution

2. **Solution Testing Framework**
   - Input parsing and standardization
   - Solution execution with resource constraints
   - Output validation and comparison
   - Test case management and generation

3. **Competition Time Management**
   - Countdown timer with phase awareness
   - Time-based feature adaptation
   - Progress tracking relative to competition phases
   - Optimal time allocation suggestions

4. **Algorithm Knowledge Base**
   - Categorized algorithm implementations
   - Search by complexity, type, and application
   - Usage examples and variations
   - Complexity and constraint information

5. **Editing Efficiency System**
   - Command usage analysis
   - Efficiency metrics and benchmarking
   - Alternative command suggestion
   - Personal efficiency trend analysis

## Testing Requirements

### Key Functionalities to Verify
- Correct template processing and parameter substitution
- Accurate testing of solutions against various input cases
- Proper timing functions and competition phase awareness
- Relevant algorithm retrieval based on search criteria
- Meaningful keystroke efficiency recommendations

### Critical User Scenarios
- Solving a complex algorithmic problem under time pressure
- Quick implementation of a graph algorithm from templates
- Testing a solution against multiple input cases
- Finding an appropriate algorithm for a specific problem constraint
- Adapting strategy based on remaining competition time

### Performance Benchmarks
- Template insertion with substitution must complete in <50ms
- Testing a solution against 10 test cases must complete in <2s
- Algorithm search must return results in <100ms for any query
- Editor operations must maintain <20ms latency at all times
- Memory usage must remain below 100MB during extended sessions

### Edge Cases and Error Conditions
- Very large input test cases
- Infinite loops in submitted code
- Resource-exhausting algorithms
- Template substitution with invalid parameters
- Competition time running out during critical operations

### Required Test Coverage Metrics
- >95% code coverage for template system
- >90% coverage for testing framework
- >85% coverage for timing features
- >90% coverage for algorithm library
- >90% overall project coverage

## Success Criteria
- Measurable reduction in time required to implement standard algorithms
- Higher success rate in test case validation before submission
- Improved time management during competition phases
- Faster access to appropriate algorithms for specific problems
- Continuous improvement in coding efficiency through keystroke optimization
- Miguel achieves better competition results through optimized coding workflow

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

Focus on implementing the core functionality as library components with well-defined APIs. Remember that this implementation should have NO UI components and should be designed for testing under simulated competition conditions.