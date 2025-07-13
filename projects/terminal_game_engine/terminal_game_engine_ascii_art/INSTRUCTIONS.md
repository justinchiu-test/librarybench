# PyTermGame - ASCII Art Game Engine

## Overview
A terminal-based game engine focused on creating visually stunning games using advanced ASCII art rendering techniques, pushing the boundaries of terminal graphics with sophisticated visual effects and animations.

## Persona Description
An ASCII art enthusiast creating visually rich terminal games who needs advanced rendering techniques. She wants to push the boundaries of terminal graphics with ASCII art.

## Key Requirements
1. **ASCII art sprite editor and animator** - Essential for creating visual content with drawing tools, layer support, onion skinning for animation, frame management, and export/import capabilities for sharing artwork between projects.

2. **Layered rendering system with transparency** - Critical for complex scenes by supporting multiple drawing layers, alpha transparency simulation, z-ordering, layer effects, and efficient compositing to create depth and visual richness.

3. **Particle effects using ASCII characters** - Provides dynamic visuals through character-based particles, physics simulation, emitter configurations, blend modes, and performance optimization for hundreds of simultaneous particles.

4. **Dynamic lighting and shadow effects** - Creates atmosphere with ASCII-based illumination, light source management, shadow casting, ambient occlusion approximation, and day/night cycles for immersive environments.

5. **ASCII art compression for large sprites** - Enables efficient storage of detailed artwork through pattern recognition, run-length encoding, palette optimization, streaming decompression, and maintaining quality while reducing memory footprint.

## Technical Requirements
- **Testability requirements**: Rendering output must be deterministic, sprite animations must be frame-accurate, particle systems must be reproducible, compression must be lossless
- **Performance expectations**: Render 30+ layers at 30 FPS, animate 100+ sprites simultaneously, support 500+ particles, compress sprites by 70%+, maintain smooth scrolling
- **Integration points**: Import from ASCII art tools, export to common formats, plugin system for effects, community art library integration
- **Key constraints**: Terminal color limitations, character set restrictions, performance on low-end systems, cross-platform character display

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The engine must provide comprehensive ASCII art features including:
- Sprite editor with brush tools, shape primitives, and color palette management
- Animation system supporting frame sequencing, tweening, and onion skinning
- Layer manager handling composition, transparency, and effect processing
- Particle engine with emitters, forces, and collision detection
- Lighting processor calculating illumination, shadows, and color grading
- Compression system optimizing storage while preserving visual quality
- Rendering pipeline efficiently compositing all visual elements

## Testing Requirements
Define comprehensive test coverage including:
- **Key functionalities that must be verified**:
  - Sprite editor produces correct ASCII output
  - Animations play at specified frame rates
  - Layer compositing maintains proper ordering
  - Particle effects follow physics rules
  - Lighting calculations produce expected results

- **Critical user scenarios that should be tested**:
  - Creating and editing multi-layer sprites
  - Animating complex character sequences
  - Particle effects in various scenarios
  - Dynamic lighting changes
  - Sprite compression and decompression

- **Performance benchmarks that must be met**:
  - Edit 100x100 sprite in real-time
  - Animate 50 sprites at 30 FPS
  - Render 500 particles without slowdown
  - Calculate lighting for 50x50 area in under 10ms
  - Compress large sprites in under 100ms

- **Edge cases and error conditions that must be handled properly**:
  - Color limitations in basic terminals
  - Character encoding issues
  - Memory limits for large scenes
  - Performance degradation handling
  - Compression edge cases

- **Required test coverage metrics**:
  - Minimum 90% code coverage
  - All rendering paths tested
  - Animation system fully covered
  - Compression algorithm validated
  - Performance benchmarks met

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
- Sprite editor enables creation of detailed ASCII artwork with animation support
- Layered rendering creates visually complex scenes with proper depth
- Particle effects add dynamic visual interest without performance impact
- Lighting system creates atmospheric environments using only ASCII characters
- Compression allows for large, detailed sprites without excessive memory usage

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