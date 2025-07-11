# PyTermGame - Mobile Terminal Game Engine

## Overview
A terminal-based game engine optimized for mobile terminal emulators with touch-friendly controls, responsive layouts, and battery-efficient rendering for accessible gaming on modern mobile devices.

## Persona Description
A developer creating games for mobile terminal emulators who needs touch-friendly controls and responsive layouts. He wants to make terminal games accessible on modern mobile devices.

## Key Requirements
1. **Touch gesture recognition and mapping** - Essential for mobile gameplay by detecting taps, swipes, pinches, and long presses, mapping gestures to game actions, supporting multi-touch, providing visual feedback, and maintaining responsiveness on various screen sizes.

2. **Responsive layout system for different screen sizes** - Critical for device compatibility through dynamic UI scaling, orientation support, safe area handling, flexible grid systems, and automatic text size adjustment for readability across phones and tablets.

3. **Virtual keyboard optimization for gameplay** - Provides seamless input by minimizing keyboard appearances, quick-access command buttons, gesture-based alternatives, custom input methods, and smart positioning to avoid covering game content.

4. **Battery-efficient rendering modes** - Enables extended play sessions through adaptive frame rates, partial screen updates, dark mode optimization, CPU throttling awareness, and power-saving mode detection for appropriate performance scaling.

5. **Cloud save synchronization across devices** - Facilitates cross-device play by automatic save syncing, conflict resolution, offline capability, compression for mobile data, and seamless progression between phone, tablet, and desktop.

## Technical Requirements
- **Testability requirements**: Touch input must be simulatable for testing, layouts must be verifiable at different sizes, battery efficiency must be measurable, cloud sync must handle all edge cases
- **Performance expectations**: 60 FPS on modern devices, 30 FPS on older devices, touch response under 16ms, layout adaptation under 100ms, cloud sync under 5 seconds
- **Integration points**: Terminal emulator APIs, mobile OS gesture systems, cloud storage providers, device capability detection
- **Key constraints**: Limited screen real estate, touch precision limitations, mobile data constraints, battery life considerations

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The engine must provide comprehensive mobile optimization features including:
- Touch input manager recognizing gestures and mapping to game controls
- Responsive layout engine adapting to screen sizes and orientations
- Virtual control system with customizable on-screen buttons and gestures
- Render optimizer with battery-aware performance scaling
- Cloud save manager handling synchronization and conflict resolution
- Mobile-specific features like haptic feedback and screen wake locks
- Performance profiler tracking battery usage and thermal state

## Testing Requirements
Define comprehensive test coverage including:
- **Key functionalities that must be verified**:
  - Touch gestures correctly map to game actions
  - Layouts adapt properly to all screen sizes
  - Virtual controls register inputs accurately
  - Battery optimization reduces power consumption
  - Cloud saves sync reliably across devices

- **Critical user scenarios that should be tested**:
  - Playing game with touch-only input
  - Switching between portrait and landscape
  - Continuing game on different device
  - Extended play session battery impact
  - Network interruption during sync

- **Performance benchmarks that must be met**:
  - Touch response latency under 16ms
  - Layout recalculation under 100ms
  - 30+ FPS on 5-year-old devices
  - Battery usage under 10% per hour
  - Cloud sync completion under 5 seconds

- **Edge cases and error conditions that must be handled properly**:
  - Extremely small screen sizes
  - Rapid orientation changes
  - Touch input during keyboard display
  - Low battery mode activation
  - Cloud sync conflicts

- **Required test coverage metrics**:
  - Minimum 90% code coverage
  - All gesture types tested
  - Every layout breakpoint verified
  - Battery modes validated
  - Sync scenarios covered

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
- Touch controls provide intuitive and responsive gameplay on mobile devices
- Responsive layouts ensure playability across all screen sizes and orientations
- Virtual keyboard integration minimizes gameplay interruption
- Battery optimization enables extended play sessions without excessive drain
- Cloud synchronization allows seamless progression across multiple devices

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