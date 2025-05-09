# Data Pipeline Task Management System

This repository provides a lightweight task and workflow management system suitable for data processing pipelines. It supports:

- **Task Definition**: Define tasks with custom functions, timeouts, retries, and backoff strategies.
- **Dependency Management**: Specify task dependencies to enforce execution order.
- **Logging**: Detailed logging of task execution, including start time, end time, retries, and errors.
- **Task Timeout**: Prevent tasks from running indefinitely by enforcing a maximum execution time.
- **Retry Policies**: Configure maximum retries and retry delays with exponential backoff.
- **Scheduling**: Schedule workflows to run at fixed intervals.
- **Queuing**: In-memory FIFO task queue.
- **Workflow Versioning**: Automatic version increment on workflow updates.
- **API Integration**: Flask-based REST API for workflow and task management.

## Installation

1. Clone the repository:
   