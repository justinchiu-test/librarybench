# TaskScheduler

## Purpose and Motivation
TaskScheduler is a cron-style, in-process job scheduling library for Python scripts and applications. It provides easy task registration, recurring or one-off scheduling, and error-resilience out of the box. You get the power of sched or threading without boilerplate, suitable for background jobs, maintenance tasks, or timed cleanup routines.

## Core Functionality
- Schedule functions at fixed intervals (seconds, minutes, hours, cron-like spec).
- One-off delayed job execution with cancelation support.
- Persistent job store abstraction (in-memory by default, hook for file-based dump).
- Retry logic with exponential backoff and custom retry policies.
- Hooks for pre- and post-execution observers (logging, metrics).
- Query and introspection API to list, pause, resume, or remove scheduled tasks.

