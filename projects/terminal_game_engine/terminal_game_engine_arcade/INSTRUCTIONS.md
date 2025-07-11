# PyTermGame - Retro Arcade Engine

## Overview
A terminal-based game engine optimized for recreating classic arcade games with smooth animations, precise collision detection, and authentic retro gameplay mechanics within terminal constraints.

## Persona Description
A developer recreating classic arcade games in terminal form who needs smooth animations and precise collision detection. He wants to capture the feel of classic games while working within terminal constraints.

## Key Requirements
1. **Sub-character position tracking for smooth movement** - Essential for arcade-quality movement by tracking positions at sub-cell precision, interpolating between character positions, supporting diagonal movement, and creating fluid motion that transcends terminal grid limitations.

2. **Sprite animation system with frame timing** - Critical for bringing characters to life with multi-frame animations, configurable frame rates, animation state machines, sprite sheet management, and smooth transitions between animation states.

3. **High-score table with local and online leaderboards** - Provides competitive gameplay through persistent local score storage, optional online leaderboard integration, score validation to prevent cheating, and multiple ranking categories (daily, weekly, all-time).

4. **Power-up and combo system management** - Enables exciting gameplay with timed power-up effects, combo multiplier tracking, special ability triggers, visual and audio feedback cues, and balanced difficulty progression through power-up availability.

5. **Boss pattern scripting engine** - Facilitates epic encounters with scripted movement patterns, multi-phase boss fights, attack pattern sequencing, health bar management, and dramatic defeat sequences.

## Technical Requirements
- **Testability requirements**: All game mechanics must be frame-perfectly reproducible, collision detection must be deterministic, score calculations must be verifiable, boss patterns must follow exact timings
- **Performance expectations**: Maintain 60 FPS equivalent update rate, sub-5ms input latency, smooth animation without screen tearing, support for 100+ simultaneous sprites
- **Integration points**: Modular sprite system for easy character additions, plugin architecture for custom power-ups, data-driven boss pattern definitions, configurable game rules
- **Key constraints**: Terminal refresh rate limitations must be handled gracefully, ASCII-only rendering, no external graphics libraries, cross-platform terminal compatibility

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The engine must provide comprehensive arcade game features including:
- Sub-pixel movement system with position interpolation and velocity-based physics
- Sprite animator supporting multiple animation sets, blending, and state transitions
- Collision detector with pixel-perfect accuracy, swept collision tests, and layer support
- Score manager with combo tracking, multiplier systems, and leaderboard integration
- Power-up controller managing timed effects, stacking rules, and visual indicators
- Boss engine with pattern scripting, phase transitions, and attack choreography
- Frame timing system ensuring consistent gameplay speed across different terminals

## Testing Requirements
Define comprehensive test coverage including:
- **Key functionalities that must be verified**:
  - Sub-pixel movement produces smooth, predictable motion paths
  - Sprite animations play at correct frame rates without skipping
  - Collision detection accurately identifies all contact scenarios
  - Score calculations correctly apply combos and multipliers
  - Boss patterns execute precisely according to scripts

- **Critical user scenarios that should be tested**:
  - Complete arcade game session from start to game over
  - Power-up collection and effect application
  - Boss fight with all phases and patterns
  - High score achievement and leaderboard entry
  - Frame-perfect input sequences for combos

- **Performance benchmarks that must be met**:
  - Update 100 sprites at 60 FPS equivalent
  - Collision detection for 50 objects in under 2ms
  - Animation frame updates in under 1ms
  - Boss pattern script execution in under 0.5ms
  - Score calculation with combos in under 0.1ms

- **Edge cases and error conditions that must be handled properly**:
  - Terminal resize during gameplay
  - Extremely high scores causing overflow
  - Simultaneous collision resolution
  - Power-up effect conflicts
  - Animation state transition edge cases

- **Required test coverage metrics**:
  - Minimum 90% code coverage
  - Frame-perfect timing tests
  - All collision scenarios tested
  - Every boss pattern validated
  - Performance regression tests

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
- Smooth sub-pixel movement creates fluid motion indistinguishable from 60 FPS gameplay
- Sprite animations play without stuttering or frame drops
- Collision detection provides pixel-perfect accuracy for fair gameplay
- Score system with combos and multipliers creates engaging risk/reward mechanics
- Boss fights deliver challenging, pattern-based encounters with multiple phases

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