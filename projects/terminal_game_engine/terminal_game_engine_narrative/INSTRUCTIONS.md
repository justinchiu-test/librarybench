# PyTermGame - Narrative Game Engine

## Overview
A terminal-based game engine specialized for creating rich text adventures with complex branching storylines, dynamic dialogue systems, and sophisticated narrative state management for interactive fiction experiences.

## Persona Description
A narrative designer creating text adventures with branching storylines who needs robust dialogue systems and story state management. She requires tools for managing complex narrative trees and player choices.

## Key Requirements
1. **Dialogue tree system with conditional branches** - Essential for creating non-linear narratives where player choices matter, supporting nested dialogue options, conditional availability based on game state, and dynamic response generation based on character relationships.

2. **Story state tracking with save/load functionality** - Critical for maintaining narrative continuity across sessions, tracking player choices, quest progress, discovered information, and ensuring story coherence when returning to saved games.

3. **Character relationship and reputation systems** - Enables dynamic storytelling where NPC behavior changes based on player actions, tracking affinity levels, faction standings, past interactions, and influencing available dialogue options and story branches.

4. **Dynamic text generation with variable substitution** - Provides personalized narrative experiences by incorporating player name, chosen pronouns, past decisions, and world state into dialogue and descriptions, creating more immersive storytelling.

5. **Choice consequence visualization for debugging** - Facilitates narrative design by showing branching paths, highlighting unreachable content, tracking choice statistics, and validating that all narrative threads resolve properly.

## Technical Requirements
- **Testability requirements**: All narrative logic must be deterministic for testing story paths, dialogue conditions must be verifiable, save states must be validated for completeness, text generation must be predictable
- **Performance expectations**: Dialogue tree navigation must be instantaneous, save/load operations under 200ms, support for stories with 10,000+ nodes, efficient memory usage for large narratives
- **Integration points**: Import/export tools for narrative design software, plugin system for custom narrative mechanics, localization support framework, analytics API for choice tracking
- **Key constraints**: Pure Python implementation, no external narrative engines, all story data must be human-readable, support for version control of narrative content

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The engine must provide comprehensive narrative game features including:
- Dialogue tree manager supporting conditional branches, loops, and dynamic content generation
- Story state tracker maintaining all narrative variables, flags, and progression markers
- Character system with relationship values, reputation tracking, and mood states
- Text processor handling variable substitution, pronoun consistency, and dynamic descriptions
- Choice system recording all decisions, calculating consequences, and managing story flags
- Save game manager preserving complete narrative state with backwards compatibility
- Narrative debugger showing story flow, unreachable content, and choice statistics

## Testing Requirements
Define comprehensive test coverage including:
- **Key functionalities that must be verified**:
  - Dialogue trees correctly evaluate conditions and present appropriate options
  - Story state maintains consistency across all narrative branches
  - Character relationships accurately affect dialogue availability
  - Text generation produces grammatically correct output with proper substitutions
  - Choice consequences properly update all relevant story flags

- **Critical user scenarios that should be tested**:
  - Complete playthrough of main story path
  - Exploration of all major branch points
  - Save/load at various story points
  - Relationship changes affecting dialogue
  - Multiple playthroughs with different choices

- **Performance benchmarks that must be met**:
  - Navigate dialogue tree with 1000 nodes in under 10ms
  - Load story state with 500 variables in under 200ms
  - Generate dynamic text for 100 substitutions in under 50ms
  - Calculate choice consequences for complex conditions in under 20ms
  - Export story statistics for 10,000 choices in under 1 second

- **Edge cases and error conditions that must be handled properly**:
  - Circular dialogue references
  - Missing story variables in conditions
  - Save file version mismatches
  - Infinite loops in narrative logic
  - Memory management for very long play sessions

- **Required test coverage metrics**:
  - Minimum 90% code coverage
  - All dialogue paths must be reachable
  - Every story variable must be tested
  - Integration tests for complete narratives
  - Regression tests for save compatibility

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
- Dialogue system supports complex branching narratives with conditional logic working correctly
- Story state tracking maintains narrative coherence across all possible paths
- Character relationships dynamically influence story progression and available options
- Text generation creates natural, personalized narrative content without errors
- Complete narrative games can be created, played, saved, and resumed reliably

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