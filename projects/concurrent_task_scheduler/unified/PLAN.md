# Unified Library Refactoring Plan

## Overview

This document outlines the plan for creating a unified library (`common/`) that can be shared between the `render_farm_manager` and `concurrent_task_scheduler` packages while preserving their original functionality. After careful analysis of both implementations, we've identified common patterns, data structures, and functionality that can be extracted and shared.

## Shared Components

### 1. Common Models and Base Classes

From our analysis of both implementations, there's significant overlap in their model structures. We'll create common base models:

- **Status Enums**: The status values like `PENDING`, `RUNNING`, `COMPLETED` are shared between both implementations
- **Priority Enums**: Both systems have priority levels (LOW, MEDIUM, HIGH, CRITICAL)
- **Resource Types**: Both define similar resource types (CPU, GPU, MEMORY, etc.)
- **Base Models**: Common base models for jobs, nodes, and resources using Pydantic

### 2. Common Algorithms and Utilities

Both implementations share core algorithms for:

- **Dependency Tracking**: Graph-based dependency management
- **Scheduling Logic**: Priority and deadline-based scheduling
- **Checkpointing**: Mechanism for state persistence
- **Resource Management**: Allocation and optimization

### 3. Common Interfaces

We'll define common interfaces that each implementation can extend:

- **SchedulerInterface**: For job scheduling components
- **DependencyTrackingInterface**: For dependency management
- **ResourceManagerInterface**: For resource allocation and management
- **CheckpointManagerInterface**: For state persistence

## Architecture Design

### Common Package Structure

```
common/
├── core/
│   ├── __init__.py
│   ├── models.py          # Shared data models
│   ├── interfaces.py      # Abstract interfaces
│   ├── utils.py           # Common utilities
│   └── exceptions.py      # Custom exceptions
├── scheduling/
│   ├── __init__.py
│   ├── priority.py        # Priority management
│   └── scheduler.py       # Common scheduling logic
├── resource_management/
│   ├── __init__.py
│   ├── allocator.py       # Resource allocation
│   └── forecaster.py      # Resource forecasting
├── dependency_tracking/
│   ├── __init__.py
│   ├── graph.py           # Dependency graph
│   └── tracker.py         # Dependency tracking
└── failure_resilience/
    ├── __init__.py
    ├── checkpoint.py      # Checkpoint management
    └── resilience.py      # Failure detection/handling
```

### Base Model Hierarchy

```
BaseModel (Pydantic)
  ├── Resource
  │    ├── ComputeResource
  │    └── StorageResource
  ├── Job
  │    ├── RenderJob
  │    └── SimulationJob
  ├── Node
  │    ├── RenderNode
  │    └── ComputeNode
  ├── Dependency
  │    ├── JobDependency
  │    └── StageDependency
  └── Checkpoint
```

## Implementation Strategy

### Phase 1: Establish Core Models and Interfaces

1. Create common models in `common/core/models.py` 
2. Define interfaces in `common/core/interfaces.py`
3. Implement shared utilities in `common/core/utils.py`

### Phase 2: Implement Shared Components

1. Implement dependency tracking functionality
2. Implement scheduling base classes
3. Implement resource management and forecasting
4. Implement checkpointing and failure resilience

### Phase 3: Refactor Persona Implementations

1. Modify `render_farm_manager` to use the common library
   - Update imports to use common models
   - Extend common interfaces for specific render farm needs
   - Refactor implementations to leverage shared code

2. Modify `concurrent_task_scheduler` to use the common library
   - Update imports to use common models
   - Extend common interfaces for simulation-specific needs
   - Refactor implementations to leverage shared code

### Phase 4: Testing and Verification

1. Ensure all tests pass for both implementations
2. Verify that all functionality is preserved
3. Run performance tests to ensure no regressions

## Migration Approach

### For Both Implementations

1. Start with updating the imports to use common models and interfaces
2. Replace core data structures with common implementations
3. Adapt specific algorithms to extend common base classes

### For render_farm_manager

1. Adapt `RenderJob`, `RenderNode` to extend common base classes
2. Refactor resource partitioning to use common resource management
3. Refactor deadline scheduling to use common scheduling
4. Migrate node specialization to common framework
5. Adapt energy optimization to use common utilities

### For concurrent_task_scheduler

1. Adapt `Simulation`, `SimulationStage` to extend common base classes
2. Refactor dependency tracking to use common graph implementation
3. Migrate failure resilience to common checkpointing
4. Update resource forecasting to use common framework
5. Adapt scenario management to common priority management

## Backward Compatibility

To ensure backward compatibility, we will:

1. Preserve all original APIs and method signatures
2. Add compatibility layers where needed
3. Use inheritance to extend common functionality without breaking existing code
4. Ensure all original tests pass without modification

## Extension Points

We'll design the common library with extension points for domain-specific functionality:

1. Hooks for custom scheduling algorithms
2. Extension interfaces for specialized resource management
3. Pluggable strategies for dependency resolution
4. Customizable checkpointing mechanisms

## Testing Strategy

1. Run unit tests for the common library
2. Run unit tests for both persona implementations
3. Run integration tests to ensure all components work together
4. Verify that performance meets or exceeds original implementation

## Timeline and Tasks

1. **Phase 1**: Core Models and Interfaces
   - Create base models for jobs, nodes, resources
   - Define common interfaces for all components
   - Implement shared utilities and helpers

2. **Phase 2**: Implement Shared Components
   - Create dependency tracking implementations
   - Implement scheduler base classes
   - Build resource management framework
   - Create checkpoint management system

3. **Phase 3**: Migrate Persona Implementations
   - Update render_farm_manager imports and models
   - Update concurrent_task_scheduler imports and models
   - Refactor both implementations to use common components

4. **Phase 4**: Testing and Documentation
   - Run all tests to validate functionality
   - Fix any issues that arise
   - Generate final test report
   - Complete documentation of unified library