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
├── __init__.py            # Package initialization
├── README.md              # Package documentation
├── core/
│   ├── __init__.py
│   ├── models.py          # Shared data models
│   ├── interfaces.py      # Abstract interfaces
│   ├── utils.py           # Common utilities
│   └── exceptions.py      # Custom exceptions
├── dependency_tracking/
│   ├── __init__.py
│   ├── graph.py           # Dependency graph
│   ├── tracker.py         # Dependency tracking
│   └── workflow.py        # Workflow management
├── failure_resilience/
│   ├── __init__.py
│   ├── checkpoint.py      # Checkpoint management
│   ├── detector.py        # Failure detection
│   └── recovery.py        # Recovery mechanism
├── job_management/
│   ├── __init__.py
│   ├── queue.py           # Job queue management
│   ├── scheduler.py       # Common scheduling logic
│   └── prioritization.py  # Priority management
└── resource_management/
    ├── __init__.py
    ├── allocator.py       # Resource allocation
    ├── forecaster.py      # Resource forecasting
    └── partitioner.py     # Resource partitioning
```

### Base Model Hierarchy

```
BaseModel (Pydantic)
  ├── BaseJob
  │    ├── RenderJob        # render_farm_manager
  │    ├── Simulation       # concurrent_task_scheduler
  │    └── SimulationStage  # concurrent_task_scheduler
  ├── BaseNode
  │    ├── RenderNode       # render_farm_manager
  │    └── ComputeNode      # concurrent_task_scheduler
  ├── Dependency
  │    ├── JobDependency
  │    └── StageDependency
  ├── Resource
  │    ├── ComputeResource
  │    └── StorageResource
  ├── Checkpoint
  │    ├── RenderCheckpoint  # render_farm_manager
  │    └── SimulationCheckpoint  # concurrent_task_scheduler
  ├── Result (Generic[T])    # Generic result wrapper with success/error
  ├── TimeRange              # Common time range utility
  └── AuditLogEntry          # Common audit logging model
```

### Interface Hierarchy

```
Interface (ABC)
  ├── SchedulerInterface
  │    ├── DeadlineSchedulerInterface  # render_farm_manager
  │    └── SimulationSchedulerInterface  # concurrent_task_scheduler
  ├── ResourceManagerInterface
  │    ├── ResourcePartitionerInterface  # render_farm_manager
  │    └── ResourceForecastingInterface  # concurrent_task_scheduler
  ├── DependencyTrackerInterface
  │    ├── RenderDependencyInterface  # render_farm_manager
  │    └── SimulationDependencyInterface  # concurrent_task_scheduler
  ├── CheckpointManagerInterface
  │    ├── RenderCheckpointInterface  # render_farm_manager
  │    └── SimulationCheckpointInterface  # concurrent_task_scheduler
  └── AuditLogInterface
       ├── RenderAuditInterface  # render_farm_manager
       └── SimulationAuditInterface  # concurrent_task_scheduler
```

### Key Enums

```
# Status Enums
JobStatus: PENDING, QUEUED, RUNNING, PAUSED, COMPLETED, FAILED, CANCELLED
NodeStatus: ONLINE, OFFLINE, MAINTENANCE, ERROR, STARTING, STOPPING

# Priority Enums
Priority: LOW, MEDIUM, HIGH, CRITICAL

# Resource Types
ResourceType: CPU, GPU, MEMORY, STORAGE, NETWORK, SPECIALIZED

# Dependency Types
DependencyType: SEQUENTIAL, DATA, RESOURCE, CONDITIONAL, TEMPORAL

# Dependency States
DependencyState: PENDING, SATISFIED, FAILED, BYPASSED

# Checkpoint Types
CheckpointType: FULL, INCREMENTAL, DELTA, METADATA

# Log Levels
LogLevel: DEBUG, INFO, WARNING, ERROR, CRITICAL
```

## Component Analysis and Migration

### 1. Core Models and Utilities

| Common Component | render_farm_manager | concurrent_task_scheduler | Migration Approach |
|------------------|---------------------|---------------------------|-------------------|
| BaseJob | RenderJob | Simulation, SimulationStage | Extract common properties into BaseJob, have RenderJob and Simulation extend it |
| BaseNode | RenderNode | ComputeNode | Extract common properties into BaseNode, have RenderNode and ComputeNode extend it |
| Result | Used in various places | Used in various places | Define generic Result class in common.core.models |
| TimeRange | Used for scheduling | Used for scheduling | Define common TimeRange in common.core.utils |
| DateTimeEncoder | Used for serialization | Used for serialization | Move to common.core.utils |
| generate_id | Used for ID generation | Used for ID generation | Move to common.core.utils |

### 2. Dependency Tracking

| Common Component | render_farm_manager | concurrent_task_scheduler | Migration Approach |
|------------------|---------------------|---------------------------|-------------------|
| DependencyGraph | Internal dependency tracking | DependencyGraph in graph.py | Extract common graph functionality to common.dependency_tracking.graph |
| DependencyTracker | JobDependencyManager | DependencyTracker | Create common interface in common.dependency_tracking.tracker |
| DependencyType | Used for dependency types | Used for dependency types | Define common enum in common.core.models |
| DependencyState | Used for tracking state | Used for tracking state | Define common enum in common.core.models |

### 3. Resource Management

| Common Component | render_farm_manager | concurrent_task_scheduler | Migration Approach |
|------------------|---------------------|---------------------------|-------------------|
| ResourceManager | ResourcePartitioner | ResourceManager | Extract common functionality to common.resource_management.allocator |
| ResourceForecaster | Not directly implemented | ResourceForecaster | Create common interface in common.resource_management.forecaster |
| ResourceAllocation | Used for resource tracking | Used for resource tracking | Define common model in common.core.models |
| ResourceRequirement | Used in job definitions | Used in simulation definitions | Define common model in common.core.models |

### 4. Failure Resilience

| Common Component | render_farm_manager | concurrent_task_scheduler | Migration Approach |
|------------------|---------------------|---------------------------|-------------------|
| CheckpointManager | Limited checkpointing | CheckpointManager | Extract common functionality to common.failure_resilience.checkpoint |
| FailureDetector | Error handling in RenderFarmManager | FailureDetector | Create common interface in common.failure_resilience.detector |
| ResilienceCoordinator | Not directly implemented | ResilienceCoordinator | Create common interface in common.failure_resilience.recovery |
| CheckpointType | Used for checkpoint types | Used for checkpoint types | Define common enum in common.core.models |

### 5. Job Management

| Common Component | render_farm_manager | concurrent_task_scheduler | Migration Approach | Status |
|------------------|---------------------|---------------------------|-------------------|--------|
| JobQueue | Embedded in DeadlineScheduler | JobQueue in queue.py | Extract common functionality to common.job_management.queue | ✅ Completed |
| JobScheduler | DeadlineScheduler | JobScheduler | Create common interface in common.job_management.scheduler | ✅ Completed |
| PriorityManager | Priority handling in DeadlineScheduler | Priority handling in queue.py | Extract common functionality to common.job_management.prioritization | ✅ Completed |
| QueuePolicy | Not explicitly defined | QueuePolicy enum | Move to common.job_management.queue | ✅ Completed |
| PreemptionPolicy | Basic preemption in DeadlineScheduler | PreemptionPolicy in queue.py | Extract common functionality to common.job_management.queue | ✅ Completed |

## Implementation Strategy

### Phase 1: Establish Core Models and Interfaces ✅ Completed

1. Create common models in `common/core/models.py` ✅ Completed
   - BaseJob, BaseNode, Resource models
   - Common enums for status, priority, etc.
   - Result and TimeRange utilities
   
2. Define interfaces in `common/core/interfaces.py` ✅ Completed
   - SchedulerInterface
   - ResourceManagerInterface
   - DependencyTrackerInterface
   - CheckpointManagerInterface
   
3. Implement shared utilities in `common/core/utils.py` ✅ Completed
   - DateTimeEncoder for serialization
   - generate_id function
   - Other common utilities
   
4. Define exceptions in `common/core/exceptions.py` ✅ Completed
   - TaskSchedulerError as base exception
   - ResourceError, DependencyError, etc.

### Phase 2: Implement Shared Components 🔄 In Progress

1. Implement dependency tracking functionality ✅ Completed
   - Graph-based dependency representation
   - Cycle detection algorithms
   - Dependency state tracking
   
2. Implement common resource management ✅ Completed
   - Resource allocation algorithms
   - Resource requirement matching
   - Resource usage tracking
   
3. Implement failure resilience components ✅ Completed
   - Checkpoint management
   - Failure detection
   - Recovery mechanisms
   
4. Implement job management components ✅ Completed
   - Job queue management
   - Priority-based scheduling
   - Deadline-aware scheduling

### Phase 3: Refactor Persona Implementations 🔄 In Progress

1. Modify `render_farm_manager` to use the common library 🔄 In Progress
   - Update imports to use common models
   - Extend common interfaces for render farm specific needs
   - Refactor implementations to leverage shared code
   - Ensure backward compatibility with existing tests

2. Modify `concurrent_task_scheduler` to use the common library ⏳ Pending
   - Update imports to use common models
   - Extend common interfaces for simulation specific needs
   - Refactor implementations to leverage shared code
   - Ensure backward compatibility with existing tests

### Phase 4: Testing and Verification ⏳ Pending

1. Ensure all tests pass for both implementations
   - Run unit tests for render_farm_manager
   - Run unit tests for concurrent_task_scheduler
   - Fix any integration issues
   
2. Verify that all functionality is preserved
   - Compare behavior before and after refactoring
   - Check for any performance regressions
   
3. Generate test report using pytest-json-report
   - Run comprehensive test suite
   - Generate report.json file
   - Verify all tests pass

## Migration Approach - Detailed Steps

### Common Core Package

1. Implement `common/core/models.py` ✅ Completed
   - Define all common models and enums
   - Ensure backward compatibility with existing code
   
2. Implement `common/core/interfaces.py` ✅ Completed
   - Define abstract interfaces with clear contracts
   - Include comprehensive docstrings
   
3. Implement `common/core/utils.py` and `common/core/exceptions.py` ✅ Completed
   - Extract common utilities and exceptions
   - Ensure function signatures match existing code

### Common Job Management Package

1. Implement `common/job_management/queue.py` ✅ Completed
   - Define common JobQueue class with priority queue implementation
   - Support multiple queue policies
   - Include comprehensive statistics tracking
   - Implement preemption policy management

2. Implement `common/job_management/scheduler.py` ✅ Completed
   - Create common scheduler interface implementation
   - Support deadline-driven scheduling
   - Implement priority inheritance
   - Include resource requirement matching

3. Implement `common/job_management/prioritization.py` ✅ Completed
   - Create priority management system
   - Support multiple priority policies
   - Implement deadline-based and fairness-based adjustments
   - Support priority inheritance between related jobs

### For render_farm_manager

1. Update imports to use common models and interfaces 🔄 In Progress
   - Replace `from render_farm_manager.core.models import X` with `from common.core.models import X`
   - Replace custom utilities with common versions

2. Extend base classes for render farm specific needs 🔄 In Progress
   - Make RenderJob extend BaseJob
   - Make RenderNode extend BaseNode
   
3. Adapt to use common interfaces 🔄 In Progress
   - Implement SchedulerInterface for DeadlineScheduler
   - Implement ResourceManagerInterface for ResourcePartitioner

### For concurrent_task_scheduler

1. Update imports to use common models and interfaces ⏳ Pending
   - Replace `from concurrent_task_scheduler.models import X` with `from common.core.models import X`
   - Replace custom utilities with common versions

2. Extend base classes for scientific computing specific needs ⏳ Pending
   - Make Simulation extend BaseJob
   - Make SimulationStage extend BaseJob
   
3. Adapt to use common interfaces ⏳ Pending
   - Implement DependencyTrackerInterface for dependency tracking
   - Implement CheckpointManagerInterface for checkpoint management

## Backward Compatibility Strategy

To ensure backward compatibility, we will:

1. Preserve all public APIs and method signatures
   - Keep all public methods with the same parameters and return types
   - Maintain backward compatibility with existing function calls

2. Add compatibility layers where needed
   - Create adapter classes if necessary
   - Add compatibility methods to handle legacy code

3. Use inheritance to extend common functionality
   - Base classes provide common functionality
   - Derived classes add domain-specific behavior

4. Ensure all original tests pass without modification
   - Run tests regularly during refactoring
   - Fix compatibility issues as they arise

## Extension Points

We'll design the common library with extension points for domain-specific functionality:

1. Hooks for custom scheduling algorithms
   - Allow custom priority calculations
   - Support pluggable scheduling strategies

2. Extension interfaces for specialized resource management
   - Allow custom resource allocation policies
   - Support specialized resource tracking

3. Pluggable strategies for dependency resolution
   - Support different dependency types
   - Allow custom dependency validation

4. Customizable checkpointing mechanisms
   - Support different checkpoint storage backends
   - Allow custom checkpoint frequency calculations

## Testing Strategy

1. Run unit tests for the common library
   - Verify base functionality works correctly
   - Test edge cases and error handling

2. Run unit tests for both persona implementations
   - Verify domain-specific behavior is preserved
   - Check for any regressions

3. Run integration tests to ensure all components work together
   - Test end-to-end workflows
   - Verify cross-component interactions

4. Verify that performance meets or exceeds original implementation
   - Measure execution time before and after
   - Check resource utilization

5. Generate comprehensive test report
   - Use pytest-json-report to create report.json
   - Verify all tests pass successfully