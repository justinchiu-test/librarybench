# Workflow Orchestration

A lightweight workflow orchestration system for defining and executing task pipelines with dependencies, similar to a simple DAG runner.

## Features

- Define tasks with dependencies
- Execute tasks in the correct order respecting dependencies
- Track task states (pending, running, success, failure, retrying)
- Support for task retries with configurable parameters
- Failure propagation to dependent tasks
- Parallel execution of independent tasks
- Task timeout handling

## Usage

```python
from workflow import Task, Workflow

# Create a workflow
workflow = Workflow()

# Define tasks
task1 = Task(
    name="task1",
    func=lambda: "result1"
)

# Task with dependency
def task2_func():
    # Access result from task1
    result1 = workflow.get_task_result("task1")
    return f"processed {result1}"

task2 = Task(
    name="task2",
    func=task2_func,
    dependencies=["task1"]
)

# Task with retry configuration
def flaky_task():
    # This might fail sometimes
    return "result3"

task3 = Task(
    name="flaky_task",
    func=flaky_task,
    max_retries=3,
    retry_delay=1.0,
    timeout=5.0  # 5 second timeout
)

# Add tasks to workflow
workflow.add_task(task1)
workflow.add_task(task2)
workflow.add_task(task3)

# Run the workflow
results = workflow.run()
```

## Core Components

### Task

Represents a single unit of work with:

- Name and function to execute
- Dependencies on other tasks
- State tracking (pending, running, success, failure, retrying)
- Retry configuration
- Timeout handling

### Workflow

Manages a collection of tasks:

- Validates the DAG for cycles and missing dependencies
- Determines execution order using topological sorting
- Executes tasks respecting dependencies
- Handles parallel execution of independent tasks
- Tracks results and propagates failures

## Running the Example

The repository includes an example workflow to demonstrate usage:

```
python example.py
```

## Tests

Run the test suite to verify functionality:

```
pytest tests.py
```