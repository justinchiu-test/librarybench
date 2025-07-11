# PyTermGame - Terminal UI Game Engine

## Overview
A terminal-based game engine focused on creating gamified productivity tools with rich UI components, achievement systems, and data visualization capabilities to increase user engagement in terminal applications.

## Persona Description
A developer creating terminal-based productivity tools with game-like elements who needs widget systems and data visualization. She wants to gamify terminal applications to increase user engagement.

## Key Requirements
1. **Reusable UI widget library (menus, progress bars, charts)** - Essential for rapid application development with pre-built terminal UI components including dropdown menus, multi-select lists, progress indicators, bar charts, line graphs, and gauges that can be easily integrated and customized.

2. **Achievement and experience point systems** - Critical for gamification by tracking user actions, awarding points for milestones, unlocking achievements, displaying progress notifications, and maintaining user levels to encourage continued engagement.

3. **Data visualization components for statistics** - Provides insights through ASCII-based charts and graphs, real-time data updates, sparklines for trends, heat maps for patterns, and dashboard layouts for comprehensive data display.

4. **Notification and event scheduling system** - Enables timely user engagement with toast-style notifications, scheduled reminders, event queues, priority-based alerts, and non-intrusive display methods that don't interrupt workflow.

5. **Theme customization with color palette support** - Allows personalization through predefined color schemes, custom palette creation, consistent styling across widgets, accessibility options for colorblind users, and theme persistence across sessions.

## Technical Requirements
- **Testability requirements**: All UI components must be testable without display, widget state changes must be verifiable, achievement triggers must be deterministic, data visualizations must produce consistent output
- **Performance expectations**: Widget rendering under 10ms, smooth animations at 30 FPS minimum, efficient redraw with dirty region tracking, support for 50+ widgets simultaneously
- **Integration points**: Plugin system for custom widgets, data source adapters for visualizations, achievement API for external systems, theme marketplace integration
- **Key constraints**: Must work in all standard terminals, graceful degradation for limited color support, no external UI libraries, ASCII-only rendering

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The engine must provide comprehensive UI and gamification features including:
- Widget factory with pre-built components for menus, forms, progress bars, and charts
- Achievement system tracking user actions, progress milestones, and unlock conditions
- Experience calculator with level progression, skill trees, and reward unlocking
- Data visualizer supporting various chart types with real-time updates
- Notification manager with priority queues, scheduling, and display positioning
- Theme engine with color palette management, style inheritance, and hot-reloading
- Layout system supporting responsive grids, absolute positioning, and z-ordering

## Testing Requirements
Define comprehensive test coverage including:
- **Key functionalities that must be verified**:
  - Widgets render correctly with proper boundaries and content
  - Achievement system accurately tracks progress and unlocks
  - Data visualizations correctly represent input data
  - Notifications appear at scheduled times with correct priority
  - Themes apply consistently across all components

- **Critical user scenarios that should be tested**:
  - Complete productivity session with multiple widgets
  - Achievement unlocking through various actions
  - Real-time data updates in visualizations
  - Theme switching without display corruption
  - Complex layouts with overlapping widgets

- **Performance benchmarks that must be met**:
  - Render 50 widgets in under 50ms
  - Update chart with 1000 data points in under 20ms
  - Process 100 achievements checks in under 10ms
  - Apply theme changes in under 100ms
  - Handle 1000 notifications in queue efficiently

- **Edge cases and error conditions that must be handled properly**:
  - Terminal resize with active widgets
  - Invalid data for visualizations
  - Achievement condition conflicts
  - Color limitations in basic terminals
  - Memory management for long sessions

- **Required test coverage metrics**:
  - Minimum 90% code coverage
  - All widget types thoroughly tested
  - Every achievement condition validated
  - All chart types with edge cases
  - Theme application regression tests

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
- Widget library provides all specified components with consistent behavior and styling
- Achievement system successfully gamifies user actions with meaningful progression
- Data visualizations accurately represent complex datasets in terminal constraints
- Notification system delivers timely alerts without disrupting user workflow
- Theme system allows full customization while maintaining readability

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