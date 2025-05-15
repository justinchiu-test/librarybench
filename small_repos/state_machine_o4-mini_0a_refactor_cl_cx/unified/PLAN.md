# State Machine Library Refactoring Plan

## Current Structure Analysis

Based on the test files, we have four different implementation variants of state machine libraries:

1. **Game Developer**: OOP approach with `StateMachine` class
2. **Robotics Engineer**: Functional/procedural approach with global state
3. **UX Prototyper**: `WizardEngine` class (OOP) with UI-focused terminology
4. **Business Process Analyst**: Procedural approach with business process terminology

Each implementation handles similar concepts but with different interfaces and terminologies.

## Design Goals

1. Create a unified state machine implementation that supports all use cases
2. Maintain backward compatibility with minimal adaptation required
3. Provide consistent interfaces across different domains
4. Support domain-specific terminology through appropriate abstractions
5. Preserve all current functionality while reducing code duplication

## Refactored Project Structure

```
unified/
├── __init__.py
├── setup.py
├── PLAN.md
├── src/
│   ├── __init__.py
│   ├── statemachine/
│   │   ├── __init__.py
│   │   ├── core.py         # Core StateMachine implementation
│   │   ├── guards.py       # Guard composition utilities
│   │   ├── hooks.py        # Event hook and callback system
│   │   ├── history.py      # History, undo/redo support
│   │   ├── serialization.py # Import/export functionality
│   │   ├── visualization.py # Visualization utilities
│   │   └── simulation.py   # Simulation and testing utilities
│   │
│   ├── adapters/
│   │   ├── __init__.py
│   │   ├── game_dev.py     # Game developer compatibility layer
│   │   ├── robotics.py     # Robotics engineer compatibility layer
│   │   ├── ux.py           # UX prototyper compatibility layer
│   │   └── business.py     # Business process analyst compatibility layer
│   │
│   └── cli/
│       ├── __init__.py
│       ├── common.py       # Common CLI utilities
│       ├── game_dev.py     # Game developer CLI
│       ├── robotics.py     # Robotics engineer CLI
│       ├── ux.py           # UX prototyper CLI
│       └── business.py     # Business process analyst CLI
│
└── tests/
    ├── __init__.py
    ├── test_core.py        # Core functionality tests
    ├── test_guards.py      # Guard composition tests
    ├── test_hooks.py       # Hook system tests
    ├── test_history.py     # History tests
    ├── test_serialization.py # Serialization tests
    ├── test_visualization.py # Visualization tests
    ├── test_simulation.py  # Simulation tests
    │
    ├── test_game_developer_statemachine.py      # Compatibility tests
    ├── test_robotics_engineer_robotfsm.py       # Compatibility tests
    ├── test_ux_prototyper_wizard_engine.py      # Compatibility tests
    ├── test_business_process_analyst_process_engine.py # Compatibility tests
    │
    ├── test_game_developer_cli.py               # CLI tests
    ├── test_robotics_engineer_cli.py            # CLI tests
    ├── test_ux_prototyper_cli.py                # CLI tests
    ├── test_business_process_analyst_cli.py     # CLI tests
    │
    ├── test_game_developer_run_tests.py         # Specific tests
    └── test_ux_prototyper_simulate_invalid_transition.py # Specific tests
```

## Implementation Strategy

### Core StateMachine Implementation

1. Create a robust, flexible core `StateMachine` class that supports:
   - State definitions and transitions
   - Event triggering and state transitions
   - Guard functions with composition (AND, OR, NOT)
   - Entry/exit hooks for states
   - Global hooks for transition events
   - History tracking and undo/redo
   - Serialization to/from various formats
   - Visualization export
   - Simulation and testing utilities

2. Separate concerns into appropriate modules:
   - `core.py`: Basic state machine structure and transition logic
   - `guards.py`: Guard function composition and evaluation
   - `hooks.py`: Hook registration and invocation
   - `history.py`: History tracking, undo/redo functionality
   - `serialization.py`: Import/export to various formats
   - `visualization.py`: Graph representation and export
   - `simulation.py`: Sequence simulation and testing

### Domain-Specific Adapters

Create adapter layers that maintain backward compatibility:

1. `game_dev.py`: Expose the standard `StateMachine` class with the same API
2. `robotics.py`: Provide a global state instance with procedural functions
3. `ux.py`: Implement `WizardEngine` using the core stateMachine
4. `business.py`: Provide process-oriented procedural interface

### CLI Tools

Maintain CLI tools for each domain that use the unified core:

1. Game Developer: Scaffold and visualization tools
2. Robotics Engineer: Command-line interface with YAML support
3. UX Prototyper: Wizard session management
4. Business Process Analyst: Process state management

## Migration Plan

1. Implement the core `StateMachine` class with all required functionality
2. Create the adapter layers for each domain with backward-compatible APIs
3. Update CLI tools to use the unified core through adapters
4. Ensure all existing tests pass with the refactored implementation
5. Add new tests for the core functionality

## Benefits

1. Reduces code duplication across implementations
2. Provides consistent behavior across all domain-specific interfaces
3. Makes it easier to maintain and enhance the core functionality
4. Preserves domain-specific terminology and interfaces for users
5. Improves testability with a unified core implementation