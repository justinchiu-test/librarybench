# Game Engine Fundamentals Simulator

## Overview
A specialized virtual machine implementation designed to demonstrate core game engine principles, providing clear visualization of game loops, state management, resource handling, and rendering pipelines to help students understand how game engines work at a low level.

## Persona Description
Elena teaches game development fundamentals and wants students to understand how game engines work at a low level. She needs a virtual machine that demonstrates the core principles of game loops, state management, and resource utilization.

## Key Requirements
1. **Game Loop Implementation**: Create a comprehensive simulation of game engine loops showing update-render cycles, timing management, and frame rate control. This feature is critical for students to understand the fundamental backbone of game engines that drives all game behavior, demonstrating how time-based updates and rendering are coordinated while maintaining consistent gameplay regardless of hardware performance.

2. **Asset Loading Simulation**: Implement a resource management system demonstrating initialization, streaming, memory management, and garbage collection for game assets. This capability helps students understand how games efficiently handle the large amounts of data required for graphics, audio, and gameplay, teaching crucial optimization techniques that are essential in resource-constrained environments.

3. **Entity Component System**: Develop a complete entity-component system implementation to demonstrate modern game object representation, composition patterns, and efficient update mechanisms. This architectural pattern is fundamental to contemporary game development, helping students understand how to create flexible, maintainable game objects while avoiding inheritance problems and enabling better performance optimization.

4. **Graphics Pipeline Simulation**: Create a simplified but accurate representation of the transformation from game state to visual output, showing key stages like culling, transformation, and rendering. This visualization demystifies how game worlds become pixels on screen, helping students grasp the multiple transformation steps and optimizations that enable efficient rendering of complex 3D environments.

5. **Input Handling Framework**: Implement a comprehensive input system demonstrating event processing, input mapping, and response handling across different input devices. This framework teaches students how games transform diverse player inputs into consistent game actions, showing how to create responsive controls that work across multiple platforms and input methods.

## Technical Requirements
- **Testability Requirements**:
  - Game loop timing must be deterministic when using fixed time steps
  - Asset loading sequences must be reproducible and verifiable
  - Entity component operations must have predictable, testable outcomes
  - Graphics pipeline transformations must produce consistent results
  - Input events must be simulatable for automated testing
  
- **Performance Expectations**:
  - Game loop should support stable 60 frames per second simulation
  - Asset loading system should handle at least 1000 simulated resources
  - Entity component system should efficiently manage at least 10,000 entities
  - Graphics pipeline should process at least 1000 simulated objects per frame
  - Complete system should operate with minimal overhead on standard development machines

- **Integration Points**:
  - Clean API for creating custom entity components
  - Standardized resource description format for asset simulation
  - Well-defined interfaces between major engine subsystems
  - Export mechanisms for system state and performance metrics
  - Hooks for custom pipeline stage implementations

- **Key Constraints**:
  - Implementation must be in pure Python for educational clarity
  - No dependencies beyond standard library to ensure portability
  - No actual rendering or graphical output, only simulation and data logging
  - All subsystems must be well-documented with educational comments
  - System must be understandable without game development background

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The core functionality of this game engine fundamentals simulator includes:

1. A complete game loop implementation with fixed and variable time step options

2. A timing system with frame rate control and consistent update timing

3. A resource management system for different asset types (textures, models, audio, etc.)

4. A comprehensive entity-component system with efficient updates and queries

5. A simulated graphics pipeline showing key transformation stages

6. A scene graph implementation for spatial organization

7. An input management system with device abstraction and mapping

8. A state management system for game progression

9. Performance monitoring and profiling tools

10. Memory management and optimization demonstrations

11. Event system for communication between engine components

12. Data-driven configuration capabilities

## Testing Requirements
- **Key Functionalities that Must be Verified**:
  - Correct game loop execution with consistent timing
  - Proper asset loading and management lifecycle
  - Accurate entity-component system operations
  - Correct transformation through all graphics pipeline stages
  - Proper handling of input events and mappings
  - Accurate performance metrics collection

- **Critical User Scenarios**:
  - Demonstrating frame rate independence in game simulations
  - Showing resource loading strategies and their performance implications
  - Illustrating entity-component patterns for different game object types
  - Tracing an object through the entire graphics pipeline
  - Demonstrating input handling across different virtual devices
  - Profiling engine performance for different scenarios

- **Performance Benchmarks**:
  - Stable simulation at 60 frames per second equivalent
  - Management of at least 10,000 entities with multiple components
  - Processing of at least 1000 resources through the asset system
  - Handling of at least 100 simultaneous input events
  - Complete system operating with reasonable memory footprint (<500MB)

- **Edge Cases and Error Conditions**:
  - Handling of extremely long or short frame times
  - Proper behavior with resource loading failures
  - Correct operation with complex entity hierarchies
  - Appropriate response to invalid pipeline data
  - Graceful handling of conflicting input events

- **Required Test Coverage Metrics**:
  - Minimum 90% line coverage for all components
  - 100% coverage for game loop implementation
  - At least 95% branch coverage for entity-component system
  - Complete coverage of graphics pipeline transformation stages
  - At least 85% coverage for input handling system

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
The implementation will be considered successful if it:

1. Accurately simulates game engine loops with proper timing and frame rate management

2. Demonstrates effective resource loading and management strategies

3. Provides a functional entity-component system showing modern game object patterns

4. Clearly illustrates the transformation stages in a graphics rendering pipeline

5. Implements a comprehensive input handling system with appropriate abstraction

6. Generates useful performance metrics that help identify bottlenecks

7. Documents key game engine concepts through implementation and comments

8. Provides reproducible demonstrations of core game engine principles

9. Remains simple enough for students to understand each component

10. Successfully passes all test cases demonstrating the required functionality

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

## Environment Setup
To set up the development environment:

1. Create a virtual environment using:
   ```
   uv venv
   ```

2. Activate the virtual environment:
   ```
   source .venv/bin/activate
   ```

3. Install the project in development mode:
   ```
   uv pip install -e .
   ```

4. CRITICAL: For test execution and reporting:
   ```
   pip install pytest-json-report
   pytest --json-report --json-report-file=pytest_results.json
   ```

REMINDER: Generating and providing the pytest_results.json file is a critical requirement for project completion. This file must be included as proof that all tests pass successfully.