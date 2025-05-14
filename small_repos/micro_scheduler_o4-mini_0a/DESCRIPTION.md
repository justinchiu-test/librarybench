# micro_scheduler

## Purpose and Motivation
micro_scheduler is a lightweight task scheduler that runs delayed or periodic Python functions using only the standard library. It helps applications coordinate background jobs—such as cleanup routines, heartbeat pings, or polling tasks—without pulling in heavyweight frameworks. Designed for easy embedding in scripts, services, or CLI tools, it exposes a concise API for job registration, lifecycle control, and graceful shutdown.

## Core Functionality
- Register one‐off and recurring jobs with custom delay or interval parameters  
- Start, pause, resume, and stop the scheduler loop cleanly  
- Optional job persistence to disk (e.g., via `shelve` or `pickle`) for restart recovery  
- Job metadata querying and manual trigger capability  
- Error handling hooks and logging integration  
- Configurable concurrency model using threads or sequential execution  

