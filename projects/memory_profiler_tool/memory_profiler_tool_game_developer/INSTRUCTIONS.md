# PyMemTrace for Game Development

## Overview
A specialized memory profiling tool designed for game developers working with Python game engines. This implementation focuses on real-time memory tracking during gameplay, asset lifecycle management, and performance optimization to ensure smooth gaming experiences without memory-related stutters or crashes.

## Persona Description
A game studio lead optimizing a Python game engine who needs to track memory usage of game objects and assets. She wants to ensure smooth gameplay by preventing memory-related stutters and crashes.

## Key Requirements

1. **Game Loop Memory Profiling with Frame-by-frame Analysis**
   - Track memory allocation/deallocation per game frame
   - Monitor memory usage spikes during frame rendering
   - Identify memory allocation patterns causing frame drops
   - Support for fixed timestep and variable timestep loops
   - Essential for maintaining consistent frame rates and smooth gameplay

2. **Asset Memory Lifecycle Tracking from Load to Unload**
   - Monitor memory usage of textures, sounds, and models
   - Track asset reference counting and lifecycle states
   - Detect orphaned assets and memory leaks
   - Provide asset memory usage heat maps
   - Critical for efficient asset management in memory-constrained environments

3. **Object Pooling Effectiveness Measurement**
   - Analyze memory savings from object pooling
   - Track pool utilization rates and overflow frequency
   - Monitor allocation/deallocation overhead reduction
   - Identify optimal pool sizes for different object types
   - Vital for reducing garbage collection pauses during gameplay

4. **Memory Budget Enforcement with Automatic Asset Eviction**
   - Set and monitor memory budgets per subsystem
   - Implement automatic asset eviction strategies
   - Prioritize asset retention based on usage patterns
   - Support for multi-level memory budget hierarchies
   - Essential for maintaining stable performance across different hardware

5. **Platform-specific Memory Limit Awareness (Mobile, Console)**
   - Track platform-specific memory constraints
   - Monitor memory usage against platform limits
   - Provide platform-optimized memory recommendations
   - Support for console memory bank management
   - Critical for cross-platform game deployment

## Technical Requirements

### Testability Requirements
- All functionality must be implemented as Python modules with no UI components
- Comprehensive test coverage using pytest with game simulation fixtures
- Mock game loop and asset loading for isolated testing
- Performance benchmarks for real-time profiling overhead
- Test scenarios for various game genres and complexities

### Performance Expectations
- Frame profiling overhead must not exceed 0.5ms per frame
- Support for 60+ FPS without impacting performance
- Real-time memory tracking with microsecond precision
- Minimal memory footprint for profiler (<20MB)
- Zero-allocation profiling mode for critical paths

### Integration Points
- Game engine agnostic design with hook system
- PyGame, Panda3D, and custom engine support
- Asset pipeline integration hooks
- Platform SDK memory API integration
- Export to game profiling tools (PIX, RenderDoc format)

### Key Constraints
- Must work with Python 3.8+ standard library
- Thread-safe for multi-threaded game engines
- Lock-free profiling for real-time requirements
- Compatible with game engine update loops
- Must not cause frame rate drops

## Core Functionality

The memory profiler must provide a comprehensive library for tracking and analyzing memory usage in game development:

1. **Frame Memory Profiler**
   - Per-frame memory allocation tracking
   - Frame timing correlation with memory events
   - Memory spike detection and alerting
   - Historical frame memory analysis

2. **Asset Memory Manager**
   - Asset type-specific memory tracking
   - Lifecycle state monitoring
   - Reference counting validation
   - Memory leak detection for assets

3. **Object Pool Analyzer**
   - Pool efficiency metrics
   - Allocation pattern analysis
   - Pool size optimization
   - GC impact measurement

4. **Memory Budget System**
   - Hierarchical budget management
   - Automatic eviction policies
   - Priority-based retention
   - Budget violation alerts

5. **Platform Memory Monitor**
   - Platform-specific limit tracking
   - Memory bank utilization
   - Platform optimization suggestions
   - Cross-platform comparison tools

## Testing Requirements

### Key Functionalities to Verify
- Accurate per-frame memory measurement without frame drops
- Correct asset lifecycle tracking across load/unload cycles
- Object pool efficiency calculations
- Memory budget enforcement accuracy
- Platform memory limit detection

### Critical User Scenarios
- Profiling a game running at 60 FPS for 1 hour
- Tracking memory during level transitions
- Monitoring asset streaming during open-world gameplay
- Detecting memory leaks in particle systems
- Optimizing memory for mobile deployment

### Performance Benchmarks
- Frame overhead < 0.5ms at 60 FPS
- Asset tracking for 10,000+ game objects
- Pool monitoring with < 0.1ms overhead
- Memory snapshot generation < 5ms
- Support for 1GB+ asset libraries

### Edge Cases and Error Conditions
- Handling of sudden memory spikes
- Recovery from out-of-memory conditions
- Profiling during scene transitions
- Multi-threaded asset loading
- Platform memory exhaustion

### Required Test Coverage Metrics
- Code coverage > 90%
- Branch coverage > 85%
- Performance regression tests
- Platform-specific test suites
- Memory stress tests

**IMPORTANT**: All tests must be run with pytest-json-report to generate a pytest_results.json file:
```bash
pip install pytest-json-report
pytest --json-report --json-report-file=pytest_results.json
```

## Success Criteria

The implementation will be considered successful when:

1. **All functional requirements are met** with comprehensive test coverage
2. **Frame profiling overhead** remains below 0.5ms per frame
3. **Asset memory tracking** accurately reflects game memory usage
4. **Object pooling analysis** provides actionable optimization insights
5. **Platform memory limits** are correctly detected and enforced
6. **All tests pass** when run with pytest and a valid pytest_results.json file is generated
7. **Documentation** includes game-specific profiling examples

**REQUIRED FOR SUCCESS**:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

## Implementation Guidelines

Use `uv venv` to set up the virtual environment. From within the project directory, activate the environment with `source .venv/bin/activate`. Install the project with `uv pip install -e .`.

Focus on creating a high-performance library that game developers can integrate without impacting frame rates. The implementation should prioritize real-time performance, accurate measurements, and actionable insights for memory optimization in games.