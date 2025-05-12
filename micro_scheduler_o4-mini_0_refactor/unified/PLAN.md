# Unified Scheduler Implementation Plan

## Overview

This plan outlines a unified scheduler implementation that will satisfy all requirements from the various scheduler implementations examined in the test files. The implementation will provide a flexible, extensible job scheduling system with support for various persistence backends, dependency management, hooks, metrics exposure, and more.

## Component Breakdown

### 1. Core Scheduler
- Central job management and execution
- Support for synchronous and asynchronous jobs
- Job scheduling with various timing mechanisms (interval, cron, one-time, etc.)
- Leader election coordination for distributed environments
- Graceful shutdown capabilities
- Health monitoring

### 2. Job Management
- Job representation with metadata (id, name, status, run count, etc.)
- Job triggering and execution
- Job dependency management
- Resource limiting
- Priority ordering
- Job tagging system
- Tenant/namespace isolation

### 3. Persistence Layer
- Abstract backend interface
- Multiple backend implementations:
  - SQLite backend
  - Redis backend
  - File-based backends (JSON, Pickle)
  - In-memory backend
  - Shelve backend
- Job state persistence and recovery

### 4. Time Management
- Timezone-aware scheduling
- Various timing mechanisms:
  - Fixed interval execution
  - Cron-style scheduling
  - One-time scheduled execution
  - Manual triggering

### 5. Event System
- Pre/post execution hooks
- Failure handling hooks
- Customizable event handlers

### 6. Retry and Backoff
- Retry strategies
- Customizable backoff algorithms
- Exponential backoff decorator

### 7. Metrics and Monitoring
- Metrics collection
- Metrics exposure
- Logging integration
- HTTP health endpoint

## File Structure

```
unified/
├── __init__.py
├── setup.py
├── src/
│   ├── __init__.py
│   ├── scheduler/
│   │   ├── __init__.py
│   │   ├── scheduler.py      # Core scheduler implementation
│   │   ├── job.py            # Job representation and management
│   │   ├── persistence/      # Persistence backends
│   │   │   ├── __init__.py
│   │   │   ├── base.py       # Abstract persistence interface
│   │   │   ├── sqlite.py     # SQLite implementation
│   │   │   ├── redis.py      # Redis implementation
│   │   │   ├── file.py       # File-based implementations
│   │   │   └── memory.py     # In-memory implementation
│   │   ├── time/
│   │   │   ├── __init__.py
│   │   │   ├── cron.py       # Cron scheduling utilities
│   │   │   └── timezone.py   # Timezone management
│   │   ├── events/
│   │   │   ├── __init__.py
│   │   │   ├── hooks.py      # Hook registration and execution
│   │   │   └── handlers.py   # Default event handlers
│   │   ├── retry/
│   │   │   ├── __init__.py
│   │   │   ├── backoff.py    # Backoff strategies
│   │   │   └── decorator.py  # Retry decorators
│   │   └── metrics/
│   │       ├── __init__.py
│   │       ├── collector.py  # Metrics collection
│   │       └── reporter.py   # Metrics reporting
│   └── utils/
│       ├── __init__.py
│       ├── lock.py           # Locking utilities
│       ├── serialization.py  # Serialization helpers
│       └── threading.py      # Threading utilities
├── tests/
│   ├── __init__.py
│   └── [test files]
```

## Implementation Strategy

1. **Core Interface Abstraction**: Define a unified API that satisfies all test cases while being internally consistent and extensible.

2. **Modular Design**: Implement components as separate modules but with clear interfaces between them.

3. **Pluggable Components**: Support for different backends, hooks, and strategies through a pluggable architecture.

4. **Compatibility Layer**: Ensure the implementation passes all existing tests with minimal test modifications.

5. **Default Behaviors**: Provide sensible defaults that work out of the box for common use cases.

## Dependency Management Strategy

1. **External Dependencies**:
   - Minimize external dependencies to essential libraries only
   - Support for Redis (optional)
   - Support for SQLite (via standard library)
   - Date/time handling (via standard library and optional pytz/dateutil)
   - Async support (asyncio from standard library)

2. **Internal Dependencies**:
   - Use dependency injection to allow customization of components
   - Clear separation between modules to prevent circular dependencies
   - Define interfaces for all major components to allow alternate implementations

## Key Classes and Interfaces

1. **Scheduler**
   - Main scheduler class with unified interface
   - Factory methods for creating jobs and configuring the scheduler

2. **Job**
   - Represents a scheduled task with its metadata
   - Methods for job execution, status tracking

3. **PersistenceBackend**
   - Abstract interface for job persistence
   - Multiple implementations (SQLite, Redis, File, Memory)

4. **TimeProvider**
   - Handles timezone conversions
   - Calculates next run times for different scheduling patterns

5. **Hook System**
   - Manages event hooks and callbacks
   - Pre-execution, post-execution, and failure hooks

6. **BackoffStrategy**
   - Interface for defining retry behavior
   - Implementations for fixed, linear, and exponential backoff

7. **MetricsCollector**
   - Collects job execution metrics
   - Exposes metrics in Prometheus format

## Compatibility Notes

The unified implementation will be a completely new codebase, not referencing any existing implementations. The test files will be updated to import from the new unified implementation paths.

This design ensures that all requirements from the various implementations are satisfied while providing a clean, consistent, and maintainable architecture.