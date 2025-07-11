# PyTermGame - Educational Game Engine

## Overview
A terminal-based game engine designed specifically for creating educational games that teach programming concepts through interactive visualizations and gamified learning experiences, making computer science education engaging and accessible.

## Persona Description
A computer science teacher creating educational games to teach programming concepts who needs visual representations of algorithms and data structures. She wants to make learning interactive and engaging through terminal-based visualizations.

## Key Requirements
1. **Algorithm visualization components (sorting, pathfinding)** - Essential for demonstrating how algorithms work step-by-step, supporting bubble sort, quicksort, merge sort, A*, Dijkstra's algorithm, and binary search with visual representation of data movement and comparisons.

2. **Step-by-step execution mode with breakpoints** - Critical for allowing students to control pacing of algorithm execution, set breakpoints at specific operations, inspect variable states at each step, and understand the flow of complex algorithms.

3. **Student progress tracking and hints system** - Provides personalized learning by tracking which concepts students struggle with, offering contextual hints based on errors, maintaining completion statistics, and adapting difficulty based on performance.

4. **Puzzle validation framework for assignments** - Enables automated checking of student solutions, supports multiple correct approaches, provides detailed feedback on incorrect attempts, and integrates with gradebook systems for assessment.

5. **Code sandbox integration for in-game programming** - Allows students to write and test code within the game environment, execute Python snippets safely, visualize code execution results, and complete programming challenges with immediate feedback.

## Technical Requirements
- **Testability requirements**: All educational components must be verifiable for correctness, visualization steps must be deterministic, progress tracking must accurately record student interactions, sandbox execution must be secure and isolated
- **Performance expectations**: Algorithm visualizations must render smoothly with configurable speed, support datasets up to 1000 elements, instant feedback on puzzle validation, minimal latency in code execution
- **Integration points**: Plugin system for adding new algorithms and visualizations, export functionality for progress reports, API for external gradebook integration, customizable curriculum paths
- **Key constraints**: Must work in standard terminal environments without special permissions, secure sandbox preventing system access, all visualizations must be ASCII-based, no external dependencies

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The engine must provide comprehensive educational game features including:
- Algorithm visualizer supporting step-by-step execution with variable inspection and operation highlighting
- Interactive puzzle system with multiple puzzle types (code completion, debugging, algorithm selection)
- Progress tracker maintaining student profiles, concept mastery levels, and learning analytics
- Hint engine providing contextual assistance based on student actions and common misconceptions
- Code sandbox with secure execution environment, syntax highlighting simulation, and output capture
- Lesson framework supporting sequential curriculum, prerequisite checking, and adaptive difficulty
- Assessment tools for creating quizzes, coding challenges, and project-based evaluations

## Testing Requirements
Define comprehensive test coverage including:
- **Key functionalities that must be verified**:
  - Algorithm visualizations accurately represent each step of execution
  - Progress tracking correctly records all student interactions
  - Puzzle validation accepts all correct solutions and rejects incorrect ones
  - Hint system provides appropriate guidance for common errors
  - Code sandbox safely executes student code without system access

- **Critical user scenarios that should be tested**:
  - Complete lesson sequence from introduction to assessment
  - Algorithm visualization with pause, resume, and step controls
  - Puzzle solving with hints and multiple attempts
  - Code writing and execution in sandbox environment
  - Progress review and report generation

- **Performance benchmarks that must be met**:
  - Visualize sorting of 100 elements at 30 FPS equivalent
  - Validate puzzle solutions within 100ms
  - Execute sandbox code within 500ms timeout
  - Load student progress in under 200ms
  - Generate progress reports in under 1 second

- **Edge cases and error conditions that must be handled properly**:
  - Invalid student code execution
  - Infinite loops in sandbox
  - Corrupted progress data recovery
  - Network issues during progress sync
  - Memory limits in visualizations

- **Required test coverage metrics**:
  - Minimum 95% code coverage for educational components
  - All algorithms must have correctness tests
  - Security tests for sandbox isolation
  - Integration tests for complete lessons

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
Clear metrics indicating successful implementation:
- Algorithm visualizations correctly demonstrate all supported algorithms with accurate step-by-step execution
- Student progress tracking provides meaningful insights into learning patterns and concept mastery
- Puzzle validation framework accurately assesses student solutions with helpful feedback
- Code sandbox safely executes student code while preventing system access or resource abuse
- Complete educational game can guide students through programming concept mastery

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

## Environment Setup
Use `uv venv` to setup virtual environments. From within the project directory, the environment can be activated with `source .venv/bin/activate`. Install the project with `uv pip install -e .`.

CRITICAL: Running tests with pytest-json-report and providing the pytest_results.json file is MANDATORY:
```
pip install pytest-json-report
pytest --json-report --json-report-file=pytest_results.json
```