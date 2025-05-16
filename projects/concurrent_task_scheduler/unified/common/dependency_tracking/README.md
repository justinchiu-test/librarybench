# Dependency Tracking System

This module provides a unified dependency tracking system that can be used by both the render farm manager and scientific computing implementations. It includes components for tracking dependencies between jobs/stages, managing workflows, and handling transitions between job states.

## Components

### DependencyGraph

The `DependencyGraph` class represents a directed acyclic graph (DAG) of dependencies between jobs or stages. It provides methods for:

- Adding and removing dependencies
- Checking if dependencies are satisfied
- Finding jobs/stages that are ready to execute
- Getting critical paths through the graph
- Serializing and deserializing the graph

### DependencyTracker

The `DependencyTracker` class manages multiple dependency graphs and provides higher-level functionality for:

- Creating and managing dependency graphs
- Registering dependencies between jobs/stages
- Checking if dependencies are satisfied
- Updating job/stage statuses and propagating changes
- Determining when jobs/stages are ready to run
- Finding critical paths and blocking jobs
- Generating execution plans

### WorkflowManager

The `WorkflowManager` class provides a workflow-based approach to dependency management, with support for:

- Creating and managing workflow templates
- Creating workflow instances from templates
- Creating linear and parallel workflows
- Getting the next jobs/stages to execute
- Updating job/stage statuses
- Getting workflow status

## Usage Examples

### Basic Dependency Tracking

```python
from common.core.models import BaseJob, JobStatus
from common.dependency_tracking.tracker import DependencyTracker

# Create a dependency tracker
tracker = DependencyTracker()

# Create a dependency graph
tracker.create_graph("owner-1")

# Register dependencies
tracker.register_dependency("job-1", "job-2")  # job-2 depends on job-1
tracker.register_dependency("job-2", "job-3")  # job-3 depends on job-2

# Check if a job is ready to run
ready = tracker.is_ready_to_run("owner-1", "job-1", set())  # True - job-1 has no dependencies
ready = tracker.is_ready_to_run("owner-1", "job-2", set())  # False - job-2 depends on job-1

# Update job status
tracker.update_status("owner-1", "job-1", JobStatus.COMPLETED)

# Check again
ready = tracker.is_ready_to_run("owner-1", "job-2", {"job-1"})  # True - job-1 is completed
```

### Workflow Management

```python
from common.core.models import BaseJob, JobStatus, Priority
from common.dependency_tracking.workflow import WorkflowManager

# Create jobs
jobs = {
    "job-1": BaseJob(id="job-1", name="Stage 1", status=JobStatus.PENDING, priority=Priority.MEDIUM),
    "job-2": BaseJob(id="job-2", name="Stage 2", status=JobStatus.PENDING, priority=Priority.MEDIUM),
    "job-3": BaseJob(id="job-3", name="Stage 3", status=JobStatus.PENDING, priority=Priority.MEDIUM),
}

# Create workflow manager
manager = WorkflowManager()

# Create a linear workflow
result = manager.create_linear_workflow(
    owner_id="owner-1",
    stage_names=["Stage 1", "Stage 2", "Stage 3"],
    jobs=jobs,
)

# Get workflow instance
instance = result.value

# Get next jobs to execute
next_jobs = manager.get_next_jobs(instance.id, jobs).value

# Update job status
for job_id in next_jobs:
    manager.update_job_status(instance.id, job_id, JobStatus.RUNNING, jobs)
    # ... execute job ...
    manager.update_job_status(instance.id, job_id, JobStatus.COMPLETED, jobs)

# Get workflow status
status = manager.get_workflow_status(instance.id).value
```

## Extension Points

The dependency tracking system is designed to be extensible:

- You can subclass `DependencyGraph` to add domain-specific graph operations
- You can subclass `DependencyTracker` to add domain-specific tracking functionality
- You can create custom workflow templates by subclassing `WorkflowTemplate`
- You can extend the workflow system with custom node and transition types

## Integration with Domain-Specific Components

To integrate with domain-specific components:

1. Use the common interfaces from `common.core.interfaces`
2. Pass domain-specific jobs and stages to the tracker and workflow manager
3. Implement domain-specific factory functions for creating jobs/stages
4. Extend the system with domain-specific workflow templates if needed