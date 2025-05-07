# Unified Workflow Orchestration System

This is a unified workflow orchestration system that addresses the requirements of three different roles: Data Engineer, Data Scientist, and Product Manager.

## Architecture Overview

The system is designed with a modular architecture that provides flexible, robust workflow orchestration capabilities. Here's a high-level overview of the main components:

### Core Components

1. **Task** (`task.py`): The fundamental unit of work. Tasks can have dependencies, timeouts, retries, and backoff strategies.

2. **TaskManager** (`task_manager.py`): Manages the lifecycle of tasks, including queuing, execution, and monitoring.

3. **Workflow** (`workflow/workflow.py`): A collection of related tasks with dependencies.

4. **WorkflowManager** (`workflow/workflow.py`): Manages workflows, including registration, scheduling, and execution.

5. **Scheduler** (`scheduler.py`): Handles time-based scheduling of tasks and workflows.

6. **Queue** (`queue.py`): Provides prioritized and FIFO queuing mechanisms.

7. **API** (`api.py`): REST API for interacting with the system.

8. **Authentication** (`auth.py`): Handles authentication and authorization.

9. **Logger** (`logger.py`): Configurable logging system.

10. **UI** (`ui/ui.py`): Command-line and web interfaces.

11. **Utils** (`utils.py`): Utility functions used across the system.

### How Requirements Are Addressed

#### Data Engineer Requirements

1. **retry_mechanism**: Implemented in `Task.run()` with configurable retry limits.
2. **documentation**: Comprehensive docstrings and README.
3. **backoff_strategy**: Exponential backoff implemented in `utils.py` and used in `Task.run()`.
4. **task_states**: Task states tracked in `Task` class (pending, running, success, failure, timeout, canceled).
5. **task_prioritization**: Priority queuing in `PriorityQueue` class.
6. **retry_policies**: Configurable max_retries and retry_delay_seconds in `Task`.
7. **user_interface**: Command-line and web interfaces in `ui/ui.py`.
8. **security**: Authentication and authorization in `auth.py`.
9. **time_based_scheduling**: Scheduling functionality in `scheduler.py`.
10. **dynamic_task_creation**: Support for creating tasks dynamically at runtime.

#### Data Scientist Requirements

1. **Documentation**: Comprehensive docstrings and README.
2. **Logging**: Configurable logging in `logger.py`.
3. **Task Timeout**: Timeout handling in `Task._execute_with_timeout()`.
4. **Time-Based Scheduling**: Scheduling in `scheduler.py`.
5. **Dependency Management**: Task dependencies managed in `Workflow` and `TaskManager`.
6. **Retry Policies**: Configurable in `Task`.
7. **API Integration**: REST API in `api.py`.
8. **Backoff Strategy**: Exponential backoff in `utils.py`.
9. **Task Queuing**: Queue implementations in `queue.py`.
10. **Workflow Versioning**: Version tracking in `Workflow`.

#### Product Manager Requirements

1. **cancel_task**: Task cancellation in `Task.cancel()` and `TaskManager.cancel_task()`.
2. **set_task_timeout**: Timeout configuration in `Task`.
3. **queue_tasks**: Task queuing in `TaskManager.queue_task()`.
4. **send_alerts**: Alert generation in `TaskManager._execute_task()`.
5. **schedule_tasks**: Scheduling in `TaskManager.schedule_task()` and `WorkflowManager.schedule_workflow()`.
6. **store_metadata**: Metadata tracking in `TaskManager._metadata`.
7. **retry_failed_tasks**: Retry mechanism in `Task.run()`.
8. **log_execution_details**: Execution logging in `Task.run()` and `TaskManager`.
9. **configure_retry_policies**: Retry configuration in `Task`.
10. **api_access**: REST API in `api.py`.

## Component Interactions

- **Task Execution**: Tasks are created and queued in the `TaskManager`, which uses a thread pool to execute them. Tasks with dependencies wait until their dependencies complete.

- **Workflow Execution**: Workflows contain multiple tasks with dependencies. The `WorkflowManager` executes tasks in dependency order.

- **Scheduling**: The `Scheduler` periodically triggers tasks or workflows based on configured intervals.

- **API Integration**: The REST API provides endpoints for managing tasks and workflows, integrating with external systems.

- **Authentication**: API requests and UI actions are authenticated using tokens and authorized based on user roles.

## Key Features

1. **Robust Task Execution**: Tasks have configurable retries, timeouts, and backoff.

2. **Dependency Management**: Tasks can depend on other tasks, ensuring correct execution order.

3. **Priority-Based Scheduling**: Tasks can be prioritized for execution.

4. **Time-Based Scheduling**: Tasks and workflows can be scheduled to run at intervals.

5. **Dynamic Task Creation**: Tasks can create new tasks at runtime.

6. **Comprehensive Monitoring**: Task states, metadata, and execution details are tracked.

7. **Multiple Interfaces**: Command-line and web interfaces, plus a REST API.

8. **Secure Access**: Authentication and role-based authorization.

## Getting Started

To use the system:

1. Import the necessary components:

```python
from unified.task import Task
from unified.task_manager import TaskManager
from unified.workflow.workflow import Workflow, WorkflowManager
```

2. Create and execute tasks:

```python
# Create a task manager
task_manager = TaskManager()

# Queue a task
task_id = task_manager.queue_task(
    func=lambda: "Hello, World!",
    timeout=10,
    max_retries=3
)

# Get task metadata
metadata = task_manager.get_task_metadata(task_id)
```

3. Create and execute workflows:

```python
# Create a workflow manager
workflow_manager = WorkflowManager()

# Register a workflow
workflow_id = workflow_manager.register_workflow(
    name="My Workflow",
    description="Sample workflow"
)

# Add tasks to the workflow
task1 = Task(task_id="task1", func=lambda: "Step 1")
task2 = Task(task_id="task2", func=lambda: "Step 2", dependencies=["task1"])
workflow_manager.add_task_to_workflow(workflow_id, task1)
workflow_manager.add_task_to_workflow(workflow_id, task2)

# Run the workflow
result = workflow_manager.run_workflow(workflow_id)
```

4. Use the command-line interface:

```bash
python -m unified.ui.ui
```

5. Use the REST API:

```bash
# Start the API server
uvicorn unified.api:app --reload

# Create a workflow via API
curl -X POST "http://localhost:8000/workflows" \
     -H "X-API-Key: admin_secret_token_123" \
     -H "Content-Type: application/json" \
     -d '{"name": "API Workflow", "description": "Created via API"}'
```

## Conclusion

This unified workflow orchestration system provides a comprehensive solution for task and workflow management, addressing the diverse requirements of Data Engineers, Data Scientists, and Product Managers. Its modular design allows for flexibility, scalability, and ease of maintenance.