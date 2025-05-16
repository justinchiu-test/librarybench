# Unified Concurrent Task Scheduler Libraries

## Overview
This is a unified implementation of concurrent task scheduler functionality that supports multiple domain-specific implementations while sharing common functionality.

The library consists of:
- `common`: Shared functionality for all implementations
- `render_farm_manager`: Implementation for managing 3D rendering operations
- `concurrent_task_scheduler`: Implementation for managing scientific computing simulations

## Architecture
The project follows a modular architecture with the following components:

### Common Library
The `common` package provides shared functionality:

- **Core Models**: Shared data structures (`BaseJob`, `BaseNode`, etc.)
- **Interfaces**: Abstract interfaces that domain implementations extend
- **Dependency Tracking**: Functionality for managing job dependencies
- **Job Management**: Scheduling and queue management
- **Resource Management**: Resource allocation and forecasting
- **Failure Resilience**: Checkpointing and recovery

### Domain-Specific Implementations
Each domain has its own specialized implementation that extends the common library:

- **Render Farm Manager**: Focuses on deadline-driven scheduling, node specialization, progressive rendering, and energy optimization
- **Scientific Computing**: Focuses on long-running job management, simulation scenarios, resource forecasting, and dependency workflows

## Installation
Install the library in development mode:

```bash
pip install -e .
```

## Usage
You can import the common library or domain-specific packages:

```python
# Import common functionality
from common.core.models import BaseJob, BaseNode
from common.core.interfaces import SchedulerInterface

# Import domain-specific functionality
from render_farm_manager.core.models import RenderJob, RenderNode
from concurrent_task_scheduler.models import Simulation, SimulationStage
```

## Refactoring Example
Here's how a domain-specific class can be refactored to use the common library:

```python
# Before
from render_farm_manager.core.models import RenderJob
from render_farm_manager.core.interfaces import SchedulerInterface

# After
from common.core.models import BaseJob
from common.core.interfaces import SchedulerInterface
from render_farm_manager.core.models_refactored import RenderJob
```

## Testing
Tests are preserved for each domain implementation:

```bash
# Run all tests
pytest

# Run tests for a specific domain
pytest tests/render_farm_manager/
pytest tests/scientific_computing/

# Run tests for a specific component
pytest tests/render_farm_manager/unit/test_deadline_scheduler.py
```

Record test results:
```bash
pytest --json-report --json-report-file=report.json --continue-on-collection-errors
```

## Implementation Status
The refactoring is currently in progress:

- [x] Common core models and interfaces
- [x] Common dependency tracking framework
- [x] Common job management framework
- [x] Common resource management framework
- [x] Common failure resilience framework
- [x] Refactored render farm manager core models
- [x] Refactored scheduler implementation
- [ ] Migrate other render farm manager components
- [ ] Migrate scientific computing components