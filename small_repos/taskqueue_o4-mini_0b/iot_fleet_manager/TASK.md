# The Task

I am an IoT fleet manager coordinating firmware updates and telemetry processing across thousands of edge devices. I want to schedule staged rollouts, track success/failure rates, and recover from network interruptions seamlessly. This code repository delivers delayed scheduling, dead-letter handling, and observability for reliable fleet operations.

# The Requirements

* `EncryptionAtRest`       : Encrypt firmware binaries and telemetry logs stored on gateway disks.  
* `DelayedTaskScheduling`  : Roll out firmware in waves with defined ETAs per device group.  
* `BackupAndRestore`       : Snapshot queue state before mass-update campaigns and restore in case of rollback.  
* `GracefulShutdown`       : Let in-flight updates finish on devices before redeploying gateway workers.  
* `DeadLetterQueue`        : Isolate devices that repeatedly fail to update for manual investigation.  
* `MetricsIntegration`     : Emit per-device update latencies, success ratios, and retry counts to Prometheus.  
* `UniqueTaskID`           : Tag each update or telemetry task with a unique ID to avoid duplication.  
* `WebDashboard`           : Live dashboard showing device group health, rollout progress, and error breakdowns.  
* `AuditLogging`           : Immutable audit trail of each update command, retry, and cancellation event.  
* `CLIInterface`           : Enqueue new campaigns, view queue depth, replay failed updates, and tail logs from the CLI.  
