# The Task

I am a DevOps Engineer managing critical infrastructure automation. I want to be able to reliably schedule and monitor operational jobs—like backups, log rotations, and cluster maintenance—while gracefully handling shutdowns, failures, and resource spikes. This code repository provides a lightweight, extensible scheduler that meets all my requirements.

# The Requirements

* `graceful_shutdown` : On SIGINT or SIGTERM, finish running jobs, persist state, and forcibly stop after a configurable timeout.
* `health_check` : Expose a simple HTTP endpoint (or CLI command) for liveness and readiness probes to integrate with Kubernetes or load balancers.
* `trigger_job` : Manually invoke any registered job on demand—useful for emergency remediation tasks.
* `schedule_job` : Define delays and intervals in seconds, minutes, or cron‐style expressions for precise scheduling.
* `set_persistence_backend` : Swap out the default shelve backend for Redis, SQLite, or a custom implementation via a pluggable persistence interface.
* `timezone_aware` : Schedule jobs in specific timezones and correctly handle daylight‐saving transitions for global clusters.
* `exponential_backoff` : Automatically retry failed operations—like API calls or database migrations—using exponential or custom backoff strategies.
* `define_dependencies` : Configure DAG relationships so that database schema migrations run before backups, and backups before notification jobs.
* `retry_job` : Set retry policies with retry count, fixed or backoff delays, and failure thresholds per job.
* `limit_resources` : Impose max concurrent CPU or I/O jobs, apply memory limits, or use custom semaphore controls to prevent resource contention.
