# Common Library for Concurrent Task Schedulers

This library provides common functionality for various concurrent task scheduler implementations.

## Components

### Core

- **Models**: Common data models for jobs, nodes, resources, etc.
- **Interfaces**: Abstract interfaces that define component contracts
- **Utilities**: Shared utility functions and classes
- **Exceptions**: Custom exception types for error handling

### Dependency Tracking

- **Graph**: Generic dependency graph implementation
- **Tracker**: Dependency tracking and management
- **Workflow**: Workflow management and orchestration

### Job Management

- **Queue**: Job queue with priority management
- **Scheduler**: Base scheduler implementation
- **Prioritization**: Job priority management

### Resource Management

- **Allocator**: Resource allocation algorithms
- **Forecaster**: Resource usage forecasting
- **Partitioner**: Resource partitioning for multi-tenant systems

### Failure Resilience

- **Checkpoint Manager**: Job state checkpointing
- **Failure Detector**: Detecting node and job failures
- **Resilience Coordinator**: Coordinating recovery from failures

## Usage

Import modules directly from their packages:

```python
# Import core models
from common.core.models import BaseJob, BaseNode, JobStatus, Priority

# Import interfaces
from common.core.interfaces import SchedulerInterface, ResourceManagerInterface

# Import utilities
from common.core.utils import generate_id, DateTimeEncoder
```

## Extension Points

The library is designed with extension points for domain-specific functionality:

1. **Model Extension**: Extend base models with domain-specific fields
   ```python
   from common.core.models import BaseJob
   
   class DomainJob(BaseJob):
       domain_specific_field: str = "default"
   ```

2. **Interface Implementation**: Implement interfaces with domain-specific logic
   ```python
   from common.core.interfaces import SchedulerInterface
   
   class DomainScheduler(SchedulerInterface):
       def schedule_jobs(self, jobs, nodes):
           # Domain-specific implementation
           pass
   ```

3. **Composition**: Use common components as building blocks
   ```python
   from common.job_management.queue import JobQueue
   from common.dependency_tracking.graph import DependencyGraph
   
   class DomainWorkflowManager:
       def __init__(self):
           self.job_queue = JobQueue()
           self.dependency_graph = DependencyGraph()
   ```