# task_scheduler

## Purpose and Motivation
A lightweight, in-process job scheduler that runs Python callables at fixed intervals, specific times of day, or cron-style schedules, all implemented using `threading` and `datetime`. It provides an easy way to build periodic workers, maintenance tasks, or reminder systems without external dependencies.  
Practical applications include cleanup jobs, report generators, and time-based cache invalidation.  
Extension points: custom schedule parsers, asynchronous task execution, persistent job storage.

## Core Functionality
- Schedule tasks using interval (every N seconds), daily at specific time(s), or simplified cron expressions  
- Add, remove, and list tasks at runtime, with human-readable metadata  
- Thread-based execution with optional locking to prevent overlapping runs  
- Graceful shutdown procedure to wait for running jobs or cancel them  
- Retry logic and error handlers for failed jobs  
- Query interface for next run times and job statistics

