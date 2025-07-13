# PyTermGame - Puzzle Game Engine

## Overview
A terminal-based game engine specialized for creating logic-based puzzle games with grid systems, puzzle validation, generation algorithms, and comprehensive hint systems for engaging brain-teasing experiences.

## Persona Description
A puzzle game enthusiast creating logic-based games who needs grid systems and puzzle validation. He requires tools for creating and validating various types of puzzles with increasing difficulty.

## Key Requirements
1. **Grid-based puzzle framework with validation** - Essential for supporting various puzzle types like Sudoku, crosswords, nonograms, and sliding puzzles with automatic validation of solutions, constraint checking, and support for irregular grid shapes and sizes.

2. **Puzzle generator with difficulty scaling** - Critical for providing endless content by algorithmically creating solvable puzzles, adjusting difficulty based on technique requirements, ensuring unique solutions, and maintaining consistent challenge progression.

3. **Hint system with progressive reveals** - Provides player assistance without spoiling the experience through subtle hints, technique suggestions, partial solution reveals, mistake highlighting, and adaptive hint generation based on player struggle patterns.

4. **Move history with undo/redo functionality** - Enables experimentation and learning by tracking all player actions, supporting unlimited undo/redo, bookmarking interesting states, branching history for exploration, and replay functionality for solved puzzles.

5. **Puzzle sharing and import/export system** - Facilitates community engagement through standardized puzzle formats, compression for efficient sharing, validation of imported puzzles, rating and difficulty metadata, and collection management.

## Technical Requirements
- **Testability requirements**: Puzzle generators must produce solvable puzzles 100% of the time, validation logic must correctly identify all valid/invalid states, hint system must provide helpful guidance, difficulty scaling must be measurable
- **Performance expectations**: Generate medium complexity puzzles in under 500ms, validate solutions in under 10ms, undo/redo operations instantaneous, support grids up to 100x100
- **Integration points**: Plugin system for new puzzle types, solver algorithm framework, custom validation rules, import/export format adapters
- **Key constraints**: All puzzles must be solvable through logic alone, no guessing required, terminal-friendly visualization, efficient memory usage for large grids

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The engine must provide comprehensive puzzle game features including:
- Grid manager supporting rectangular, hexagonal, and irregular layouts with cell relationships
- Puzzle generator implementing various creation algorithms with difficulty control
- Constraint validator checking puzzle rules, conflicts, and solution uniqueness
- Hint engine analyzing puzzle state and suggesting next logical moves
- History tracker maintaining complete move history with branch support
- Solver framework implementing various solution techniques for validation
- Import/export system supporting multiple puzzle formats with compression

## Testing Requirements
Define comprehensive test coverage including:
- **Key functionalities that must be verified**:
  - Puzzle generators create valid, solvable puzzles with unique solutions
  - Validation correctly identifies legal and illegal moves
  - Hint system provides appropriate guidance without revealing solutions
  - Move history accurately tracks and reverses all actions
  - Import/export maintains puzzle integrity across formats

- **Critical user scenarios that should be tested**:
  - Complete puzzle solving from empty to solution
  - Using hints to overcome difficult sections
  - Undoing mistakes and trying alternative approaches
  - Generating puzzles of varying difficulties
  - Sharing and importing community puzzles

- **Performance benchmarks that must be met**:
  - Generate easy puzzle in under 100ms
  - Generate hard puzzle in under 1000ms
  - Validate 9x9 grid in under 5ms
  - Process 1000 undo operations in under 100ms
  - Import/export puzzle in under 50ms

- **Edge cases and error conditions that must be handled properly**:
  - Unsolvable puzzle detection
  - Multiple solution scenarios
  - Grid size limits and memory constraints
  - Corrupted import data handling
  - History overflow management

- **Required test coverage metrics**:
  - Minimum 95% code coverage
  - All puzzle types thoroughly tested
  - Solver algorithms validated
  - Generator randomness tested
  - Performance regression suite

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
- Puzzle generator reliably creates solvable puzzles with appropriate difficulty levels
- Validation system accurately enforces all puzzle rules and constraints
- Hint system provides helpful guidance that teaches solving techniques
- Move history enables free experimentation without fear of losing progress
- Import/export system facilitates easy puzzle sharing within the community

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