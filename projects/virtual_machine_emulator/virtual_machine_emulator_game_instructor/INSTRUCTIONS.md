# Game Engine Fundamentals Virtual Machine

## Overview
A specialized virtual machine designed for teaching game development fundamentals, demonstrating the low-level operation of game engines with implementations of game loops, asset management, entity component systems, simplified graphics pipelines, and input handling.

## Persona Description
Elena teaches game development fundamentals and wants students to understand how game engines work at a low level. She needs a virtual machine that demonstrates the core principles of game loops, state management, and resource utilization.

## Key Requirements
1. **Game loop implementation showing update-render cycles and timing management**: Essential for Elena to demonstrate the foundational structure behind all games, helping students understand how game engines separate logic updates from rendering, how timing is managed to achieve consistent gameplay across different hardware, and how the loop orchestrates all game systems.

2. **Asset loading simulation demonstrating resource initialization and management**: Critical for teaching students how games efficiently handle the loading, caching, and unloading of various assets like textures, models, and audio, showing memory management techniques, asset streaming strategies, and resource reference management.

3. **Entity component system modeling for game object representation**: Important for illustrating modern game architecture approaches, demonstrating how entities, components, and systems provide a flexible and performant alternative to deep inheritance hierarchies for representing and updating game objects.

4. **Simplified graphics pipeline showing transformation from game state to visual output**: Necessary for demystifying how game state becomes rendered output, providing students with a clear understanding of the steps involved in transforming 3D models and 2D sprites into the final rendered frame without diving into the complexities of actual GPU programming.

5. **Input handling framework demonstrating event processing and response**: Vital for teaching how games receive and respond to player actions, showing how input events are captured, buffered, translated into meaningful game actions, and how these systems can be configured for different control schemes.

## Technical Requirements
- **Testability Requirements**:
  - Game loop timing must be precisely controllable and measurable
  - Asset loading scenarios must be reproducible with simulated I/O constraints
  - Entity component system operations must be independently verifiable
  - Graphics pipeline transformations must produce predictable, testable outputs
  - Input handling must support automated test event injection

- **Performance Expectations**:
  - Game loop should maintain 60 updates per second (16.7ms per frame) with standard workloads
  - Asset loading simulation should reflect realistic timing ratios
  - Entity component system should efficiently handle at least 10,000 entities
  - Simplified graphics pipeline should process at least 1,000 simple objects per frame
  - Input handling should process at least 100 events per frame with minimal latency

- **Integration Points**:
  - Game state serialization and deserialization
  - Entity definition and instantiation API
  - Component implementation framework
  - System registration and execution pipeline
  - Asset creation and management interfaces

- **Key Constraints**:
  - Must be implementable using Python standard library
  - Should focus on fundamental concepts rather than high-fidelity simulation
  - Must prioritize clarity and educational value over performance
  - Should be approachable for students with intermediate programming skills

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
1. **Game Loop System**: Implement a configurable game loop demonstrating fixed and variable time steps, logic/render separation, and performance monitoring with detailed timing statistics and visualization.

2. **Asset Management System**: Create a complete asset pipeline with loading, caching, reference counting, and memory management that simulates real-world constraints while providing clear visibility into the process.

3. **Entity Component Framework**: Develop a fully-featured entity component system with efficient component storage, entity lifecycle management, and system execution with various update strategies.

4. **Simplified Graphics Pipeline**: Implement a basic rendering pipeline showing transformation, culling, sorting, and batching operations without actual graphical output but with complete data transformation visibility.

5. **Input Processing System**: Create an event-based input handling system with device abstraction, event queuing, input mapping, and response processing demonstrating how player actions translate to game behavior.

6. **Game State Management**: Implement state tracking, transitions, and serialization to demonstrate how games maintain and evolve complex state over time.

7. **Performance Profiling Tools**: Provide detailed instrumentation for measuring and visualizing the performance characteristics of different engine components to identify bottlenecks and optimization opportunities.

## Testing Requirements
- **Key Functionalities to Verify**:
  - Correct implementation of various game loop strategies
  - Proper management of assets through their complete lifecycle
  - Efficient entity component system operations and updates
  - Accurate transformation of object data through the graphics pipeline
  - Responsive and correct handling of input events

- **Critical User Scenarios**:
  - Simulating a complete game frame including updates, rendering, and input
  - Loading and unloading assets under various memory constraints
  - Managing thousands of entities with different component combinations
  - Processing a scene through the complete graphics pipeline
  - Handling complex input sequences with appropriate game responses

- **Performance Benchmarks**:
  - Maintain 60 frames per second with 5,000 simple entities
  - Complete asset loading operations with realistic timing ratios
  - Update 10,000 entities in less than 16ms (one frame at 60fps)
  - Process 1,000 renderable objects through the pipeline in less than 8ms
  - Handle 100 input events per frame with less than 1ms of processing time

- **Edge Cases and Error Conditions**:
  - Handle frame timing spikes and recovery
  - Manage asset loading failures and missing dependencies
  - Recover from component system errors without crashing
  - Handle malformed objects in the graphics pipeline
  - Process conflicting or invalid input combinations appropriately

- **Required Test Coverage Metrics**:
  - 95% code coverage for the game loop implementation
  - 90% coverage for asset management systems
  - 95% coverage for the entity component framework
  - 90% coverage for graphics pipeline operations
  - 90% coverage for input handling systems

IMPORTANT: 
- ALL functionality must be testable via pytest without any manual intervention
- Tests should verify behavior against requirements, not implementation details
- Tests should be designed to validate the WHAT (requirements) not the HOW (implementation)
- Tests should be comprehensive enough to verify all aspects of the requirements
- Tests should not assume or dictate specific implementation approaches

## Success Criteria
1. Students can clearly understand the structure and behavior of game loops under different conditions
2. Asset loading and management concepts are demonstrated with realistic constraints and solutions
3. Entity component system provides a clear alternative to inheritance-based game object models
4. Graphics pipeline clearly demonstrates the transformation of game state to renderable output
5. Input handling system shows how player actions are captured and translated to game behavior
6. All systems work together to demonstrate a complete game frame execution cycle
7. Performance characteristics are measurable and optimizable, providing practical lessons in game engine efficiency

To set up your environment, use `uv venv` to create a virtual environment. From within the project directory, the environment can be activated with `source .venv/bin/activate`.