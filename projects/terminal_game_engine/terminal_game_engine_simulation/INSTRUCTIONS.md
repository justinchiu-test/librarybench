# PyTermGame - Simulation Game Engine

## Overview
A terminal-based game engine specialized for creating complex management and simulation games with economic systems, AI agents, and sophisticated simulation mechanics for city builders and tycoon-style games.

## Persona Description
A developer creating management and simulation games who needs complex economic systems and AI. He requires sophisticated simulation mechanics for city builders and management games.

## Key Requirements
1. **Resource management framework with supply chains** - Essential for economic simulations with multi-tier resource processing, production chains, storage limitations, transportation networks, and market dynamics that create realistic economic challenges.

2. **AI agent system for simulated entities** - Critical for bringing simulations to life with autonomous citizens, workers, or units that have needs, goals, decision-making capabilities, and emergent behaviors creating dynamic gameplay.

3. **Time acceleration with event scheduling** - Provides flexible pacing through variable speed controls, accurate event timing at all speeds, scheduled events and deadlines, seasonal cycles, and proper simulation updates regardless of time scale.

4. **Statistical analysis and graphing tools** - Enables data-driven gameplay by tracking economic metrics, population statistics, resource flows, trend analysis, and presenting complex data through ASCII-based visualizations.

5. **Scenario editor for custom challenges** - Facilitates replayability through custom starting conditions, victory objectives, disaster events, economic presets, and shareable scenario files for community content.

## Technical Requirements
- **Testability requirements**: Economic models must be deterministic for testing, AI decisions must be reproducible, time acceleration must maintain accuracy, statistics must be verifiable
- **Performance expectations**: Simulate 10,000+ agents at reasonable speed, update economy in under 50ms per tick, handle complex supply chains efficiently, graph generation under 100ms
- **Integration points**: Pluggable AI behavior modules, economic model frameworks, custom resource types, scenario import/export system
- **Key constraints**: Memory efficient for large simulations, all calculations must be precise, no floating-point errors in economy, terminal-friendly data display

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The engine must provide comprehensive simulation features including:
- Resource manager tracking production, consumption, storage, and transportation
- Supply chain processor calculating multi-step production with efficiency modifiers
- AI controller managing agent goals, needs satisfaction, and decision-making
- Time system with variable speed, event scheduling, and tick synchronization
- Statistics collector aggregating economic data, population metrics, and trends
- Graph generator creating ASCII visualizations for time series and distributions
- Scenario loader supporting custom game setups, objectives, and victory conditions

## Testing Requirements
Define comprehensive test coverage including:
- **Key functionalities that must be verified**:
  - Resource calculations maintain conservation laws
  - Supply chains process materials correctly
  - AI agents make rational decisions
  - Time acceleration maintains event accuracy
  - Statistics accurately reflect simulation state

- **Critical user scenarios that should be tested**:
  - Building complete production chains
  - Economic boom and recession cycles
  - Population growth and decline
  - Resource scarcity management
  - Achieving various victory conditions

- **Performance benchmarks that must be met**:
  - Simulate 10,000 agents at 10 ticks/second
  - Process 100-step supply chain in under 10ms
  - Update statistics for 1000 metrics in under 20ms
  - Generate graph with 1000 data points in under 100ms
  - Save/load simulation state in under 1 second

- **Edge cases and error conditions that must be handled properly**:
  - Resource overflow/underflow
  - Circular supply chain dependencies
  - AI deadlock situations
  - Time acceleration edge cases
  - Memory management for long simulations

- **Required test coverage metrics**:
  - Minimum 90% code coverage
  - All economic formulas verified
  - AI behavior comprehensively tested
  - Time system accuracy validated
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
- Resource management system accurately models complex economic relationships
- AI agents exhibit believable behaviors and adapt to changing conditions
- Time acceleration allows for both detailed and long-term gameplay
- Statistical tools provide meaningful insights into simulation performance
- Scenario editor enables diverse gameplay experiences and community content

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