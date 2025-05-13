# The Task

I am a DevOps engineer responsible for a mission-critical microservices platform. I want to be able to safely enqueue, monitor, and recover asynchronous jobs across multiple clusters and data centers without risking data leakage or downtime. This code repository provides robust task-queuing primitives, observability, security, and disaster-recovery features to keep everything running smoothly.

# The Requirements

* `EncryptionAtRest`       : Encrypt persisted logs and snapshots so sensitive payloads remain secure on disk.  
* `DelayedTaskScheduling`  : Allow tasks to be enqueued with an ETA or delay so they run at a specified future time.  
* `BackupAndRestore`       : Provide tools to snapshot state and restore from backups in disaster-recovery scenarios.  
* `GracefulShutdown`       : Drain the queue and finish in-flight tasks before shutting down workers cleanly.  
* `DeadLetterQueue`        : Automatically move permanently failing tasks into a DLQ for later inspection and reprocessing.  
* `MetricsIntegration`     : Emit Prometheus/Grafana-compatible metrics on throughput, latencies, retries and failure rates.  
* `UniqueTaskID`           : Assign and enforce globally unique IDs for each task to prevent duplication and enable idempotent retries.  
* `WebDashboard`           : Real-time UI to monitor queues, visualize task statuses, drill into failures, and replay tasks.  
* `AuditLogging`           : Maintain an immutable audit trail of all enqueue, dequeue, retry, and cancellation events for compliance.  
* `CLIInterface`           : Provide command-line tools for enqueuing tasks, viewing queue stats, canceling jobs, and tailing logs.  
