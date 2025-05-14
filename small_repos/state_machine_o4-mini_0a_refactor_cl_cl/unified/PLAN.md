# State Machine Unification Plan

## Overview

This document outlines the approach for refactoring the state machine implementations from four different personas (Business Process Analyst, Game Developer, Robotics Engineer, and UX Prototyper) into a single, unified state machine library. The unified implementation will preserve all functionality and interfaces while eliminating redundancy.

## Requirements Analysis

After analyzing the source code and tests from each persona, the following key requirements have been identified:

1. **Core State Machine Functionality**:
   - State definitions and transitions
   - Ability to define transitions with guards/conditions
   - State change mechanisms (triggers/events)
   - Current state tracking
   - State history tracking

2. **Hooks and Callbacks**:
   - State enter/exit hooks
   - Global hooks (before/after transitions)

3. **Undo/Redo Management**:
   - Push and pop operations
   - Undo and redo stacks
   - State restoration

4. **Import/Export**:
   - Serialization to different formats (JSON, YAML, Dict)
   - Load from serialized formats
   - Visualization export (dot format, interactive)

5. **Simulation**:
   - Sequence simulation
   - Assertions for expected states

6. **Different APIs**:
   - Object-oriented API (instance-based)
   - Functional API (global singleton)
   - CLI interfaces

## Architecture Design

### Core Components

1. **StateMachine**: The foundational class that handles states, transitions, and operations
2. **Transition**: A class/structure to represent transitions between states
3. **Hooks**: A system for managing callbacks at various points in the state machine lifecycle
4. **Serialization**: Components for serializing and deserializing state machines
5. **CLI**: Interface for command-line operations

### File Structure

```
unified/
├── __init__.py
├── setup.py
├── src/
│   ├── __init__.py
│   ├── statemachine/
│   │   ├── __init__.py
│   │   ├── core.py                # Core StateMachine class
│   │   ├── transition.py          # Transition representation
│   │   ├── hooks.py               # Hook/callback management
│   │   ├── serialization.py       # Import/export functionality
│   │   ├── history.py             # History tracking
│   │   └── visualization.py       # Visualization exports
│   ├── api/
│   │   ├── __init__.py
│   │   ├── functional.py          # Functional API (singleton-based)
│   │   └── object_oriented.py     # OO API (instance-based)
│   ├── interfaces/
│   │   ├── __init__.py
│   │   ├── cli.py                 # CLI interface
│   │   ├── business_process_analyst/  # Business Process Analyst persona
│   │   │   ├── __init__.py
│   │   │   ├── cli.py
│   │   │   └── process_engine.py
│   │   ├── game_developer/        # Game Developer persona
│   │   │   ├── __init__.py
│   │   │   └── statemachine.py
│   │   ├── robotics_engineer/     # Robotics Engineer persona
│   │   │   ├── __init__.py
│   │   │   ├── robotfsm.py
│   │   │   └── yaml.py
│   │   └── ux_prototyper/         # UX Prototyper persona
│   │       ├── __init__.py
│   │       └── wizard_engine.py
│   └── utils/
│       ├── __init__.py
│       └── helpers.py             # Common utility functions
├── tests/
    ├── test_business_process_analyst_cli.py
    ├── test_business_process_analyst_process_engine.py
    ├── test_game_developer_cli.py
    ├── test_game_developer_run_tests.py
    ├── test_game_developer_statemachine.py
    ├── test_robotics_engineer_cli.py
    ├── test_robotics_engineer_robotfsm.py
    ├── test_ux_prototyper_cli.py
    ├── test_ux_prototyper_simulate_invalid_transition.py
    └── test_ux_prototyper_wizard_engine.py
```

### Core StateMachine Class

The central `StateMachine` class will:

1. Maintain states, transitions, hooks, and history
2. Provide methods for common operations (define transitions, trigger events, simulation)
3. Support serialization/deserialization
4. Manage undo/redo
5. Handle callbacks and hooks

### Implementation Strategy

1. **Layered Architecture**:
   - Core: The foundational state machine logic
   - API: User-facing interfaces (OO and functional)
   - Interfaces: Persona-specific adapters

2. **Backward Compatibility**:
   - Interface adapters will provide backward compatibility
   - Preserve all API signatures from original implementations
   - Same method names, parameters, and return values

3. **Consistent Design Patterns**:
   - Factory pattern for creating state machines
   - Observer pattern for hooks and callbacks
   - Strategy pattern for guards and conditions
   - Command pattern for undo/redo operations

### Dependency Management

1. **Minimal Dependencies**:
   - No external dependencies beyond Python standard library
   - Custom YAML implementation for robotics engineer persona

2. **Interface Adapters**:
   - Each persona interface will adapt the core StateMachine to match original APIs
   - Import paths updated in tests to use new implementation

## Key Design Decisions

1. **Unified State Representation**:
   - Consistent internal representation for states
   - Compatible with all persona state models

2. **Flexible Guard System**:
   - Support for both simple and complex guards
   - Composable guards using AND/OR/NOT operations
   - Consistent guard application across all transition types

3. **Configurable Serialization**:
   - Support YAML, JSON, and Dict formats
   - Automatic format detection
   - Preserve custom serialization needs

4. **Functional vs. OO API**:
   - Provide both object-oriented and functional APIs
   - Singleton pattern for functional API
   - First-class functions for functional style

5. **Visualization Formats**:
   - GraphViz DOT format
   - Interactive format
   - Extensible for additional formats

## Implementation Approach

1. Build the core `StateMachine` class
2. Implement transition management
3. Add hooks and callbacks
4. Implement serialization/deserialization
5. Create visualization export
6. Develop API layers (OO and functional)
7. Implement persona-specific interface adapters
8. Update import paths in tests
9. Verify test compatibility
10. Document the unified implementation

## Testing Strategy

1. Unit tests for core components
2. Integration tests for combined functionality
3. Ensure backward compatibility with existing tests
4. Verify edge cases are handled properly
5. Test serialization/deserialization for all formats
6. Test all hook and callback scenarios

This plan provides a comprehensive approach to unify the various state machine implementations while preserving all functionality and maintaining backward compatibility with existing tests.