# SchedualPy

## Purpose and Motivation
SchedualPy is a lightweight scheduling library to run Python callables at defined intervals or specific times, akin to cron but embedable in any application. It uses only the standard threading and time modules, offering flexible task registration and execution control without external schedulers or dependencies. This is ideal for background jobs, periodic health checks, or timed data fetches.

## Core Functionality
- Register one-off or recurring tasks using interval (seconds, minutes, hours) or cron-like expressions  
- Start, pause, resume, and cancel individual or grouped tasks at runtime  
- Thread-safe internal scheduler loop with optional concurrency limits  
- Task result logging and basic retry/backoff strategies  
- Support for synchronous and asynchronous-style (via callbacks) task invocation  
- Hooks for pre-/post-execution handlers and custom error recovery  

