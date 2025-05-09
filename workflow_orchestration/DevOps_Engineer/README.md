# Workflow Scheduler

A Python-based workflow scheduler for automating task execution with dependency management,
retry policies, backoff strategies, logging, and versioned workflows.

## Features

- **Documentation**: This README and docstrings in code.
- **Logging**: Execution details (start, end, outcome) are recorded via the `logging` module.
- **Task Timeout**: Tasks can specify a maximum runtime (`timeout` in seconds).
- **Time-Based Scheduling**: Workflows run on intervals (hourly, daily, etc.).
- **Dependency Management**: Tasks declare dependencies; execution order is topologically sorted.
- **Retry Policies**: Configure `max_retries` and `retry_delay_seconds` per task.
- **Exponential Backoff**: Retry delays grow exponentially on each attempt.
- **Task Queuing**: An in-memory `asyncio.Queue` with worker coroutines.
- **Workflow Versioning**: Maintain multiple versions; roll back to earlier versions.
- **API Integration**: FastAPI-based HTTP API for external triggers and management.

## Installation

