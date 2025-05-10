# Game Engine Virtual Machine Emulator

## Overview
A specialized virtual machine emulator designed for game development education, demonstrating the low-level principles of game engines including game loops, state management, resource utilization, rendering pipelines, and input handling. The system provides instructors with tools to teach fundamental game programming concepts without the complexity of commercial engines.

## Persona Description
Elena teaches game development fundamentals and wants students to understand how game engines work at a low level. She needs a virtual machine that demonstrates the core principles of game loops, state management, and resource utilization.

## Key Requirements
1. **Game Loop Implementation**: Create a system that clearly demonstrates update-render cycles, frame timing, and time-step management techniques. This is essential for Elena to teach students how games maintain consistent simulation rates independent of rendering speed, helping them understand the foundation of all game engines and the importance of separating logic updates from visual rendering.

2. **Asset Loading Simulation**: Implement a framework for demonstrating resource initialization, management, and efficient access patterns. This feature allows Elena to show students how game engines handle loading, unloading, and accessing various game assets like textures, sounds, and models, emphasizing critical concepts like resource pools, asynchronous loading, and memory efficiency.

3. **Entity Component System Modeling**: Design a demonstration of modern game object representation using composable components rather than deep inheritance hierarchies. This approach is crucial for Elena to teach students contemporary game architecture patterns that enable flexibility, reusability, and performance, illustrating why most professional game engines have moved to component-based design.

4. **Simplified Graphics Pipeline**: Develop a system that demonstrates the transformation from game state to visual output through multiple processing stages. This capability helps Elena show students the fundamental steps of 3D rendering without the overwhelming complexity of modern graphics APIs, creating a clear conceptual understanding of transformations, rasterization, and shading.

5. **Input Handling Framework**: Create tools for demonstrating event processing, input mapping, and response systems typical in games. This feature enables Elena to teach students how games detect, process, and respond to player input across various devices, showing the complete path from physical input to game state changes and highlighting concepts like input buffering and command patterns.

## Technical Requirements

### Testability Requirements
- Game loop timing must be precisely controllable for deterministic testing
- Asset loading scenarios must be reproducible with consistent performance characteristics
- Entity-component interactions must be verifiable through clear API boundaries
- Graphics pipeline stages must be independently testable with known inputs and outputs
- Input handling must support simulation of various input sequences for testing

### Performance Expectations
- The emulator should maintain 60 frames per second for basic demonstrations
- Asset loading should demonstrate both immediate and asynchronous loading patterns
- Entity-component operations should scale efficiently to at least 1000 entities
- The graphics pipeline should handle at least 10,000 primitives for performance demonstrations
- Input processing should support at least 60 input events per second with minimal latency

### Integration Points
- Well-defined interfaces for implementing custom game loop variations
- APIs for creating resource loading scenarios with different constraints
- Component registration system for extending entity capabilities
- Stage insertion points in the graphics pipeline for custom processing
- Event system hooks for custom input handling and processing

### Key Constraints
- The implementation must demonstrate concepts without requiring actual graphics rendering
- Performance characteristics must be reliably measurable and comparable
- All systems must be explainable at a level appropriate for beginning game development students
- The design should reflect current industry practices while remaining educationally focused
- Examples must be simple enough to understand yet realistic enough to be relevant

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The virtual machine emulator must implement these core components:

1. A configurable game loop system with various time-step strategies
2. An asset management system demonstrating resource loading, caching, and unloading
3. An entity-component system for game object representation and management
4. A pipeline for transforming game state to renderable output
5. An input processing system for handling and mapping player actions
6. Performance monitoring and analysis tools for all subsystems
7. State serialization for saving and restoring game scenarios
8. Testing utilities for validating behavior under various conditions
9. Simulated rendering and audio output (without actual graphics/sound)
10. Documentation tools for explaining concepts and implementation choices

The system should allow game development instructors to create specific scenarios that demonstrate key gaming concepts, execute these scenarios with controllable parameters, measure performance characteristics, and provide students with clear examples of how game engines function at a fundamental level.

## Testing Requirements

### Key Functionalities to Verify
- Correct implementation of different game loop strategies
- Proper asset loading and management under various scenarios
- Accurate entity-component system with expected composition behavior
- Correct pipeline processing for transforming game state to output
- Reliable input handling with appropriate event propagation
- Consistent performance measurement across all systems
- Accurate simulation of time-dependent behaviors

### Critical User Scenarios
- Demonstrating fixed vs. variable time-step game loops
- Showing asset loading strategies under memory constraints
- Building game objects from components and managing their interactions
- Tracing data flow through a simplified graphics pipeline
- Processing complex input sequences and mapping them to game actions
- Analyzing performance bottlenecks in different subsystems
- Comparing different implementation strategies for common game patterns

### Performance Benchmarks
- Maintain stable 60 FPS game loop for scenarios with up to 1000 entities
- Asset loading system handling at least 100MB of simulated assets
- Entity-component system supporting 1000 entities with 10 components each
- Graphics pipeline processing 10,000 primitives per frame
- Input system handling 60 input events per second with less than 16ms latency
- All systems maintaining performance characteristics within 10% variance across runs

### Edge Cases and Error Conditions
- Handling of extremely long or short frame times in the game loop
- Management of asset loading failures and recovery
- Proper behavior when adding/removing components from active entities
- Graceful handling of graphics pipeline overflow or errors
- Appropriate processing of simultaneous or conflicting input events
- Recovery from simulated resource exhaustion
- Proper handling of corrupted game state

### Required Test Coverage Metrics
- Minimum 90% line coverage across all modules
- 100% coverage of game loop implementations
- 100% coverage of asset management core functionality
- 100% coverage of entity-component system operations
- All graphics pipeline stages must have specific test cases
- All input handling paths must be tested

IMPORTANT: 
- ALL functionality must be testable via pytest without any manual intervention
- Tests should verify behavior against requirements, not implementation details
- Tests should be designed to validate the WHAT (requirements) not the HOW (implementation)
- Tests should be comprehensive enough to verify all aspects of the requirements
- Tests should not assume or dictate specific implementation approaches

## Success Criteria
The implementation will be considered successful if:

1. A game development instructor can use it to demonstrate core engine concepts effectively
2. The system clearly illustrates at least three different game loop strategies and their tradeoffs
3. Asset loading simulation demonstrates both immediate and asynchronous loading patterns
4. Entity-component system shows clear advantages over traditional inheritance for game objects
5. The simplified graphics pipeline demonstrates all key stages from game state to final output
6. Input handling framework shows the complete cycle from player action to game response
7. All test cases pass with the specified coverage requirements
8. Documentation clearly explains how each component relates to commercial game engine concepts

## Project Setup and Development

To set up the development environment:

1. Create a new project using UV:
   ```
   uv init --lib
   ```

2. Run the project:
   ```
   uv run python your_script.py
   ```

3. Install additional dependencies:
   ```
   uv sync
   ```

4. Run tests:
   ```
   uv run pytest
   ```

5. Format code:
   ```
   uv run ruff format
   ```

6. Lint code:
   ```
   uv run ruff check .
   ```

7. Type check:
   ```
   uv run pyright
   ```