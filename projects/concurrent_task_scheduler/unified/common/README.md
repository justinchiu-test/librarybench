# Common Package

This package contains functionality shared across all the persona-specific packages.
It provides a unified library for concurrent task scheduling that can be used by
both the render farm manager and scientific computing implementations.

## Structure:

### Core Components
- `core/models.py`: Common base models and data structures
- `core/interfaces.py`: Abstract interfaces for key components
- `core/utils.py`: Utility functions shared across implementations
- `core/exceptions.py`: Custom exception types

### Upcoming Components
- `scheduling/`: Common scheduling algorithms
- `resource_management/`: Resource allocation and management
- `dependency_tracking/`: Dependency graph and tracking
- `failure_resilience/`: Checkpointing and failure handling

## Usage

Import common components in persona-specific code:

```python
# Import common models
from common.core.models import BaseJob, BaseNode, ResourceType, JobStatus

# Import interfaces
from common.core.interfaces import SchedulerInterface, ResourceManagerInterface

# Import utilities
from common.core.utils import generate_id, weighted_average
```

## Design Philosophy

The common library follows these design principles:

1. **Interface-Based Design**: Key components are defined as abstract interfaces
2. **Extensibility**: Base classes are designed to be extended by specific implementations
3. **Minimal Dependencies**: The library minimizes external dependencies
4. **API Compatibility**: Preserves backward compatibility with existing code
5. **Performance-Optimized**: Core algorithms are optimized for performance