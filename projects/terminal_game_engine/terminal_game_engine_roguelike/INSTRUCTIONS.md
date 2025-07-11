# PyTermGame - Roguelike Game Engine

## Overview
A specialized terminal-based game engine focused on creating complex roguelike dungeon crawlers with procedural generation, permadeath mechanics, and deep gameplay systems typical of the roguelike genre.

## Persona Description
An experienced roguelike developer creating a complex dungeon crawler who needs advanced procedural generation and permadeath mechanics. He requires sophisticated dungeon generation algorithms and deep gameplay systems typical of the roguelike genre.

## Key Requirements
1. **Procedural dungeon generation with room templates and corridors** - Essential for creating infinite replayability with unique dungeon layouts each run, supporting various room types (treasure rooms, boss rooms, shops) connected by corridors with proper door placement and secret passages.

2. **Line-of-sight and fog-of-war calculations** - Critical for strategic gameplay where players must explore cautiously, implementing raycasting algorithms for visibility, remembering previously seen areas, and creating tension through limited information.

3. **Permadeath save system with run statistics** - Core to the roguelike experience, implementing save-on-exit functionality, death statistics tracking, run history with achievements, and preventing save scumming while maintaining fair gameplay.

4. **Loot table and item generation system** - Provides progression and variety through randomized items with rarity tiers, procedural item properties, balanced drop rates based on dungeon depth, and unique legendary items with special effects.

5. **Turn-based combat with action scheduling** - Enables tactical gameplay with action point systems, initiative ordering, multi-turn actions, status effects duration tracking, and AI decision-making for enemies.

## Technical Requirements
- **Testability requirements**: All game logic must be deterministic with seedable random number generation for reproducible testing, combat calculations must be verifiable, dungeon generation must produce valid layouts
- **Performance expectations**: Dungeon generation must complete within 100ms for standard-sized levels, line-of-sight calculations must support 60+ FPS equivalent update rates, save/load operations must handle large game states efficiently
- **Integration points**: Modular architecture allowing easy addition of new room templates, items, and monsters; plugin system for community modifications; data-driven design for game balance
- **Key constraints**: No external dependencies beyond Python standard library, must run in standard terminal emulators, all game data must be serializable for save system

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The engine must provide a complete roguelike game framework including:
- Procedural dungeon generator with configurable parameters for room density, corridor complexity, and special room placement
- Visibility system calculating line-of-sight, fog-of-war, and light sources with efficient algorithms
- Entity management system supporting player, monsters, items, and terrain with component-based architecture
- Combat resolver handling turn order, damage calculation, status effects, and death handling
- Loot system with weighted random generation, item identification mechanics, and inventory management
- Save game manager with compression, integrity checking, and permadeath enforcement
- Game state tracker for statistics, achievements, and run history

## Testing Requirements
Define comprehensive test coverage including:
- **Key functionalities that must be verified**:
  - Dungeon generation produces connected, playable levels with all rooms accessible
  - Line-of-sight correctly identifies visible and blocked tiles
  - Combat damage calculations match expected formulas
  - Save/load maintains complete game state integrity
  - Loot generation follows specified rarity distributions

- **Critical user scenarios that should be tested**:
  - Complete game loop from start to permadeath
  - Saving mid-game and resuming correctly
  - Combat with multiple enemies and status effects
  - Item usage and inventory management
  - Level progression and difficulty scaling

- **Performance benchmarks that must be met**:
  - Generate 100x100 dungeon in under 100ms
  - Calculate visibility for 50x50 area in under 5ms
  - Save/load game state under 500ms
  - Handle 100+ entities without performance degradation

- **Edge cases and error conditions that must be handled properly**:
  - Dungeon generation failure recovery
  - Save file corruption handling
  - Invalid player actions
  - Memory management for long play sessions
  - Circular line-of-sight edge cases

- **Required test coverage metrics**:
  - Minimum 90% code coverage
  - All public APIs must have comprehensive tests
  - Integration tests for complete game scenarios
  - Property-based testing for procedural generation

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
- Procedural dungeon generator creates valid, fully-connected dungeons 100% of the time
- Combat system produces balanced, predictable results matching game design specifications
- Save system reliably preserves and restores complete game state with permadeath enforcement
- Performance meets all specified benchmarks for generation and calculation times
- Comprehensive test suite passes with 90%+ coverage and generates valid pytest_results.json

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