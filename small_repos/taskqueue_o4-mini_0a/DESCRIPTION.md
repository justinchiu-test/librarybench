# TaskQueue

## Purpose and Motivation
TaskQueue is a file-persisted, forecastable job scheduler and queue manager. It supports enqueuing tasks with priorities, schedules, and retry policies, all backed by the filesystem. Developers get reliable task execution without requiring Redis, RabbitMQ, or Celery—just Python’s standard library. Ideal for lightweight background processing, cron replacement, or dependency-aware workflows.

## Core Functionality
- Enqueue and dequeue tasks with metadata: priority, ETA/delay, unique ID  
- File-based persistence (append-only log or JSON snapshots) ensuring recovery after crashes  
- Retry policies (fixed, exponential backoff) and configurable failure hooks  
- Task chaining and dependency declarations so jobs wait for predecessor completions  
- Scheduler that supports one‐off and recurring (cron-like) tasks  
- Pluggable execution backends (threaded vs. single‐thread) and health monitoring  

