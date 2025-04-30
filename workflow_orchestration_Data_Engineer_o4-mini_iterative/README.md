# Data Pipeline Manager

This repository provides a simple framework to define, schedule, and monitor data processing tasks with:

- **Retry Mechanism**: Configurable retries with exponential backoff.
- **Task States**: Track each task's state (`PENDING`, `RUNNING`, `SUCCESS`, `FAILURE`).
- **Task Prioritization**: Higher-priority tasks execute before lower-priority ones.
- **Time-based Scheduling**: Schedule tasks to run at specific times.
- **Dynamic Task Creation**: Tasks can spawn additional tasks at runtime.
- **Authentication & Authorization**: Secure access via roles.
- **Command-line Interface**: Manage and run tasks from the CLI.

Usage and detailed API documentation are provided in the source modules.

